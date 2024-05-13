from pathlib import Path
from typing import Dict, Optional, Union

from trade.calendar import MarketCalendar, MarketHolidayType, MarketTimingType
from trade.ticker.api_config import APIConfig
from trade.ticker.yf import YFinance
from trade.utils import DownloadTools, Logger, LoggingType, Utilities


class Exchange(APIConfig, YFinance, MarketCalendar, DownloadTools):

    def __init__(
        self,
        today,
        date_fmt,
        config,
        market,
        country,
        market_holidays,
        market_timings,
        ticker_mod,
    ):
        super().__init__(config)
        YFinance.__init__(
            self, market, country, date_fmt, ticker_modifications=ticker_mod
        )
        MarketCalendar.__init__(self, today, date_fmt, market_holidays, market_timings)


class CombinedMeta(type(Exchange), type(Utilities)):
    pass


class Market(Exchange):

    def __init__(
        self,
        today: str,
        date_fmt: str,
        market_config: Union[Path, str],
        market: str,
        country: str,
        market_holiday: MarketHolidayType,
        market_timing: MarketTimingType,
        ticker_mod: Optional[Dict[str, str]] = None,
        logging_config: Optional[LoggingType] = None,
        **kwargs,
    ):

        super().__init__(
            today=today,
            date_fmt=date_fmt,
            market=market,
            country=country,
            config=market_config,
            market_holidays=market_holiday,
            market_timings=market_timing,
            ticker_mod=ticker_mod,
            **kwargs,
        )
