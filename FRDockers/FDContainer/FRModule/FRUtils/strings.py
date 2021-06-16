import json
import numpy as np
from enum import Enum
from json import JSONEncoder


class FRStatusEnum(str, Enum):
    FACE_UNKNOWN = "face_unknown"
    FACE_DETECTED = "face_detected"
    FACE_RECOGNIZED = "face_recognized"
    FACE_REGISTERED = "face_registered"
    FACE_NOT_DETECTED = "face_not_detected"
    MULTIPLE_FACE_DETECTED = "multiple_face_detected"
    
class FRTaskTypeEnum(str, Enum):
    FACE_DETECT = "face_detect"
    FACE_VERIFY = "face_verify"
    FACE_IDENTIFY = "face_identify"
    FACE_REGISTER = "face_register"
    
class TaskStatusEnum(str, Enum):
    passed = "passed"
    failed = "failed"
    inqueue = "inqueue"
    
class FrModesEnum(str, Enum):
    evaluate = "evaluate"
    authenticate = "authenticate"

class NumpyEncoder(JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        else:
            return obj.__dict__
        return JSONEncoder.default(self, obj)

class _JsonEncoder:
    def toJSON(self):
        # return json.dumps(self, default=lambda o: o.__dict__, cls=NumpyEncoder)
        return json.dumps(self, cls=NumpyEncoder)
    def toDict(self):
        return json.loads(self.toJSON())

class _JsonEncoder:
    def toJSON(self):
        # return json.dumps(self, default=lambda o: o.__dict__, cls=NumpyEncoder)
        return json.dumps(self, cls=NumpyEncoder)
    def toDict(self):
        return json.loads(self.toJSON())


class FrResult(_JsonEncoder):
    def __init__(self, **kwargs):
        self.success = False
        self.res_log = {}
        for key, value in kwargs.items():
            setattr(self, key, value)

class FrJob(_JsonEncoder):
    def __init__(self, **kwargs):
        super()
        self.fr_images = []
        self.task_id = None
        self.fr_user = None
        self.fr_group = None
        self.fr_status = None
        self.task_type = None
        self.fr_result = FrResult()
        self.fr_mode:FrModesEnum = FrModesEnum.authenticate
        for key, value in kwargs.items():
            setattr(self, key, value)

# class FEJob(_JsonEncoder):
#     def __init__(self, **kwargs):
#         super()
#         self.aligned_face_list = []
#         self.bbox_list = []
#         self.task_id = None
#         self.fr_user = None
#         self.fr_group = None
#         self.fr_status = None
#         self.task_type = None
#         self.fr_result = FrResult()
#         self.fr_mode:FrModesEnum = FrModesEnum.authenticate
#         for key, value in kwargs.items():
#             setattr(self, key, value)
