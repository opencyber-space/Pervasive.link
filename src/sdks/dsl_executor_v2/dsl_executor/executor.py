from typing import Dict, Any
import logging

from .threads_manager import DSLThreadsManager
from .function_executor import LocalCodeExecutor

class DSLWorkflowExecutorLocal:
    def __init__(self, dsl: Dict[str, Any], addons_manager=None, inference_service=None, addons={}):
        self.dsl = dsl
        self.global_settings = dsl.get("globalSettings", {})
        self.global_parameters = dsl.get("globalParameters", {})
        self.global_settings.update(addons)
        self.modules = dsl.get("modules", {})
        self.graph = dsl.get("graph", {})
        self.local_code_executors = {}
        self.execution_order = []
        self.validate_and_sort_graph()
        self.addons_manager = addons_manager
        self.inference_service = inference_service
        self.dsl_threads_manager = DSLThreadsManager(self, addons_manager, inference_service)
        self.load_modules()

    def estimate(self):
        return True

    def validate_and_sort_graph(self):
        from collections import defaultdict, deque

        all_graph_keys = set(self.graph.keys())
        all_module_keys = set(self.modules.keys())
        if not all_graph_keys.issubset(all_module_keys):
            raise ValueError(
                f"Graph references undefined module keys: {all_graph_keys - all_module_keys}")

        adjacency_list = defaultdict(list)
        in_degree = defaultdict(int)

        for source, targets in self.graph.items():
            for target in targets:
                adjacency_list[source].append(target)
                in_degree[target] += 1
                in_degree.setdefault(source, 0)

        queue = deque([node for node in in_degree if in_degree[node] == 0])
        visited_count = 0

        while queue:
            current = queue.popleft()
            self.execution_order.append(current)
            visited_count += 1
            for neighbor in adjacency_list[current]:
                in_degree[neighbor] -= 1
                if in_degree[neighbor] == 0:
                    queue.append(neighbor)

        if visited_count != len(in_degree):
            raise ValueError(
                "The graph contains cycles, which are not allowed.")

    def load_modules(self):
        for module_key, module_info in self.modules.items():
            code_path = module_info["codePath"]
            settings = module_info["settings"]
            parameters = module_info["parameters"]

            executor = LocalCodeExecutor(
                download_url=code_path,
                global_settings=self.global_settings,
                global_parameters=self.global_parameters,
                settings=settings,
                parameters=parameters,
                global_state={}
            )

            executor.init()

            self.local_code_executors[module_key] = executor

    def execute(self, input_data: Dict[str, Any]):
        logging.info("Starting concurrent workflow execution with DSLThreadsManager")
        final_output = self.dsl_threads_manager.execute_workflow(input_data)
        logging.info("Workflow execution completed")
        return final_output
