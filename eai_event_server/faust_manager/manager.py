from imports import (
    subprocess, signal, time, logger,
    Optional, BaseModel
)

class FaustManager:
    FAUST_WORKER_PORT = 6300

    def __init__(self,):
        self.faust_worker_map = {}

    def __start_worker(self, app_name:str):
        worker = subprocess.Popen(
            ["faust", "-A", app_name, "worker", "-l", "info", "--web-port", str(self.FAUST_WORKER_PORT)],
            # start_new_session=True # Enable it if you want to the worker to run even if event server is stopped
        )

        logger.info(f"Started worker at port:{self.FAUST_WORKER_PORT} with PID {worker.pid}")
        return worker

    def __stop_worker(self, worker:Optional[subprocess.Popen] = None):
        if worker is None:
            raise ValueError("Worker with PID {worker.pid} does not exist")
        
        worker.send_signal(signal.SIGINT)
        worker.wait()  # Wait for process to terminate
        logger.info(f"Stopped worker with PID {worker.pid}")

    def spawn_workers(self, app_name:str, pipeline_id:str, number_of_workers:int=3):
        self.faust_worker_map[pipeline_id] = {}

        for i in range(number_of_workers):
            self.FAUST_WORKER_PORT = self.FAUST_WORKER_PORT + 1
            worker = self.__start_worker(app_name=app_name)
            self.faust_worker_map[pipeline_id][self.FAUST_WORKER_PORT] = worker
        return self
    
    def stop_worker_port(self, pipeline_id:str, worker_port:str):
        worker = self.faust_worker_map[pipeline_id][worker_port]
        logger.info(f"Stopping worker at port {worker_port} with PID {worker.pid}")
        self.__stop_worker(worker=worker)

    def stop_workers_pipeline(self, pipeline_id:str):
        for worker_port, worker in self.faust_worker_map[pipeline_id].items():
            self.stop_worker_port(pipeline_id=pipeline_id, worker_port=worker_port)
    
    def stop_all_workers(self):
        for pipeline_id in self.faust_worker_map.keys():
            self.stop_workers_pipeline(pipeline_id=pipeline_id)
    


