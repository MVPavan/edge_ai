from imports import (
    Optional, List, faust
)

class BoundingBox(faust.Record, serializer='json'):
    x: int
    y: int
    w: int
    h: int

class DetectionObject(faust.Record, serializer='json'):
    object_id: str
    class_name: str
    bounding_box: BoundingBox

class DetObjRecieved(faust.Record, serializer='json'):
    version: str
    idx: str
    sensorId: str
    objects: list
    timestamp: Optional[str] = None

class DetObjParsed(faust.Record, serializer='json'):
    version: str
    idx: str
    timestamp: str
    sensorId: str
    objects: List[DetectionObject]




