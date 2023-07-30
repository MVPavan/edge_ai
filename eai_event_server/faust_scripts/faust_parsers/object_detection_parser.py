
from imports import (
    Optional, List, faust
)
from faust_scripts.faust_vars import FaustAppVars
from .parser_vars import object_detection_vars as odv

class ObjectDetectionParser:
    def __init__(self, app:faust.App, app_vars:FaustAppCreateVars):
        self.app = app
        self.app_vars = app_vars
        self.setup_faust_topics()
        self.add_faust_worker_todo()

    def setup_faust_topics(self):
        pipeline_topic = self.app.topic(self.app_vars.pipeline_topic_id, value_type=odv.DetObjRecieved)
        self.app_vars = FaustAppVars(**self.app_vars.model_dump(), pipeline_topic=pipeline_topic)
        self.app_vars.sink_topic = self.app.topic(
            f"{self.app_vars.pipeline_topic_id}_sink", value_type=odv.DetObjParsed
        )

    def add_faust_worker_todo(self):
        self.app.agent(channel=self.app_vars.pipeline_topic)(self.process_messages)

    async def process_messages(self, stream:faust.Stream[odv.DetObjRecieved]):
        async for event in stream:
            # Parse the JSON message
            # Process the record (e.g. write to a database, send to another Kafka topic, etc.)
            event.timestamp = event.__dict__["@timestamp"]
            det_object_list = []
            for obj_str in event.objects:
                det_obj = self.obj_str_parser(obj_str)
                det_object_list.append(det_obj)
            result_object = self.construct_result_object(event, det_object_list)
            await self.app_vars.sink_topic.send(value=result_object)

    @staticmethod
    def obj_str_parser(obj_str:str):
        obj_parts = obj_str.split('|')
        obj_id, x, y, w, h, class_name = obj_parts
        bbox = odv.BoundingBox(x=int(x), y=int(y), w=int(w), h=int(h))
        det_obj = odv.DetectionObject(object_id=obj_id, bounding_box=bbox, class_name=class_name)
        return det_obj

    @staticmethod
    def construct_result_object(infer_obj:odv.DetObjRecieved, det_object_list:list):
        result_obj = odv.DetObjParsed(
            version=infer_obj.version,
            idx=infer_obj.idx,
            timestamp=infer_obj.timestamp,
            sensorId=infer_obj.sensorId,
            objects=det_object_list
        )
        return result_obj