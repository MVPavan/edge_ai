from imports import (
    os, BaseModel,
    Optional, List,
    faust,
)

from .faust_agent_manager import Agent, BusinessLogics

worker_details = lambda app: f"{app.conf._id}:{app.conf.web_port}:{os.getpid()}"

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
    business_logic_agents: List[Agent]



