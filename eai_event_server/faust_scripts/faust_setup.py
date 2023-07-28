from imports import (
    os,datetime,  Path, CWD,
    logging, logger,get_logger_with_file,
    OmegaConf, 
    asyncio, faust, Worker, codecs,
)

from config import  FAUST_APP_DATA_PATH
from .faust_config import FaustConfig
from .faust_parsers.fake_profile_parser import FakeProfileParser
from .faust_monitor import populate_monitor_from_app
class FaustAppSetup:
    worker_details = lambda app: f"{app.conf._id}:{app.conf.web_port}:{os.getpid()}"

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
        self.app.timer(interval=60)(self.monitor_log)

    def add_fuast_parsers(self):
        if self.app_vars.pipeline_topic_id == "test_kafka_topic":
            FakeProfileParser(app=self.app, app_vars=self.app_vars)
        else:
            raise NotImplementedError

    async def on_started(self,):
        self.app.logger.info(f"Faust worker: {FaustAppSetup.worker_details(self.app)} started")
    
    async def heartbeat(self,):
        self.app.logger.info(f"Heartbeat -> {FaustAppSetup.worker_details(self.app)}")
    
    async def on_stop(self,):
        self.app.logger.info(f"Faust worker {FaustAppSetup.worker_details(self.app)} stopped")

    async def monitor_log(self,):
        monitor_logs = populate_monitor_from_app(self.app)
        monitor_logs_json = monitor_logs.model_dump_json(
            indent=2,
            exclude_none=True
        )
        self.app.logger.info(f"{FaustAppSetup.worker_details(self.app)} Monitor:\n{monitor_logs_json}")