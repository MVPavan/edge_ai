from imports import (
    BaseModel
)

class FaustAppVars(BaseModel):
    app_name: str
    broker: str
    # worker_port: int
    # worker: Worker = None
    # worker_pid: int = None
    # worker_log: str = None
    # worker_log_file: str = None
    # worker_log_file_handle: str = None
    # worker_log_file_path: str = None