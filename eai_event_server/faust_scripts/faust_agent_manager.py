from imports import (
    os, BaseModel, field_validator, Path, CWD,
    Optional, List, Callable,
    faust,
    Counter, Deque, cast, TP, HTTPStatus,
)

from faust_scripts.faust_agents.fake_agents import FakeAgents
from faust_scripts.faust_agents.object_counting import ObjectCountAgents

from faust_scripts.faust_parsers.fake_profile_parser import FakeProfileParser
from faust_scripts.faust_parsers.object_detection_parser import ObjectDetectionParser

class AgentMapper(BaseModel):
    fake_agent_1 = FakeAgents.fake_agent_1
    fake_agent_2 = FakeAgents.fake_agent_2
    fake_agent_3 = FakeAgents.fake_agent_3
    count_all_objects = ObjectCountAgents.count_all_objects
    count_line_crosser = ObjectCountAgents.count_line_crosser
    count_objects_in_area = ObjectCountAgents.count_objects_in_area


class AgentsList(BaseModel):    
    fake_agent_1: bool = False
    fake_agent_2: bool = False
    fake_agent_3: bool = False
    count_all_objects: bool = False
    count_line_crosser: bool = False
    count_objects_in_area: bool = False


class Agent(BaseModel):
    name: str
    enabled: bool = False
    func: Callable = None  # The actual function

    @field_validator('func')
    @classmethod
    def map_name_to_func(cls, v, values, **kwargs):
        name = values.get('name')
        agent_mapper = AgentMapper().model_dump()
        if name in agent_mapper:
            return agent_mapper[name]        
        raise ValueError(f"Invalid agent name: {name}")

class ParserList(AgentsList):
    fake_profile_parser: Optional[FakeProfileParser] = None
    object_detection_parser: Optional[ObjectDetectionParser] = None

    @field_validator('fake_profile_parser', 'object_detection_parser')
    @classmethod
    def map_name_to_func(cls, v, values, **kwargs):
        if (cls.fake_agent_1 or cls.fake_agent_2 or cls.fake_agent_3) and \
            not cls.fake_profile_parser:
            cls.fake_profile_parser = FakeProfileParser
        if (
            (
            cls.count_all_objects or \
            cls.count_line_crosser or \
            cls.count_objects_in_area
            ) and not \
            cls.object_detection_parser
        ):
            cls.object_detection_parser = ObjectDetectionParser
                

class AgentRequest(BaseModel):
    business_logics: List[Agent]