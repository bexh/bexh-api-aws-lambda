import logging
import sys
from typing import Literal
import uuid


LogLevel = Literal["INFO", "WARNING", "DEBUG"]


class LoggerFactory:
    @staticmethod
    def get_logger(name: str, log_level: LogLevel = "INFO"):
        return Logger(name=name, log_level=log_level)


class Logger:
    def __init__(self, name: str, log_level: LogLevel = "INFO"):
        self._logger = logging.getLogger(name=name)
        logging_level = self._get_log_level(log_level)
        self._logger.setLevel(logging_level)
        handler = self._get_logging_handler(logging_level)
        self._logger.addHandler(handler)
        self._extras = {"RUN_ID": uuid.uuid4()}

    @staticmethod
    def _get_log_level(log_level: LogLevel):
        log_level_lookup = {
            "INFO": logging.INFO,
            "WARNING": logging.WARNING,
            "DEBUG": logging.DEBUG
        }
        return log_level_lookup.get(log_level, logging.INFO)

    @staticmethod
    def _get_logging_handler(logging_level):
        handler = logging.StreamHandler(sys.stdout)
        handler.setLevel(logging_level)
        formatter = logging.Formatter('[%(levelname)s] created=%(asctime)sZ module=%(name)s run_id=%(RUN_ID)s message=%(message)s')
        formatter.default_time_format = "%Y-%m-%dT%H:%M:%S"
        formatter.default_msec_format = "%s.%03d"
        handler.setFormatter(formatter)
        return handler

    def debug(self, msg: str, **kwargs):
        self._logger.debug(msg=msg, extra=self._extras)

    def info(self, msg: str, **kwargs):
        self._logger.info(msg=msg, extra=self._extras)

    def warning(self, msg: str, **kwargs):
        self._logger.warning(msg=msg, extra=self._extras)

    def error(self, msg: str, **kwargs):
        self._logger.error(msg=msg, exc_info=True, extra=self._extras)

    def critical(self, msg: str, **kwargs):
        self._logger.critical(msg=msg, exc_info=True, extra=self._extras)
