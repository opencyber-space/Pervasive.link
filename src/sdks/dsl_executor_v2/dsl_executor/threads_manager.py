import multiprocessing
import resource
import time
import os
import traceback
import signal
import logging
from typing import Dict, Any, Optional
from collections import defaultdict
from .addons import AddonsManager
from .workflow_state import WorkflowPersistence

logger = logging.getLogger(__name__)


class DSLThreadsManagerMP:
    def __init__(self, dsl_workflow_executor, addons_manager: Optional[AddonsManager] = None, inference_service=None,
                 max_workers: int = 4, cpu_limit: int = 60, mem_limit: int = 512 * 1024 * 1024, time_limit: int = 120,
                 workflow_id: Optional[str] = None):

        self.dsl_workflow_executor = dsl_workflow_executor
        self.addons_manager = addons_manager
        self.inference_service = inference_service
        self.max_workers = max_workers
        self.cpu_limit = cpu_limit
        self.mem_limit = mem_limit
        self.time_limit = time_limit
        self.task_queue = multiprocessing.Queue()
        self.result_queue = multiprocessing.Queue()
        self.processes = []
        self.workflow_id = workflow_id
        self.results = {}  # Shared results dictionary (multiprocessing-safe)
        self.dependency_counts = defaultdict(int)
        self.persistence = WorkflowPersistence()
        self.load_workflow_state()
        self.initialize_dependencies()
        self.enqueue_ready_tasks()

    def initialize_dependencies(self):
        for module_key, targets in self.dsl_workflow_executor.graph.items():
            for target in targets:
                self.dependency_counts[target] += 1
        for module_key in self.dsl_workflow_executor.modules:
            self.dependency_counts.setdefault(module_key, 0)

    def enqueue_ready_tasks(self):
        for module_key, count in self.dependency_counts.items():
            if count == 0:
                self.task_queue.put(module_key)

    def _set_resource_limits(self):
        try:
            resource.setrlimit(resource.RLIMIT_CPU,
                               (self.cpu_limit, self.cpu_limit))
            resource.setrlimit(resource.RLIMIT_AS,
                               (self.mem_limit, self.mem_limit))
            logger.debug(
                f"Resource limits set: CPU={self.cpu_limit}s, Memory={self.mem_limit} bytes")
        except Exception as e:
            logger.error(f"Failed to set resource limits: {e}")

    def worker(self, task_queue: multiprocessing.Queue, result_queue: multiprocessing.Queue):

        self._set_resource_limits()

        while True:
            module_key = task_queue.get()
            if module_key is None:
                logger.info("Received shutdown signal.")
                break  # Shutdown signal

            try:
                logger.info(f"Starting task for module {module_key}")
                start_time = time.time()
                output, error = self.execute_task(module_key)
                duration = time.time() - start_time
                logger.info(f"Completed task {module_key} in {duration:.2f}s")
                result_queue.put((module_key, output, error))
            except Exception as e:
                error_msg = f"Exception in module {module_key}: {e}\n{traceback.format_exc()}"
                logger.error(error_msg)
                result_queue.put((module_key, None, error_msg))

    def execute_task(self, module_key, input_data=None):
        executor = self.dsl_workflow_executor.local_code_executors[module_key]
        try:
            logging.info(f"Executing module: {module_key}")
            module_input = input_data.copy() if input_data else {}
            module_input["previous_outputs"] = self.results
            output = executor.evaluate(module_input)
            self.results[module_key] = output  # Store output
            logging.info(f"Output of module {module_key}: {output}")
            self.persistence.save_module_state(
                module_key, self.workflow_id, output)  # Save module state
            return output, None
        except Exception as e:
            logging.error(f"Error in module {module_key}: {e}")
            return None, e

    def start_workers(self):
        for _ in range(self.max_workers):
            p = multiprocessing.Process(target=self.worker, args=(
                self.task_queue, self.result_queue))
            p.start()
            self.processes.append(p)
        logger.info(f"Started {len(self.processes)} worker processes.")

    def shutdown(self):
        logger.info("Shutting down workers...")
        for _ in self.processes:
            self.task_queue.put(None)  # Poison pill
        for p in self.processes:
            p.join()
        logger.info("All worker processes have been shut down.")

    def execute_workflow(self, input_data: Dict[str, Any]) -> Dict[str, Any]:

        self.start_workers()

        start_time = time.time()
        completed_tasks = set()
        final_output = {}

        while completed_tasks != set(self.dsl_workflow_executor.modules.keys()) and (time.time() - start_time) < self.time_limit:
            try:
                module_key, output, error = self.result_queue.get(timeout=1)
                if module_key:
                    completed_tasks.add(module_key)
                    if error:
                        final_output["error"] = error
                        logger.error(
                            f"Task {module_key} failed with error: {error}")
                    else:
                        logger.info(
                            f"Task {module_key} completed successfully.")
                    for dependent_module in self.dsl_workflow_executor.graph.get(module_key, []):
                        with self.lock:
                            self.dependency_counts[dependent_module] -= 1
                            if self.dependency_counts[dependent_module] == 0:
                                self.task_queue.put(dependent_module)
                else:
                    logger.warning("Received result with no task ID.")
            except multiprocessing.queues.Empty:
                continue

        # Handle any tasks that timed out or never returned results
        remaining_tasks = set(
            self.dsl_workflow_executor.modules.keys()) - completed_tasks
        for module_key in remaining_tasks:
            logger.error(
                f"Task {module_key} timed out or did not return a result.")
            final_output["error"] = "Timeout or no result"

        self.shutdown()

        sink_nodes = [
            node for node in self.dsl_workflow_executor.graph if not self.dsl_workflow_executor.graph[node]]
        if sink_nodes:
            sink_node = sink_nodes[0]
            final_output["output"] = self.results.get(sink_node)
        else:
            logger.warning("No sink nodes found in the workflow graph.")

        return final_output

    def load_workflow_state(self):
        workflow_data = self.persistence.load_workflow_instance(
            self.workflow_id)
        if workflow_data:
            dsl_definition, global_settings, global_parameters = workflow_data
            self.dsl_workflow_executor.dsl = dsl_definition
            self.dsl_workflow_executor.global_settings = global_settings
            self.dsl_workflow_executor.global_parameters = global_parameters

            for module_key in self.dsl_workflow_executor.modules:
                module_state = self.persistence.load_module_state(
                    module_key, self.workflow_id)
                if module_state:
                    self.results[module_key] = module_state
        else:
            logger.info(
                f"No workflow state found for workflow ID: {self.workflow_id}")

    def close(self):
        self.persistence.close()
