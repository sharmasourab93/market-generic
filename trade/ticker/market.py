from pathlib import Path
from trade.utils import Utilities, Logger, LoggingType
from typing import Union, Optional, Dict
from trade.utils import DownloadTools
from trade.ticker.yf import YFinance
from trade.calendar import MarketCalendar, MarketHolidayType, MarketTimingType
from trade.ticker.api_config import APIConfig


class ExchangeData(APIConfig, YFinance, MarketCalendar, DownloadTools):

    def __init__(self, today, date_fmt, config, market, country, market_holidays,
                 market_timings, ticker_mod):
        APIConfig.__init__(config)
        YFinance.__init__(market, country, date_fmt,ticker_modifications=ticker_mod)
        MarketCalendar.__init__(today, date_fmt, market_holiday, market_timing)


class CombinedMeta(type(ExchangeData), type(Utilities)):
    pass


class Exchange(ExchangeData, metaclass=CombinedMeta):

    def __init__(self, today: str, date_fmt: str,
                 market: str, country: str,
                 market_config: Union[Path, str],
                 market_holiday: MarketHolidayType,
                 market_timing: MarketTimingType,
                 ticker_mod: Optional[Dict[str, str]] = None,
                 logging_config: Optional[LoggingType] = None):

        ExchangeData.__init__(today, date_fmt,
                              market, country,
                              market_config, market_holiday,
                              market_timing, ticker_mod)
