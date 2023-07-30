from imports import (
    os, BaseModel,
    Optional, List,
    faust,
)


worker_details = lambda app: f"{app.conf._id}:{app.conf.web_port}:{os.getpid()}"


class BusinessLogics(BaseModel):    
    fake_agent_1: bool = False
    fake_agent_2: bool = False
    fake_agent_3: bool = False
    count_all_objects: bool = False
    count_line_crosser: bool = False
    count_objects_in_area: bool = False

class FaustAppCreateVars(BaseModel):
    faust_app_id: str
    broker: str
    pipeline_topic_id: str
    business_logics: BusinessLogics
    sink_topic_ids: Optional[List[str]] = None

class FaustAppVars(FaustAppCreateVars):
    app: faust.App
    pipeline_topic: Optional[faust.Topic] = None
    sink_topics: Optional[List[faust.Topic]] = None



