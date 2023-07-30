from typing import Any
from imports import (
    BaseModel, field_validator, model_validator,
    Optional, Dict, Callable,
)

from faust_scripts.faust_agents.fake_agents import FakeAgents
from faust_scripts.faust_agents.object_counting import ObjectCountAgents

from faust_scripts.faust_parsers.fake_profile_parser import FakeProfileParser
from faust_scripts.faust_parsers.object_detection_parser import ObjectDetectionParser

from faust_scripts.faust_vars import BusinessLogics

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


class ParserLists(BaseModel):
    fake_profile_parser: Callable = None
    object_detection_parser: Callable = None
    

class AgentCollection(BaseModel):
    business_logics: BusinessLogics
    parsers: ParserLists = ParserLists()
    business_logic_agents: Dict[str,Agent] = {}

    def model_post_init(self, __context: Any):
        self.business_logic_agents = {
            agent: Agent(name=agent) for agent,val in self.business_logics.model_dump().items() if val
        }
    
        if (
            self.business_logics.fake_agent_1 or \
            self.business_logics.fake_agent_2 or \
            self.business_logics.fake_agent_3
            ) and \
            not self.parsers.fake_profile_parser:
            self.parsers.fake_profile_parser = FakeProfileParser
        
        if (
            self.business_logics.count_all_objects or \
            self.business_logics.count_line_crosser or \
            self.business_logics.count_objects_in_area
            ) and not \
            self.parsers.object_detection_parser:
            self.parsers.object_detection_parser = ObjectDetectionParser

        assert sum([
            self.parsers.fake_profile_parser is not None,
            self.parsers.object_detection_parser is not None
        ]) == 1, "Only one parser can be enabled at a time"



    # @field_validator('fake_profile_parser', 'object_detection_parser')
    # @classmethod
    # def map_name_to_func(cls, v, values, **kwargs):
    #     if (self.fake_agent_1 or self.fake_agent_2 or self.fake_agent_3) and \
    #         not self.fake_profile_parser:
    #         self.fake_profile_parser = FakeProfileParser
        
    #     if (
    #         (
    #         self.count_all_objects or \
    #         self.count_line_crosser or \
    #         self.count_objects_in_area
    #         ) and not \
    #         self.object_detection_parser
    #     ):
    #         self.object_detection_parser = ObjectDetectionParser

    #     assert sum(
    #         self.fake_profile_parser is not None,
    #         self.object_detection_parser is not None
    #     ) == 1, "Only one parser can be enabled at a time"


    # @field_validator('func', mode='before')
    # @classmethod
    # def map_agent_name(cls, v, values, **kwargs):
    #     name = values.get('name')
    #     agent_mapper = BusinessLogicAgentMapper().model_dump()
    #     print("name in agent_mapper: ", name)
        
    #     if name in agent_mapper:
    #         v = agent_mapper[name]
    #         return v        
    #     else:
    #         raise ValueError(f"Invalid agent name: {name}")