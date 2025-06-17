from dsl_executor import new_dsl_workflow_executor, parse_dsl_output
from dsl_executor.workflow_executor import DSLWorkflowExecutor
from typing import Dict
import os


class Executor:

    def __init__(self) -> None:
        self.stateful_executors: Dict[str, DSLWorkflowExecutor] = {}
        self.workflow_db_uri = os.getenv("WORKFLOW_URI")

    def create_executor(self, stateful: bool, session_id: str, dsl_workflow_data) -> DSLWorkflowExecutor:
        try:
            if stateful:
                if session_id in self.stateful_executors:
                    return self.stateful_executors[session_id]

            if type(dsl_workflow_data) == str:
                dsl_executor = new_dsl_workflow_executor(
                    dsl_workflow_data, self.workflow_db_uri
                )

                if stateful:
                    self.stateful_executors[session_id] = dsl_executor
                    return self.stateful_executors[dsl_executor]
                else:
                    return dsl_executor

            if type(dsl_workflow_data) == dict:
                dsl_executor = DSLWorkflowExecutor(
                    dsl_workflow_data, addons={}
                )

                if stateful:
                    self.stateful_executors[session_id] = dsl_executor
                    return self.stateful_executors[dsl_executor]
                else:
                    return dsl_executor

            return self.stateful_executors[session_id]

        except Exception as e:
            raise e

    def execute(self, execution_data: dict):
        try:

            dsl_data = execution_data['dsl_data']

            if 'session_id' in execution_data:
                dsl_executor = self.create_executor(
                    True, execution_data['session_id'], dsl_data
                )

                result = dsl_executor.execute(execution_data['input'])
                op = parse_dsl_output(
                    result, execution_data.get('output_module', ""))
                return {"success": True, "data": op}

            else:
                dsl_executor = self.create_executor(
                    False, "", dsl_data
                )

                result = dsl_executor.execute(execution_data['input'])
                op = parse_dsl_output(
                    result, execution_data.get('output_module', ""))
                return {"success": True, "data": op}

        except Exception as e:
            return {"success": False, "message": str(e)}
