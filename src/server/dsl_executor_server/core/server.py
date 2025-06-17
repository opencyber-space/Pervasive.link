import asyncio
import websockets
import threading
import queue
import uuid
import os
import json
import logging

from .executor import Executor

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler("server.log"),
        logging.StreamHandler()
    ]
)

task_queue = queue.Queue()


class DSLWorker:
    def __init__(self, max_threads):
        self.max_threads = max_threads
        self.semaphore = threading.Semaphore(max_threads)
        self.running = True
        self.executor = Executor()

    def start(self):
        worker_thread = threading.Thread(
            target=self._process_tasks, daemon=True)
        worker_thread.start()
        logging.info(
            "DSLWorker started with a maximum of %d threads.", self.max_threads)

    def stop(self):
        self.running = False

    def _process_tasks(self):
        while self.running:
            try:
                task_id, task_data, output_queue = task_queue.get()
                logging.info("Processing task %s: %s", task_id, task_data)
                self.semaphore.acquire()

                threading.Thread(
                    target=self._process_task, args=(
                        task_id, task_data, output_queue), daemon=True
                ).start()

            except Exception as e:
                logging.error("Error while processing tasks: %s", str(e))

    def _process_task(self, task_id, task_data, output_queue):
        try:
            # Simulate task processing (replace with actual processing function)
            logging.info("Task %s is being processed.", task_id)

            result = self.executor.execute(task_data)

            output_queue.put(result)
            logging.info("Task %s completed with result: %s", task_id, result)

        except Exception as e:
            logging.error("Error while processing task %s: %s",
                          task_id, str(e))
            output_queue.put(f"Error: {str(e)}")

        finally:
            self.semaphore.release()


async def websocket_handler(websocket, path):
    output_queue = queue.Queue()

    try:
        logging.info("New client connected: %s", websocket.remote_address)

        async for message in websocket:
            task_id = str(uuid.uuid4())
            logging.info("Received task from client %s: %s",
                         websocket.remote_address, message)

            message = json.loads(message)

            # Add task to the global queue
            task_queue.put((task_id, message, output_queue))

            # Wait for the result from the output queue
            try:
                # Timeout to avoid blocking indefinitely
                result = output_queue.get()
                await websocket.send(result)
                logging.info("Sent result to client %s: %s",
                             websocket.remote_address, result)
            except queue.Empty:
                error_message = "Task processing timed out."
                await websocket.send(error_message)
                logging.warning("Timeout for task %s from client %s",
                                task_id, websocket.remote_address)

    except websockets.ConnectionClosed:
        logging.info("Connection closed by client: %s",
                     websocket.remote_address)

    except Exception as e:
        logging.error("Error in websocket handler: %s", str(e))

    finally:
        logging.info("Client disconnected: %s", websocket.remote_address)


def run_server():
    try:
        # Start the DSLWorker
        worker = DSLWorker(max_threads=int(os.getenv("MAX_WORKERS", "4")))
        worker.start()

        # Start the WebSocket Server
        start_server = websockets.serve(websocket_handler, "localhost", 8765)
        logging.info("WebSocket server starting on ws://localhost:8765")

        asyncio.get_event_loop().run_until_complete(start_server)
        asyncio.get_event_loop().run_forever()

    except KeyboardInterrupt:
        logging.info("Shutting down server...")
        worker.stop()

    except Exception as e:
        logging.error("Unhandled exception: %s", str(e))

    finally:
        logging.info("Server shut down.")
