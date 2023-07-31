
from imports import (
    BaseModel, Callable, Any,
)
from faust_scripts.faust_vars import BusinessLogics
from .fake_profile_parser import FakeProfileParser
from .object_detection_parser import ObjectDetectionParser


class FaustParserSelector(BaseModel):
    business_logics: BusinessLogics
    fake_profile_parser: Callable = None
    object_detection_parser: Callable = None
    
    def model_post_init(self, __context: Any):

        if (
            self.business_logics.fake_agent_1 or \
            self.business_logics.fake_agent_2 or \
            self.business_logics.fake_agent_3
            ) and not self.fake_profile_parser:
            self.fake_profile_parser = FakeProfileParser
        
        if (
            self.business_logics.count_all_objects or \
            self.business_logics.count_line_crosser or \
            self.business_logics.count_objects_in_area
            ) and not self.object_detection_parser:
            self.object_detection_parser = ObjectDetectionParser

        assert sum([
            self.fake_profile_parser is not None,
            self.object_detection_parser is not None
        ]) == 1, "Only one parser can be enabled at a time"
