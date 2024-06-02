import asyncio
import os
from cProfile import runctx
from functools import wraps
from os import getenv
from time import perf_counter
from typing import Optional

from pandas import set_option

from trade.utils.log_configurator import LogConfig as Logger
from trade.utils.log_configurator import LoggingType

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

    def __new__(mcs, name, bases, namespace, attrs):
        log_config = attrs.pop("log_config", None)
        enable_time = attrs.pop("enable_time", False)
        enable_profile = attrs.pop("enable_profile", False)

        set_option("chained_assignment", None)
        set_option("copy_on_write", True)

        if logging_config:
            Logger.setup_logging(**logging_config)

        logger = Logger.get_logger(name)
        namespace["logger"] = logger

        for attr_name, attr_value in namespace.items():
            if callable(attr_value) and not attr_name.startswith("__"):
                if enable_time:
                    attr_value = compute_execution_time(attr_value)

                namespace[attr_name] = attr_value

        if not enable_profile:
            return super().__new__(mcs, name, bases, namespace, attrs)

        runctx(
            "return return super().__new__(mcs, name, bases, namespace, attrs)",
            globals(),
            locals(),
        )
