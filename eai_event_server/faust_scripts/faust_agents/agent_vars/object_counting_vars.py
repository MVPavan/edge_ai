from imports import (
    BaseModel, Dict
)



class CountObjectsInFrame(BaseModel):
    total_objects_in_frame: int = 0
    classwise_object_total_in_frame: Dict[str, int] = {}

class CountObjects(BaseModel):
    total_objects: int = 0
    classwise_object_total: Dict[str, int] = {}

class CountAllObjects(CountObjectsInFrame, CountObjects):
    pass

class CountLineCrossingConfig(BaseModel):
    line_crossing_threshold: int = 0

class CountLineCrossing(CountAllObjects):
    pass