from imports import (
    date, logger,
    asyncio, faust, Worker, codecs
)


class FaustAppBase(faust.App):
    def __init__(self, app_name:str, broker:str,):
        super().__init__(
            app_name, 
            broker=broker,
        )
