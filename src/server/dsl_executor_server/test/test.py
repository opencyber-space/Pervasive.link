import asyncio
import websockets
import json
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)

workflow_dict = {
    "globalSettings": {
        "incr": 20
    },
    "globalParameters": {
        "param1": "value1"
    },
    "modules": {
        "module1": {
            # Replace with the actual path or URL to module1
            "codePath": "/home/cognitifai/Documents/agentspacev1/systems/dsl/dsl_tests/flow_test/module1",
            "settings": {"module_setting": "value1"},
            "parameters": {"module_param": "value1"}
        },
        "module2": {
            # Replace with the actual path or URL to module2
            "codePath": "/home/cognitifai/Documents/agentspacev1/systems/dsl/dsl_tests/flow_test/module2",
            "settings": {"module_setting": "value2"},
            "parameters": {"module_param": "value2"}
        },
        "module3": {
            # Replace with the actual path or URL to module3
            "codePath": "/home/cognitifai/Documents/agentspacev1/systems/dsl/dsl_tests/flow_test/module3",
            "settings": {"module_setting": "value3"},
            "parameters": {"module_param": "value3"}
        },
        "module4": {
            # Replace with the actual path or URL to module4
            "codePath": "/home/cognitifai/Documents/agentspacev1/systems/dsl/dsl_tests/flow_test/module4",
            "settings": {"module_setting": "value4"},
            "parameters": {"module_param": "value4"}
        }
    },
    "graph": {
        "module1": ["module2", "module3"],
        "module2": ["module4"],
        "module3": ["module4"],
        "module4": []
    }
}


async def test_client():
    uri = "ws://localhost:8765"
    message = {
        "session_id": "",
        "dsl_data": workflow_dict,
        "output_module": "",
        "input": {
            "number": 1000
        }
    }

    try:
        async with websockets.connect(uri) as websocket:
            logging.info("Connected to the WebSocket server at %s", uri)

            await websocket.send(json.dumps(message))
            logging.info("Sent message: %s", message)

            response = await websocket.recv()
            logging.info("Received response: %s", response)

    except websockets.ConnectionClosedError as e:
        logging.error("Connection closed unexpectedly: %s", str(e))

    except Exception as e:
        logging.error("An error occurred: %s", str(e))

if __name__ == "__main__":
    asyncio.run(test_client())
