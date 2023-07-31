
from faust_scripts.faust_vars import (
    FaustAppVars, worker_details
)

from .parser_vars.fake_profile_vars import Data, DataOut
from faust_scripts.faust_agents.fake_agents import FakeAgents


class FakeProfileParser:
    def __init__(self, app_vars:FaustAppVars):
        self.app = app_vars.app
        self.app_vars = app_vars
        self.setup_faust_topics()
        self.setup_variables()
        self.add_faust_worker_todo()
        
    def setup_faust_topics(self):
        pipeline_topic = self.app.topic(self.app_vars.pipeline_topic_id, value_type=Data)
        self.app_vars.pipeline_topic = pipeline_topic
        self.app_vars.sink_topics = [self.app.topic(
            f"{self.app_vars.pipeline_topic_id}_sink", value_type=Data
        )]

    def add_faust_worker_todo(self):
        assert self.app_vars.pipeline_topic is not None, \
            f"{worker_details(self.app)} pipeline_topic is None"
        
        self.app.agent(channel=self.app_vars.pipeline_topic, sink=[self.parser_sink], concurrency=3)(self.process_messages)
        # self.app.agent(channel=self.app_vars.pipeline_topic, concurrency=1)(self.process_messages)
        self.app.timer(interval=1)(self.periodic_sender)
        

    def setup_variables(self):
        self.event_count = 0

    async def parser_sink(self,event):
        await self.app_vars.sink_topics[0].send(value=event)
        self.event_count += 1
            
    async def process_messages(self, stream):
        async for event in stream:
            event = DataOut(**event.asdict())
            assert event.fake_agent_1 or event.fake_agent_2 or event.fake_agent_3 == False, \
                f"{worker_details(self.app)}"

            for agent_id, agent in self.app_vars.business_logic_agents.items():
                event = await agent.func(event=event)
                assert getattr(event,agent_id) == True, f"{worker_details(self.app)}"
            # self.event_count += 1
            yield event
            
    async def periodic_sender(self):
        self.app.logger.info(
            f"{worker_details(self.app)}" +
            f" -> message count : {self.event_count}"
        )
        self.event_count = 0

    