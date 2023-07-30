from imports import (
    os,datetime,  Path, CWD,
    logging, logger,get_logger_with_file,
    OmegaConf, 
    asyncio, faust, Worker, codecs,
)

from config import  FAUST_APP_DATA_PATH
from .faust_config import FaustConfig
from .faust_monitor import populate_monitor_from_app
from .faust_vars import worker_details, FaustAppVars
from .faust_agent_manager import Agent, BusinessLogics

from .faust_parsers.fake_profile_parser import FakeProfileParser
from .faust_parsers.object_detection_parser import ObjectDetectionParser
class FaustAppSetup:

    def __init__(self, ) -> None:
        app_vars = FaustConfig.load_faust_config()
        self.app = faust.App(app_vars.faust_app_id, broker=app_vars.broker)
        business_logic_agents = [
            Agent(name=agent) for agent in app_vars.business_logics.model_dump().keys() if agent
        ]
        self.app_vars = FaustAppVars(
            **app_vars.model_dump(), 
            app=self.app,
            business_logic_agents=business_logic_agents
        )
        self.logger_setup()
        self.add_faust_worker_todo()
        self.add_faust_parsers()

    def logger_setup(self):
        logger = get_logger_with_file(log_file_name=self.app_vars.faust_app_id)
        logger.setLevel(logging.INFO)
        self.app.conf.loghandlers = [logger.handlers[0]]
        self.app.conf.datadir = FAUST_APP_DATA_PATH/f"{self.app_vars.faust_app_id}"

    def add_faust_worker_todo(self):
        self.app.task(self.on_started)
        self.app.task(self.on_stop)
        self.app.timer(interval=30)(self.heartbeat)
        self.app.timer(interval=60)(self.monitor_log)

    def add_faust_parsers(self):
        if self.app_vars.business_logics.fake_profile_parser:
            FakeProfileParser(app=self.app, app_vars=self.app_vars)
        elif self.app_vars.business_logics.object_detection_parser:
            ObjectDetectionParser(app=self.app, app_vars=self.app_vars)
        else:
            raise NotImplementedError

    async def on_started(self,):
        self.app.logger.info(f"Faust worker: {worker_details(self.app)} started")
    
    async def heartbeat(self,):
        self.app.logger.info(f"Heartbeat -> {worker_details(self.app)}")
    
    async def on_stop(self,):
        self.app.logger.info(f"Faust worker {worker_details(self.app)} stopped")

    async def monitor_log(self,):
        monitor_logs = populate_monitor_from_app(self.app)
        monitor_logs_json = monitor_logs.model_dump_json(
            indent=2,
            exclude_none=True
        )
        self.app.logger.info(f"{worker_details(self.app)} Monitor:\n{monitor_logs_json}")

