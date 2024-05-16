import asyncio
import os
from functools import wraps
from os import getenv
from time import perf_counter
from typing import Optional

from pandas import set_option

from trade.utils.log_configurator import LogConfig as Logger
from trade.utils.log_configurator import LoggingType
from trade.utils.telegram_api import TelegramBot

EXECUTION_TIME_STR = "Execution time for {0} method {1}: {2}s"
SYNC, ASYNC = "sync", "async"


def compute_execution_time(method):
    if not asyncio.iscoroutinefunction(method):

        @wraps(method)
        def sync_wrapper(self, *args, **kwargs):

            start = perf_counter()

            execution = method(self, *args, **kwargs)

            end = perf_counter()
            elapsed_time = round(end - start, 2)

            self.logger.debug(
                EXECUTION_TIME_STR.format(SYNC, method.__name__, elapsed_time)
            )

            return execution

        return sync_wrapper

    else:

        @wraps(method)
        async def async_wrapper(self, *args, **kwargs):
            start = perf_counter()
            result = await method(self, *args, **kwargs)
            end = perf_counter()
            elapsed_time = round(end - start, 2)
            self.logger.debug(
                EXECUTION_TIME_STR.format(ASYNC, method.__name__, elapsed_time)
            )
            return result

        return async_wrapper


class UtilityEnabler(type):
    logging_config = None

    def __init__(cls, name, bases, attrs, logging_config: Optional[LoggingType] = None):
        super().__init__(name, bases, attrs)
        cls.logging_config = logging_config

    def __new__(mcs, name, bases, namespace):
        enable_time = bool(os.getenv("TIME_COMP", False))
        enable_telegram = bool(os.getenv("ENABLE_TELEGRAM", False))

        set_option("chained_assignment", None)
        set_option("copy_on_write", True)

        if logging_config:
            Logger.setup_logging(**mcs.logging_config)

        logger = Logger.get_logger(name)
        namespace["logger"] = logger

        for attr_name, attr_value in namespace.items():
            if callable(attr_value) and not attr_name.startswith("__"):
                if enable_time:
                    attr_value = compute_execution_time(attr_value)

                namespace[attr_name] = attr_value

        namespace["telegram"] = Telegram(enable_telegram)

        return super().__new__(mcs, name, bases, namespace, logging_config)
