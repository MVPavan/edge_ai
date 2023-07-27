
from imports import (
    os, date, datetime, faust
)
from faust_scripts.faust_vars import FaustAppCreateVars, FaustAppVars

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

class FakeProfileParser:
    def __init__(self, app:faust.App, app_vars:FaustAppCreateVars):
        self.app = app
        self.app_vars = app_vars
        self.setup_faust_topics()
        self.setup_variables()
        self.add_faust_worker_todo()
        

    def setup_faust_topics(self):
        pipeline_topic = self.app.topic(self.app_vars.pipeline_topic_id, value_type=Data)
        self.app_vars = FaustAppVars(**self.app_vars.model_dump(), pipeline_topic=pipeline_topic)
        self.app_vars.sink_topic = self.app.topic(
            f"{self.app_vars.pipeline_topic_id}_sink", value_type=Data
        )

    def add_faust_worker_todo(self):
        self.app.agent(channel=self.app_vars.pipeline_topic)(self.process_messages)
        self.app.timer(interval=10)(self.periodic_sender)

    def setup_variables(self):
        self.message_count = 0

    async def process_messages(self, messages):
        async for message in messages:
            self.message_count += 1
            await self.app_vars.sink_topic.send(value=message)
    
    async def periodic_sender(self):
        self.app.logger.info(
            f"{self.app.conf._id}:{self.app.conf.web_port}:{os.getpid()}" +
            f" -> message count : {self.message_count}"
        )
        self.message_count = 0

