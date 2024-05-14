from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional

from trade.calendar import MarketCalendar, MarketHolidayType, MarketTimingType
from trade.ticker.api_config import APIConfig
from trade.ticker.yf import YFinance
from trade.utils import DownloadTools, Logger, LoggingType


@dataclass
class ExchangeArgs:
    today: str
    date_fmt: str
    config: str
    market: str
    country: str
    market_holidays: List[MarketHolidayType]
    market_timings: List[MarketTimingType]
    ticker_mod: Optional[Dict[str, str]] = None
    log_config: Optional[LoggingType] = None


class Exchange(APIConfig, YFinance, MarketCalendar, DownloadTools):

    def __init__(
        self,
        today: str,
        date_fmt: str,
        config: str,
        market: str,
        country: str,
        market_holidays: List[MarketHolidayType],
        market_timings: List[MarketTimingType],
        ticker_mod: Optional[Dict[str, str]] = None,
        logging_config: Optional[LoggingType] = None,
    ):
        super().__init__(config)
        YFinance.__init__(
            self, market, country, date_fmt, ticker_modifications=ticker_mod
        )
        MarketCalendar.__init__(self, today, date_fmt, market_holidays, market_timings)

        # TODO: Identify a way to make use of metaclasses to enable, logging,
        #  telegram & compute execution time methods.
        # This is just for the time being.
        if logging_config is not None:
            Logger.setup_logging(**logging_config)
            self.logger = Logger.get_logger(__name__)
