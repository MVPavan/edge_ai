from imports import (dataclass, field)
from ds_utils.FPS import PERF_DATA

@dataclass
class ObjectStats:
    frame_count:int = 0
    det_count: int = 0
    object_count: dict = field(default_factory=dict)

@dataclass
class DsResultVars(ObjectStats):
    perf_data:PERF_DATA = None
    parser_func = None 
    label_names = None
    fps: float = 0
