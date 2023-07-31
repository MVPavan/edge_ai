from typing import Any
from imports import (
    os, BaseModel,
    Optional, List, Dict,
    faust,
)

from .faust_agents.agent_manager import BusinessLogics, Agent

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
    business_logic_agents: Dict[str, Agent] = {}
    
    def model_post_init(self, __context: Any):
        self.business_logic_agents = {
            agent: Agent(name=agent) for agent,val in self.business_logics.model_dump().items() if val
        }