from imports import (
    BaseModel, Path, CWD,
    Optional, List,
    faust,
    Counter, Deque, cast, TP, HTTPStatus,
)

class FaustAppCreateVars(BaseModel):
    faust_app_id: str
    broker: str
    pipeline_topic_id: str

class FaustAppVars(FaustAppCreateVars):
    pipeline_topic: faust.Topic
    sink_topic: Optional[faust.Topic] = None


