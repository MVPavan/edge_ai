from typing import List, Optional
import json
import faust
from faust import Worker
import asyncio

app = faust.App(
    'my-app', 
    broker='kafka://localhost:8097',
)

class BoundingBox(faust.Record, serializer='json'):
    x: int
    y: int
    w: int
    h: int

class YoloxObject(faust.Record, serializer='json'):
    object_id: str
    class_name: str
    bounding_box: BoundingBox

class InferObject(faust.Record, serializer='json'):
    version: str
    id: str
    sensorId: str
    objects: list
    timestamp: Optional[str] = None

class ResultObject(faust.Record, serializer='json'):
    version: str
    id: str
    timestamp: str
    sensorId: str
    objects: List[YoloxObject]

source_topic = app.topic('test_kafka_topic', value_type=InferObject)
sink_topic = app.topic('faust_sink_topic', value_type=ResultObject)

def yolox_obj_str_parser(obj_str:str):
    obj_parts = obj_str.split('|')
    obj_id, x, y, w, h, class_name = obj_parts
    bbox = BoundingBox(x=int(x), y=int(y), w=int(w), h=int(h))
    yolox_obj = YoloxObject(object_id=obj_id, bounding_box=bbox, class_name=class_name)
    return yolox_obj

def construct_result_object(infer_obj:InferObject, yolox_obj_list:list):
    result_obj = ResultObject(
        version=infer_obj.version,
        id=infer_obj.id,
        timestamp=infer_obj.timestamp,
        sensorId=infer_obj.sensorId,
        objects=yolox_obj_list
    )
    return result_obj

@app.agent(source_topic)
async def process_messages(messages):
    async for message in messages:
        # Parse the JSON message
        # Process the record (e.g. write to a database, send to another Kafka topic, etc.)
        message.timestamp = message.__dict__["@timestamp"]
        yolox_object_list = []
        for obj_str in message.objects:
            yolox_obj = yolox_obj_str_parser(obj_str)
            if yolox_obj.class_name != 'person':
                # print(message.id, message.timestamp, yolox_obj.class_name)
                yolox_object_list.append(yolox_obj)
        result_object = construct_result_object(message, yolox_object_list)
        await sink_topic.send(value=result_object)

# if __name__ == '__main__':
#     app.main()

def start_faust_app():
    worker = app.Worker(loglevel=20)
    worker.execute_from_commandline()

if __name__ == '__main__':
    start_faust_app()


async def start_worker(worker: Worker) -> None:
    await worker.start()

def manage_loop():
    loop = asyncio.get_event_loop()
    worker = Worker(app, loop=loop)
    try:
        loop.run_until_complete(start_worker(worker))
    finally:
        worker.stop_and_shutdown_loop()


