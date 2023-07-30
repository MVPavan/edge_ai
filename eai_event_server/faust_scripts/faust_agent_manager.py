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
    fake_agent_1 = FakeAgents.fake_agent_1
    fake_agent_2 = FakeAgents.fake_agent_2
    fake_agent_3 = FakeAgents.fake_agent_3
    count_all_objects = ObjectCountAgents.count_all_objects
    count_line_crosser = ObjectCountAgents.count_line_crosser
    count_objects_in_area = ObjectCountAgents.count_objects_in_area

class Agent(BaseModel):
    name: str
    func: Callable = None  # The actual function

    @field_validator('func')
    @classmethod
    def map_name_to_func(cls, v, values, **kwargs):
        name = values.get('name')
        agent_mapper = BusinessLogicAgentMapper().model_dump()
        if name in agent_mapper:
            return agent_mapper[name]        
        raise ValueError(f"Invalid agent name: {name}")


class ParserLists(BaseModel):
    fake_profile_parser: Optional[FakeProfileParser] = None
    object_detection_parser: Optional[ObjectDetectionParser] = None
    

class AgentCollection(BaseModel):
    business_logics: BusinessLogics
    parsers: ParserLists = ParserLists()
    business_logic_agents: Dict[str,Agent] = {}


    @field_validator('business_logic_agents')
    @classmethod
    def add_agents(cls, v, values, **kwargs):
        cls.business_logic_agents = [
            Agent(name=agent) for agent in cls.business_logics.model_dump().keys() if agent 
        ]
    
    @field_validator('parsers')
    @classmethod
    def map_name_to_func(cls, v, values, **kwargs):
        if (
            cls.business_logics.fake_agent_1 or \
            cls.business_logics.fake_agent_2 or \
            cls.business_logics.fake_agent_3
            ) and \
            not cls.parsers.fake_profile_parser:
            cls.parsers.fake_profile_parser = FakeProfileParser
        
        if (
            cls.business_logics.count_all_objects or \
            cls.business_logics.count_line_crosser or \
            cls.business_logics.count_objects_in_area
            ) and not \
            cls.parsers.object_detection_parser:
            cls.parsers.object_detection_parser = ObjectDetectionParser

        assert sum(
            cls.fake_profile_parser is not None,
            cls.object_detection_parser is not None
        ) == 1, "Only one parser can be enabled at a time"



    # @field_validator('fake_profile_parser', 'object_detection_parser')
    # @classmethod
    # def map_name_to_func(cls, v, values, **kwargs):
    #     if (cls.fake_agent_1 or cls.fake_agent_2 or cls.fake_agent_3) and \
    #         not cls.fake_profile_parser:
    #         cls.fake_profile_parser = FakeProfileParser
        
    #     if (
    #         (
    #         cls.count_all_objects or \
    #         cls.count_line_crosser or \
    #         cls.count_objects_in_area
    #         ) and not \
    #         cls.object_detection_parser
    #     ):
    #         cls.object_detection_parser = ObjectDetectionParser

    #     assert sum(
    #         cls.fake_profile_parser is not None,
    #         cls.object_detection_parser is not None
    #     ) == 1, "Only one parser can be enabled at a time"
