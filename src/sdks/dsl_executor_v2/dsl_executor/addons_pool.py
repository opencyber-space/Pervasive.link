import multiprocessing
from multiprocessing import Process, Queue
from typing import Dict, Any, Optional
import traceback
import time

from .addons import AddonsManager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class InferenceTask:
    def __init__(self, addon_name: str, input_data: Dict[str, Any], task_id: Optional[str] = None):
        self.addon_name = addon_name
        self.input_data = input_data
        self.task_id = task_id or str(time.time()) 


class InferenceResult:
    def __init__(self, task_id: str, result: Any = None, error: Optional[str] = None):
        self.task_id = task_id
        self.result = result
        self.error = error


def worker_process(task_queue: Queue, result_queue: Queue, addons_manager):
    
    while True:
        task: InferenceTask = task_queue.get()
        if task is None:
            break

        try:
            result = addons_manager.invoke_inference(task.addon_name, task.input_data)
            result_queue.put(InferenceResult(task.task_id, result=result))
        except Exception as e:
            error_trace = traceback.format_exc()
            result_queue.put(InferenceResult(task.task_id, error=error_trace))


class InferenceTaskPool:
    def __init__(self, addons_manager, num_workers: int = 4):
        self.addons_manager = addons_manager
        self.num_workers = num_workers
        self.task_queue = multiprocessing.Queue()
        self.result_queue = multiprocessing.Queue()
        self.workers = []
        self._start_workers()

    def _start_workers(self):
        for _ in range(self.num_workers):
            p = Process(target=worker_process, args=(self.task_queue, self.result_queue, self.addons_manager))
            p.daemon = True
            p.start()
            self.workers.append(p)

    def submit_task(self, addon_name: str, input_data: Dict[str, Any], task_id: Optional[str] = None) -> str:
        
        task = InferenceTask(addon_name, input_data, task_id)
        self.task_queue.put(task)
        return task.task_id

    def get_result(self, timeout: Optional[float] = None) -> Optional[InferenceResult]:
        
        try:
            return self.result_queue.get(timeout=timeout)
        except multiprocessing.queues.Empty:
            return None

    def shutdown(self):
        
        for _ in self.workers:
            self.task_queue.put(None)  # Send poison pill to each worker

        for p in self.workers:
            p.join()

        self.task_queue.close()
        self.result_queue.close()


from typing import Dict, Any, Optional
import logging



class InferenceService:
   
    def __init__(self, addons_manager: AddonsManager, num_workers: int = 4):
        
        self.addons_manager = addons_manager
        self.task_pool = InferenceTaskPool(addons_manager, num_workers)

    def run_inference(self, addon_name: str, input_data: Dict[str, Any], timeout: Optional[float] = None) -> Any:
        
        task_id = self.task_pool.submit_task(addon_name, input_data)
        logger.info(f"Submitted inference task {task_id} to addon {addon_name}")

        result: InferenceResult = None
        start_time = time.time()

        while True:
            result = self.task_pool.get_result(timeout=1)  # Check every 1 second
            if result and result.task_id == task_id:
                break  # Found our result

            if timeout is not None and time.time() - start_time > timeout:
                raise TimeoutError(f"Inference task {task_id} timed out after {timeout} seconds")

        if result.error:
            logger.error(f"Inference task {task_id} failed: {result.error}")
            raise Exception(f"Inference task failed: {result.error}")

        logger.info(f"Inference task {task_id} completed successfully")
        return result.result

    def shutdown(self):
      
        logger.info("Shutting down InferenceService")
        self.task_pool.shutdown()
