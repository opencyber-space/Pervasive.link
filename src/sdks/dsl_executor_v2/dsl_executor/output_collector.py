import json
import os
import threading
from typing import Any, Dict, Optional


class OutputCollector:

    def __init__(self, storage_dir: str = "/tmp/dsl_outputs"):
       
        self.storage_dir = storage_dir
        os.makedirs(self.storage_dir, exist_ok=True)
        self._outputs_lock = threading.Lock()
        self._outputs: Dict[str, Any] = {}  # In-memory cache keyed by workflow_id or task_id

    def collect_output(self, workflow_id: str, task_id: str, output: Any):
        
        with self._outputs_lock:
            if workflow_id not in self._outputs:
                self._outputs[workflow_id] = {}
            self._outputs[workflow_id][task_id] = output

    def get_task_output(self, workflow_id: str, task_id: str) -> Optional[Any]:
        """
        Retrieve output for a specific task/module.

        :param workflow_id: Workflow instance ID.
        :param task_id: Task/module ID.
        :return: Output data or None if not found.
        """
        with self._outputs_lock:
            return self._outputs.get(workflow_id, {}).get(task_id)

    def get_workflow_output(self, workflow_id: str) -> Optional[Dict[str, Any]]:
       
        with self._outputs_lock:
            return self._outputs.get(workflow_id)

    def persist_output(self, workflow_id: str):
        
        with self._outputs_lock:
            workflow_outputs = self._outputs.get(workflow_id)
            if workflow_outputs is None:
                raise ValueError(f"No outputs found for workflow_id {workflow_id}")

            file_path = os.path.join(self.storage_dir, f"{workflow_id}_output.json")
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(workflow_outputs, f, indent=2)
           

    def load_persisted_output(self, workflow_id: str) -> Optional[Dict[str, Any]]:
        
        file_path = os.path.join(self.storage_dir, f"{workflow_id}_output.json")
        if not os.path.exists(file_path):
            return None
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
