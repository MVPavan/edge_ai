from imports import (
    os,datetime, logging, logger,get_logger_with_file, Path, CWD,
    asyncio, faust, Worker, codecs,
    OmegaConf
)

from config import  FAUST_APP_DATA_PATH
from .faust_config import FaustConfig
from .faust_parsers.fake_profile_parser import FakeProfileParser

class FaustAppSetup:
    def __init__(self, ) -> None:
        self.app_vars = FaustConfig.load_faust_config()
        self.app = faust.App(self.app_vars.faust_app_id, broker=self.app_vars.broker)
        self.logger_setup()
        self.add_faust_worker_todo()
        self.add_fuast_parsers()

    def logger_setup(self):
        logger = get_logger_with_file(log_file_name=self.app_vars.faust_app_id)
        logger.setLevel(logging.INFO)
        self.app.conf.loghandlers = [logger.handlers[0]]
        self.app.conf.datadir = FAUST_APP_DATA_PATH/f"{self.app_vars.faust_app_id}"

    def add_faust_worker_todo(self):
        self.app.task(self.on_started)
        self.app.timer(interval=30)(self.heartbeat)

    def add_fuast_parsers(self):
        if self.app_vars.pipeline_topic_id == "test_kafka_topic":
            FakeProfileParser(app=self.app, app_vars=self.app_vars)
        else:
            raise NotImplementedError

    async def on_started(self,):
        self.app.logger.info(f"Faust worker started")
    
    async def heartbeat(self,):
        self.app.logger.info(f"Heartbeat -> {self.app.conf._id}:{self.app.conf.web_port}:{os.getpid()}")
        # logger.info(f"Latency: {app.monitor.assignment_latency}")

    

