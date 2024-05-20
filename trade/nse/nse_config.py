from collections.abc import Sequence
from dataclasses import dataclass, field
from datetime import date, datetime, time
from functools import cached_property
from io import BytesIO
from pathlib import Path
from typing import Dict, List, Optional, Union

import pandas as pd
import requests
from yfinance import Ticker

from trade.calendar.calendar_data import (
    DateObj,
    MarketHolidayType,
    MarketTimings,
    MarketTimingType,
    WorkingDayDate,
)
from trade.ticker import Exchange, ExchangeArgs
from trade.utils import LoggingType, operations

DATE_FMT = "%d-%b-%Y"
TODAY = datetime.today().date().strftime(DATE_FMT)
TZ = "Asia/Kolkata"
CONFIG_FILE = Path(__file__).parent.parent.parent / Path("configs/nse.json")
NSE_START_TIME, NSE_CLOSE_TIME, TIME_CUTOFF = "0915", "1530", "1600"
MARKET, COUNTRY = "NSE", "INDIA"
HOLIDAYS_DONOT_EXIST = "Holiday key or holidays do not exist"
MARKET_API_QUOTE_TYPE = Dict[str, Union[list, str, bool]]
TIMINGS = MarketTimings(
    start_time=NSE_START_TIME,
    close_time=NSE_CLOSE_TIME,
    time_zone=TZ,
    time_cutoff=TIME_CUTOFF,
)


class NSEConfig(Exchange):

    @property
    def advanced_header(self) -> Dict[str, str]:
        return self.headers["advanced"]

    @property
    def holiday_url(self) -> str:

        return self.main_domain + self.trading

    def get_market_holidays(self, holiday_key: str = "CM") -> List[MarketHolidayType]:
        response = self.get_request_api(self.holiday_url, self.advanced_header)
        content = response.json().get(holiday_key, None)

        if content is None:
            raise KeyError(HOLIDAYS_DONOT_EXIST)

        def replace_holiday_keywords(holiday: dict):
            holiday["trade_day"] = holiday.pop("tradingDate")
            holiday["week_day"] = holiday.pop("weekDay")
            _ = holiday.pop("Sr_no")
            return holiday

        content = [replace_holiday_keywords(i) for i in content]

        return content

    def get_equity_meta(self, symbol: str) -> MARKET_API_QUOTE_TYPE:
        symbol = symbol.upper()
        url = self.main_domain + self.equity_meta
        url = url.format(symbol)

        response = self.get_request_api(url, self.advanced_header)
        content = response.json()
        content = None if content == {} else content

        return content

    def get_equity_quote(
        self, symbol: str, with_trade_info: bool = False
    ) -> MARKET_API_QUOTE_TYPE:

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
        headers = self.advanced_header
        url = self.eq_bhavcopy["url"] + self.eq_bhavcopy["url_params"]
        today = self.working_day.day.as_str
        url = url.format(today)
        result = self.download_data(url, headers)

        return result

    def apply_nse_data_preprocessing(self, data) -> pd.DataFrame:
        data = data.loc[:, ~data.columns.str.contains("^Unnamed")]
        data.columns = [i.lower() for i in data.columns]
        data = data.loc[data.series == "EQ", :]
        # TODO: NSE Market Capitalization to be applied.
        return data

    def get_eq_listed_stocks(self) -> List[str]:
        data = self.get_eq_bhavcopy()
        data = self.apply_nse_data_preprocessing(data)
        return data.symbol.unique().tolist()

    def __init__(
        self,
        today: str,
        date_fmt: str = DATE_FMT,
        config: Union[Path, str] = CONFIG_FILE,
        market: str = MARKET,
        country: str = COUNTRY,
        market_timings: MarketTimingType = TIMINGS,
        ticker_mod: Optional[Dict[str, str]] = None,
        log_config: Optional[LoggingType] = None,
    ):

        super().__init__(
            today,
            date_fmt,
            config,
            market,
            country,
            self.get_market_holidays,
            market_timings,
            ticker_mod,
            log_config,
        )
