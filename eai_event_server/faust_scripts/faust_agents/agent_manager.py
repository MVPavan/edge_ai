from imports import BaseModel, Callable, Any
from .fake_agents import FakeAgents
from .object_counting import ObjectCountAgents


class BusinessLogics(BaseModel):    
    fake_agent_1: bool = False
    fake_agent_2: bool = False
    fake_agent_3: bool = False
    count_all_objects: bool = False
    count_line_crosser: bool = False
    count_objects_in_area: bool = False
    

class BusinessLogicAgentMapper(BaseModel):
    fake_agent_1:FakeAgents.fake_agent_1 = FakeAgents.fake_agent_1
    fake_agent_2:FakeAgents.fake_agent_2 = FakeAgents.fake_agent_2
    fake_agent_3:FakeAgents.fake_agent_3 = FakeAgents.fake_agent_3
    count_all_objects:ObjectCountAgents.count_all_objects = ObjectCountAgents.count_all_objects
    count_line_crosser:ObjectCountAgents.count_line_crosser = ObjectCountAgents.count_line_crosser
    count_objects_in_area:ObjectCountAgents.count_objects_in_area = ObjectCountAgents.count_objects_in_area


class Agent(BaseModel):
    name: str
    func: Callable = None  # The actual function

    def model_post_init(self, __context: Any) -> None:
        agent_mapper = BusinessLogicAgentMapper().model_dump()
        if self.name in agent_mapper:
            self.func = agent_mapper[self.name]
        else:
            raise ValueError(f"Invalid agent name: {self.name}")
