from imports import (
    datetime, logging, logger,get_logger_with_file, Path, CWD,
    asyncio, faust, Worker, codecs,
    OmegaConf
)

from config import FAUST_CONFIG_PATH, FAUST_APP_DATA_PATH

def dummy(app: faust.App):
    @app.task
    async def on_started(self):
        logger.info(f"Faust worker started at {datetime.now()}")


def faust_app_create():
    app_config = OmegaConf.load(FAUST_CONFIG_PATH.as_posix())
    app = faust.App(
        app_config.faust_app_id,
        broker=app_config.broker,
    )
    app.conf.datadir = FAUST_APP_DATA_PATH/f"{app_config.faust_app_id}"
    logger = get_logger_with_file(log_file_name=app_config.faust_app_id)
    logger.setLevel(logging.INFO)
    app.conf.loghandlers = [logger.handlers[0]]
    dummy(app)
    return app
    

