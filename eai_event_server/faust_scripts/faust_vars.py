from imports import (
    os, BaseModel, Path, CWD,
    Optional, List,
    faust,
    Counter, Deque, cast, TP, HTTPStatus,
)

worker_details = lambda app: f"{app.conf._id}:{app.conf.web_port}:{os.getpid()}"

class FaustAppCreateVars(BaseModel):
    faust_app_id: str
    broker: str
    pipeline_topic_id: str  

class FaustAppVars(FaustAppCreateVars):
    app: faust.App
    pipeline_topic: Optional[faust.Topic] = None
    sink_topic: Optional[faust.Topic] = None

