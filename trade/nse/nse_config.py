from pathlib import Path
from collections.abc import Sequence
from dataclasses import dataclass, field
from functools import cached_property
from io import BytesIO
from yfinance import Ticker
import requests
from datetime import datetime, date, time
from typing import Dict, List, Union, Optional
from trade.utils import LoggingType
from trade.utils import operations
from trade.calendar.calendar_data import MarketHolidayType, MarketTimingType, \
    WorkingDayDate, DateObj, MarketTimings
from trade.ticker import Exchange, ExchangeArgs

DATE_FMT = "%d-%b-%Y"
TODAY = datetime.today().date().strftime(DATE_FMT)
TZ = "Asia/Kolkata"
CONFIG_FILE = Path(__file__).parent.parent.parent / Path("configs/nse.json")
NSE_START_TIME, NSE_CLOSE_TIME, TIME_CUTOFF = "0915", "1530", "1600"
MARKET, COUNTRY = "NSE", "INDIA"
HOLIDAYS_DONOT_EXIST = "Holiday key or holidays do not exist"
MARKET_API_QUOTE_TYPE = Dict[str, Union[list, str, bool]]
TIMINGS = MarketTimings(start_time=NSE_START_TIME,
                        close_time=NSE_CLOSE_TIME,
                        time_zone=TZ,
                        time_cutoff=TIME_CUTOFF)


class NSEConfig(Exchange):

    @property
    def advanced_header(self)-> Dict[str, str]:
        return self.headers["advanced"]

    @property
    def holiday_url(self) -> str:

        return self.main_domain + self.trading

    def get_market_holidays(self, holiday_key: str = "CM") -> List[MarketHolidayType]:
        response = self.get_request_api(self.holiday_url, self.advanced_header)
        content = response.json().get(holiday_key, None)

        if content is None:
            raise KeyError(HOLIDAYS_DONOT_EXIST)

        return content

    def get_equity_meta(self, symbol: str) -> MARKET_API_QUOTE_TYPE:
        symbol = symbol.upper()
        url = self.main_domain + self.equity_meta
        url = url.format(symbol)

        response = self.get_request_api(url, self.advanced_header)
        content = response.json()
        content = None if content == {} else content

        return content

    def get_equity_quote(self, symbol: str, with_trade_info: bool = False)-> \
            MARKET_API_QUOTE_TYPE:

        symbol = symbol.upper()

        if with_trade_info:
            url = self.main_domain + self.equity_trade
        else:
            url = self.main_domain + self.equity_quote

        url = url.format(symbol)

        response = self.get_request_api(url, self.advanced_header)
        content = response.json()
        content = None if content == {} else content

        return content

    def get_eq_bhavcopy(self) -> BytesIO:

        url = self.download_domain + self.eq_bhavcopy["url"]
        headers = self.advanced_header
        today = self.working_day
        day, month, year = today.day, today.month.upper(), today.year
        url = url.format(year, month, day)
        result = self.download_data(url, headers)

        return result

    def __init__(self,
                 today: str,
                 date_fmt: str = DATE_FMT,
                 config: Union[Path, str] = CONFIG_FILE,
                 market: str = MARKET,
                 country: str = COUNTRY,
                 market_timings:MarketTimingType = TIMINGS,
                 ticker_mod: Optional[Dict[str, str]] = None,
                 log_config: Optional[LoggingType] = None):

        super().__init__(today, date_fmt, config, market, country,
                         self.get_market_holidays,market_timings, ticker_mod,
                         log_config)
