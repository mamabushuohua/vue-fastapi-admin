import sys

# import logging
from loguru import logger as loguru_logger

from app.settings import settings


class Loggin:
    def __init__(self) -> None:
        debug = settings.DEBUG
        if debug:
            self.level = "DEBUG"
        else:
            self.level = "INFO"

    def setup_logger(self):
        loguru_logger.remove()
        loguru_logger.add(sink=sys.stdout, level=self.level)
        # loguru_logger.add(
        #     "{}/{}.log".format(settings.LOGS_ROOT, settings.PROJECT_NAME), level=self.level, rotation="100 MB"
        # )  # Output log messages to a file
        return loguru_logger


loggin = Loggin()
logger = loggin.setup_logger()
