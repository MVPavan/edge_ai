
from imports import (
    os, time, date, datetime, asyncio, faust
)
from faust_scripts.faust_vars import (
    FaustAppVars, worker_details
)

from .parser_vars.fake_profile_vars import Data,DataOut, FakerDict
from faust_scripts.faust_agents.fake_agents import FakeAgents

class FakeProfileParser:
    def __init__(self, app:faust.App, app_vars:FaustAppVars):
        self.app = app
        self.app_vars = app_vars
        self.output_dict = FakerDict()
        self.faker_agents = FakeAgents(faker_dict=self.output_dict)
        self.setup_faust_topics()
        self.setup_variables()
        self.add_faust_worker_todo()
        
    def setup_faust_topics(self):
        pipeline_topic = self.app.topic(self.app_vars.pipeline_topic_id, value_type=Data)
        self.app_vars.pipeline_topic = pipeline_topic
        self.app_vars.sink_topic = self.app.topic(
            f"{self.app_vars.pipeline_topic_id}_sink", value_type=Data
        )

    def add_faust_worker_todo(self):
        assert self.app_vars.pipeline_topic is not None, \
            f"{worker_details(self.app)}pipeline_topic is None"
        
        # self.app.agent(channel=self.app_vars.pipeline_topic)(self.process_messages)
        self.app.agent(channel=self.app_vars.pipeline_topic, sink=[self.parser_sink])(self.process_messages)
        self.app.timer(interval=10)(self.periodic_sender)
        
        self.channel_1 = self.app.channel(value_type=Data)
        self.app.agent(channel=self.channel_1)(self.faker_agents.fake_agent_1)
        
        # self.channel_2 = self.app.channel(value_type=Data)
        # self.channel_3 = self.app.channel(value_type=Data)
        # self.app.agent(channel=self.channel_2)(self.faker_agents.fake_agent_2)
        # self.app.agent(channel=self.channel_3)(self.faker_agents.fake_agent_3)

        # self.channel_t = self.app.channel(value_type=Data)
        # self.app.agent(channel=self.channel_t)(self.test)

    def setup_variables(self):
        self.event_count = 0

    async def parser_sink(self,value:str):
        while not value in self.faker_agents.output_dict.output:
            print("waiting for: ", value)
            await asyncio.sleep(0.1)
        data:DataOut = self.faker_agents.output_dict.output[value]
        # while not (data.faker_agent_1): # and data.faker_agent_2 and data.faker_agent_3):
        #     await asyncio.sleep(0.1)
        await self.app_vars.sink_topic.send(value=Data.from_data(data.asdict()))
        self.event_count += 1


    async def test(self, stream):
        async for event in stream:
            self.faker_agents.output_dict.output[event.ssn] = event
            
    async def process_messages(self, stream):
        async for event in stream:
            event = DataOut(**event.asdict())
            # print("event:", event.asdict(), "\nchannel: ",self.channel_t)
            
            # await self.channel_t.send(value=event)
            # print("event:", event)

            # if event.ssn in self.output_dict.output:
            #     # print("Duplicate: ", event.ssn)
            #     continue

            await self.channel_1.send(value=event)
            # await self.channel_2.send(value=event)
            # await self.channel_3.send(value=event)
            yield event.ssn
            
    
    async def periodic_sender(self):
        self.app.logger.info(
            f"{worker_details(self.app)}" +
            f" -> message count : {self.event_count}"
        )
        self.event_count = 0

    