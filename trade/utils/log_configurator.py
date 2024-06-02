import logging
from dataclasses import dataclass
from datetime import datetime
from logging import config as log_conf
from os import mkdir, path
from pathlib import Path
from typing import Any, Literal, Optional, Union

LOG_MAP = {
    "version": 1,
    "disable_existing_loggers": True,
    "formatters": {
        "simple": {
            "format": "%(asctime)s:[%(levelname)s]: %(name)s: %(message)s",
            "datefmt": "%d/%m/%y %H:%M:%S",
        }
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "simple",
            "stream": "ext://sys.stdout",
        },
        "file_handler": {
            "class": "logging.handlers.RotatingFileHandler",
            "formatter": "simple",
            "maxBytes": 10485760,
            "backupCount": 20,
            "encoding": "utf8",
        },
    },
    "root": {"level": "INFO", "handlers": ["console", "file_handler"]},
}


@dataclass
class LoggingType:
    date_fmt: str
    log_path: str
    level: Literal[0, 10, 20, 30, 40, 50]
    config_path: Optional[str] = None
    to_log: bool = True
    to_console: bool = True


class LogConfig:
    """
    LogConfig Module to Configure logger.
    Logging levels:
    Level        |  Numeric Value
    ------------------|-----------------
    NOTSET       |    0
    DEBUG        |    10
    INFO         |    20
    WARNING      |    30
    ERROR        |    40
    CRITICAL     |    50

    Methods in logger:
    S.No   Logger method       Description
    --------------------------------------------------------------
    1.      Logger.info(msg)    Log with level INFO.
    2.      logger.warning(msg) Log with level WARNING.
    3.      logger.error(msg)   Log with level ERROR.
    4.      logger.critical(msg) Log with level CRITICAL.
    5.      logger.log(lvl, msg) Log with custom level.
    6.      logger.exception(msg, exc_info=True) Log exception.
    7.      logger.debug(msg) Log with level DEBUG.

    """

    LOG_LEVELS = {
        0: logging.NOTSET,
        10: logging.DEBUG,
        20: logging.INFO,
        30: logging.WARNING,
        40: logging.ERROR,
        50: logging.CRITICAL,
    }

    @staticmethod
    def setup_logging(
        date_fmt: str,
        log_path: Union[Path, str],
        config_path: str = None,
        level=logging.INFO,
        to_log=True,
        to_console=True,
    ):
        """
        Configure logging based on provided parameters.
        :param date_fmt:
        :param log_path: Path to the log file.
        :param config_path: Path to the config file.
        :param level: Logging level.
        :param to_log: Enable logging to file.
        :param to_console: Enable logging to console.
        """

        if config_path is None:
            config = LOG_MAP
        else:
            # TODO: Identify the config file type and process accrodingly.
            raise NotImplementedError("Yet to implement Loading Config files.")

        time = datetime.now().strftime(date_fmt)
        log_dir = "log"

        if not (log_path / Path(log_dir)).exists():
            mkdir(log_path / Path(log_dir))

        log_path = log_path / Path(log_dir) / Path(f"log_{time}.log")

        config["handlers"]["file_handler"]["filename"] = str(log_path)
        config["root"]["level"] = LogConfig.LOG_LEVELS[level]

        if not to_log:
            config["root"]["handlers"].pop(-1)

        if not to_console:
            config["root"]["handlers"].pop(0)

        if not (to_log and to_console):
            config["root"]["handlers"].clear()

        log_conf.dictConfig(config)

    @staticmethod
    def get_logger(name):
        """Get a logger instance."""
        return logging.getLogger(name)
