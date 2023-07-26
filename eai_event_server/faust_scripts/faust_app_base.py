from imports import (
    date, logger, Path,
    asyncio, faust, Worker, codecs,
    OmegaConf
)

from faust_scripts.faust_vars import FaustAppVars

class FaustAppBase:
    def __init__(self,):
        app_config_file = Path(__file__).resolve().parent/"faust_config.yml" 
        app_config = OmegaConf.load(app_config_file.as_posix())
        self.app = faust.App(
            app_config.faust_app_id,
            broker=app_config.broker,
        )
    
    
