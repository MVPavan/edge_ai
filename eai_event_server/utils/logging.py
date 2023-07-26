from imports import (sys, Path, logging, TimedRotatingFileHandler, Optional)

from config import FAUST_LOGS_PATH

class Logging:
    def __init__(
            self, 
            log_file: Optional[Path] = None, 
            formatter: Optional[logging.Formatter] = None
        ):
        if log_file is None:
            log_file = Path().cwd()/"logs/edgeai_event_server.log"
        log_file.parent.mkdir(parents=True, exist_ok=True)
        
        assert not log_file.is_dir()
        self.log_file = log_file.as_posix()

        if formatter is None:
            self.formatter = logging.Formatter(
                "%(asctime)s — %(module)s — %(levelname)s — %(funcName)s : %(lineno)d — %(message)s"
            )
        else:
            self.formatter = formatter

    def get_console_handler(self):
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(self.formatter)
        return console_handler

    def get_file_handler(self):
        file_handler = TimedRotatingFileHandler(self.log_file, when='midnight',encoding='utf-8')
        file_handler.setFormatter(self.formatter)
        return file_handler
    
    def set_file_handler(self, log_file):
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setFormatter(self.formatter)
        return file_handler

    def get_logger(self):
        _logger = logging.getLogger()
        _logger.setLevel(logging.DEBUG)  # better to have too much log than not enough
        _logger.addHandler(self.get_console_handler())
        _logger.addHandler(self.get_file_handler())
        # with this pattern, it's rarely necessary to propagate the error up to parent
        _logger.propagate = False
        return _logger

    def get_custom_logger(self, log_file_name):
        _logger = logging.getLogger(log_file_name)
        _logger.setLevel(logging.DEBUG)
        _logger.addHandler(
            self.set_file_handler((FAUST_LOGS_PATH/f"{log_file_name}.log").as_posix())
        )
        _logger.propagate = False
        return _logger


def get_logger():
    logger = Logging().get_logger()
    return logger

def get_logger_with_file(log_file_name):
    logger = Logging().get_custom_logger(log_file_name=log_file_name)
    return logger
