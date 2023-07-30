from imports import (
    time, asyncio, faust
)

from faust_scripts.faust_parsers.parser_vars import object_detection_vars as odv
class ObjectCountAgents:

    @staticmethod
    async def count_all_objects(self, event:odv.DetObjParsed):
        event.website.append("fake_agent_1")
        event.faker_agent_1 = True
        await asyncio.sleep(0.001)
        return event

    @staticmethod 
    async def count_line_crosser(self, event:odv.DetObjParsed):
        event.website.append("fake_agent_2")
        event.faker_agent_2 = True
        await asyncio.sleep(0.001)
        return event
    
    @staticmethod
    async def count_objects_in_area(self, event:odv.DetObjParsed):
        event.website.append("fake_agent_3")
        event.faker_agent_3 = True
        await asyncio.sleep(0.001)
        return event
    
    