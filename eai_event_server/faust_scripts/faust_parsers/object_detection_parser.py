
from imports import (
    Optional, List, faust
)
from faust_scripts.faust_vars import FaustAppCreateVars, FaustAppVars

class BoundingBox(faust.Record, serializer='json'):
    x: int
    y: int
    w: int
    h: int

class DetectionObject(faust.Record, serializer='json'):
    object_id: str
    class_name: str
    bounding_box: BoundingBox

class InferObject(faust.Record, serializer='json'):
    version: str
    idx: str
    sensorId: str
    objects: list
    timestamp: Optional[str] = None

class ResultObject(faust.Record, serializer='json'):
    version: str
    idx: str
    timestamp: str
    sensorId: str
    objects: List[DetectionObject]


class ObjectDetectionParser:
    def __init__(self, app:faust.App, app_vars:FaustAppCreateVars):
        self.app = app
        self.app_vars = app_vars
        self.setup_faust_topics()
        self.add_faust_worker_todo()

    def setup_faust_topics(self):
        pipeline_topic = self.app.topic(self.app_vars.pipeline_topic_id, value_type=InferObject)
        self.app_vars = FaustAppVars(**self.app_vars.model_dump(), pipeline_topic=pipeline_topic)
        self.app_vars.sink_topic = self.app.topic(
            f"{self.app_vars.pipeline_topic_id}_sink", value_type=ResultObject
        )

    def add_faust_worker_todo(self):
        self.app.agent(channel=self.app_vars.pipeline_topic)(self.process_messages)

    async def process_messages(self, messages):
        async for message in messages:
            # Parse the JSON message
            # Process the record (e.g. write to a database, send to another Kafka topic, etc.)
            message.timestamp = message.__dict__["@timestamp"]
            det_object_list = []
            for obj_str in message.objects:
                det_obj = self.obj_str_parser(obj_str)
                if det_obj.class_name != 'person':
                    # print(message.id, message.timestamp, det_obj.class_name)
                    det_object_list.append(det_obj)
            result_object = self.construct_result_object(message, det_object_list)
            await self.app_vars.sink_topic.send(value=result_object)

    @staticmethod
    def obj_str_parser(obj_str:str):
        obj_parts = obj_str.split('|')
        obj_id, x, y, w, h, class_name = obj_parts
        bbox = BoundingBox(x=int(x), y=int(y), w=int(w), h=int(h))
        det_obj = DetectionObject(object_id=obj_id, bounding_box=bbox, class_name=class_name)
        return det_obj

    @staticmethod
    def construct_result_object(infer_obj:InferObject, det_object_list:list):
        result_obj = ResultObject(
            version=infer_obj.version,
            idx=infer_obj.idx,
            timestamp=infer_obj.timestamp,
            sensorId=infer_obj.sensorId,
            objects=det_object_list
        )
        return result_obj