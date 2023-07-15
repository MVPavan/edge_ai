from imports import (sys, Path, logging, TimedRotatingFileHandler)


class Logging:
    def __init__(self, log_file: Path = None, formatter: logging.Formatter = None):
        if log_file is None:
            log_file = Path().cwd()/"logs/edgeai_deepstream.log"
        log_file.parent.mkdir(parents=True, exist_ok=True)
        payloads_folder = log_file.parent/"payloads"
        payloads_folder.mkdir(parents=True, exist_ok=True)
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
        file_handler = TimedRotatingFileHandler(self.log_file, when='midnight')
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


def start_logging():
    logger = Logging().get_logger()
    logger.info(5 * "\n")
    logger.info("Starting Deepstream .............")
    return logger
