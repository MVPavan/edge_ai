from imports import (
    date, BaseModel, Dict, faust
)
class Data(faust.Record, serializer='json'):
    job: str
    company: str
    ssn: str
    residence: str
    blood_group: str
    website: list[str]
    username: str
    name: str
    sex: str
    address: str
    mail: str
    birthdate: date

class DataOut(Data):
    fake_agent_1:bool = False
    fake_agent_2:bool = False
    fake_agent_3:bool = False

class FakerDict(BaseModel):
    output: Dict[str, DataOut] = {}
    