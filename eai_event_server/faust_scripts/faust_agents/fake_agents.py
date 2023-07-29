from imports import (
    time, asyncio, faust
)

from faust_scripts.faust_parsers.parser_vars import fake_profile_vars as fpv

class FakeAgents:
    def __init__(self, faker_dict:fpv.FakerDict) -> None:
        self.output_dict = faker_dict

    async def fake_agent_1(self, event:fpv.DataOut):
        event.website.append("fake_agent_1")
        event.faker_agent_1 = True
        await asyncio.sleep(0.001)
        return event
        
    async def fake_agent_2(self, event:fpv.DataOut):
        event.website.append("fake_agent_2")
        event.faker_agent_2 = True
        await asyncio.sleep(0.001)
        return event
    
    async def fake_agent_3(self, event:fpv.DataOut):
        event.website.append("fake_agent_3")
        event.faker_agent_3 = True
        await asyncio.sleep(0.001)
        return event
    
    
