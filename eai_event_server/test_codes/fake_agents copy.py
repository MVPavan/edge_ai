from imports import (
    time, asyncio, faust
)

from faust_scripts.faust_parsers.parser_vars import fake_profile_vars as fpv

class FakeAgents:
    def __init__(self, faker_dict:fpv.FakerDict) -> None:
        self.output_dict = faker_dict

    async def fake_agent_1(self, stream:faust.Stream[fpv.DataOut]):
        async for event in stream:
            # await asyncio.sleep(0.1)
            self.output_dict.output[event.ssn] = event

            # if event.ssn not in self.output_dict.output:
            #     self.output_dict.output[event.ssn] = event
            #     self.output_dict.output[event.ssn].website.append("fake_agent_1")
            # else:
            #     self.output_dict.output[event.ssn].website.append("fake_agent_1")
            #     print("fake_agent_1: ", event.ssn)

            self.output_dict.output[event.ssn].faker_agent_1 = True
            # print("fake_agent_1:", self.output_dict.output[event.ssn])
    
    async def fake_agent_2(self, stream:faust.Stream[fpv.DataOut]) -> None:
        async for event in stream:
            await asyncio.sleep(0.1)
            if event.ssn not in self.output_dict.output:
                self.output_dict.output[event.ssn] = event
            else:
                self.output_dict.output[event.ssn].website.append("fake_agent_2")
            self.output_dict.output[event.ssn].faker_agent_2 = True
            print("fake_agent_2:", self.output_dict.output[event.ssn])

    
    async def fake_agent_3(self, stream:faust.Stream[fpv.DataOut]) -> None:
        async for event in stream:
            await asyncio.sleep(0.1)
            if event.ssn not in self.output_dict.output:
                self.output_dict.output[event.ssn] = event
            else:
                self.output_dict.output[event.ssn].website.append("fake_agent_3")
            self.output_dict.output[event.ssn].faker_agent_3 = True
            print("fake_agent_3:", self.output_dict.output[event.ssn])
    
    
