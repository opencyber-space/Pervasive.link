import asyncio
import websockets
import json
import logging
import uuid

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DSLExecutorClient:
    def __init__(self, ws_url="ws://localhost:8765"):
        self.ws_url = ws_url

    async def _send_task(self, task_payload: dict) -> str:
        try:
            async with websockets.connect(self.ws_url) as websocket:
                logger.info("Connected to DSL Executor WebSocket at %s", self.ws_url)

                task_json = json.dumps(task_payload)
                await websocket.send(task_json)
                logger.info("Sent task: %s", task_json)

                response = await websocket.recv()
                logger.info("Received response: %s", response)
                return response
        except Exception as e:
            logger.error("WebSocket task failed: %s", str(e))
            raise

    def execute_dsl(self, dsl_uri: str, input_data: dict, parameters: dict = None) -> str:
        task = {
            "dsl_uri": dsl_uri,
            "input_data": input_data,
            "parameters": parameters or {}
        }

        return asyncio.run(self._send_task(task))
