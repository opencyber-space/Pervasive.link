import uuid
import logging
from typing import Dict, Any, Optional

from .threads_manager import DSLThreadsManagerMP
from .addons import AddonsManager, DSLCallback
from .addons_pool import InferenceService
from .workflow_state import WorkflowPersistence
from .output_collector import OutputCollector  
from .human_intervention_system import SessionClient

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

class DSLExecutor:
    def __init__(
        self,
        dsl_definition: Dict[str, Any],
        addons_manager: Optional[AddonsManager] = None,
        inference_service: Optional[InferenceService] = None,
        max_workers: int = 4,
        cpu_limit: int = 60,
        mem_limit: int = 512 * 1024 * 1024,
        time_limit: int = 120,
        workflow_id: Optional[str] = None,
        human_intervention_api_url: Optional[str] = None,
        human_intervention_subject_id: str = "default_human_intervention",
    ):
        self.dsl_definition = dsl_definition
        self.workflow_id = workflow_id or str(uuid.uuid4())
        self.addons_manager = addons_manager or AddonsManager()
        self.inference_service = inference_service
        self.persistence = WorkflowPersistence()
        self.output_collector = OutputCollector()

        if human_intervention_api_url:
            self._register_human_intervention_callback(
                human_intervention_api_url, human_intervention_subject_id
            )

        from .executor import DSLWorkflowExecutorLocal
        self.dsl_workflow_executor = DSLWorkflowExecutorLocal(
            dsl=dsl_definition,
            addons_manager=self.addons_manager,
            inference_service=self.inference_service,
            workflow_id=self.workflow_id,
        )

        # Initialize multiprocessing threads manager
        self.manager = DSLThreadsManagerMP(
            dsl_workflow_executor=self.dsl_workflow_executor,
            addons_manager=self.addons_manager,
            inference_service=self.inference_service,
            max_workers=max_workers,
            cpu_limit=cpu_limit,
            mem_limit=mem_limit,
            time_limit=time_limit,
            workflow_id=self.workflow_id,
        )

        # Hook into manager to collect outputs after each task
        self._wrap_manager_execute_task()

    def _register_human_intervention_callback(self, api_url: str, subject_id: str):
        # Create SessionClient
        session_client = SessionClient(api_base_url=api_url)

        # Define the callback function that calls the human intervention client
        def human_intervention_callback(data: Dict[str, Any]):
            return session_client.send_and_wait_for_response(
                session_id=data.get("session_id"),
                channel_id=data.get("channel_id"),
                message=data.get("message"),
                subject_id=subject_id,
                timeout=data.get("timeout", 60),
            )

        # Wrap in DSLCallback and register
        callback = DSLCallback(name="human_intervention", callback_fn=human_intervention_callback)
        self.addons_manager.register_callback(callback)
        logger.info("Registered default human intervention callback 'human_intervention'")

    def _wrap_manager_execute_task(self):
        
        original_execute_task = self.manager.execute_task

        def wrapped_execute_task(module_key, input_data=None):
            output, error = original_execute_task(module_key, input_data)
            if output is not None:
                self.output_collector.collect_output(self.workflow_id, module_key, output)
            return output, error

        self.manager.execute_task = wrapped_execute_task

    def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        logger.info(f"Starting workflow execution with ID: {self.workflow_id}")
        try:
            output = self.manager.execute_workflow(input_data)
            logger.info(f"Workflow execution completed for ID: {self.workflow_id}")
            return output
        except Exception as e:
            logger.error(f"Workflow execution failed: {e}", exc_info=True)
            raise

    def get_task_output(self, module_key: str) -> Optional[Any]:
        return self.output_collector.get_task_output(self.workflow_id, module_key)

    def get_workflow_output(self) -> Optional[Dict[str, Any]]:
        return self.output_collector.get_workflow_output(self.workflow_id)

    def persist_outputs(self):
        self.output_collector.persist_output(self.workflow_id)

    def close(self):
        logger.info(f"Closing DSLExecutor for workflow ID: {self.workflow_id}")
        self.manager.close()
        self.persistence.close()
