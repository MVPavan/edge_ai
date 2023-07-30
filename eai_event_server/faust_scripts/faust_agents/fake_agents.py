from imports import (
    asyncio, faust
)

from faust_scripts.faust_parsers.parser_vars import fake_profile_vars as fpv

class FakeAgents:
    
    @staticmethod
    async def fake_agent_1(event:fpv.DataOut):
        event.website.append("fake_agent_1")
        event.faker_agent_1 = True
        await asyncio.sleep(0.001)
        return event
    
    @staticmethod
    async def fake_agent_2(event:fpv.DataOut):
        event.website.append("fake_agent_2")
        event.faker_agent_2 = True
        await asyncio.sleep(0.001)
        return event
    
    @staticmethod
    async def fake_agent_3(event:fpv.DataOut):
        event.website.append("fake_agent_3")
        event.faker_agent_3 = True
        await asyncio.sleep(0.001)
        return event
    
