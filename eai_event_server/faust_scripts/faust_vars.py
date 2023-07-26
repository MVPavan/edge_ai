from imports import (
    BaseModel, Path, CWD
)


class FaustAppVars(BaseModel):
    faust_app_id: str
    broker: str
    # worker_port: int
    # worker: Worker = None
    # worker_pid: int = None
    # worker_log: str = None
    # worker_log_file: str = None
    # worker_log_file_handle: str = None
    # worker_log_file_path: str = None