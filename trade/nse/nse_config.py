from collections.abc import Sequence
from dataclasses import dataclass, field
from datetime import date, datetime, time
from functools import cache, cached_property
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
from trade.utils.network_tools import CustomHTTPException

DATE_FMT = "%d-%b-%Y"
TODAY = datetime.today().date().strftime(DATE_FMT)
TZ = "Asia/Kolkata"
CONFIG_FILE = Path(__file__).parent.parent.parent / Path("configs/nse.json")
NSE_START_TIME, NSE_CLOSE_TIME, TIME_CUTOFF = "0915", "1530", "1600"
MARKET, COUNTRY = "NSE", "INDIA"
HOLIDAYS_DONOT_EXIST = "Holiday key or holidays do not exist"
MARKET_API_QUOTE_TYPE = Dict[str, Union[list, str, bool]]
NSE_TOP = 1000
TIMINGS = MarketTimings(
    start_time=NSE_START_TIME,
    close_time=NSE_CLOSE_TIME,
    time_zone=TZ,
    time_cutoff=TIME_CUTOFF,
)


class NSEConfig(Exchange):

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

    @property
    def advanced_header(self) -> Dict[str, str]:
        return self.headers["advanced"]

    @property
    def simple_headers(self) -> Dict[str, str]:
        return self.headers["simple"]

    @property
    def holiday_url(self) -> str:
        return self.main_domain + self.trading

    def replace_holiday_keywords(self, holiday: dict):
        holiday["trade_day"] = holiday.pop("tradingDate")
        holiday["week_day"] = holiday.pop("weekDay")
        _ = holiday.pop("Sr_no")
        return holiday

    def get_market_holidays(self, holiday_key: str = "CM") -> List[MarketHolidayType]:
        response = self.get_request_api(self.holiday_url, self.advanced_header)
        content = response.json().get(holiday_key, None)

        if content is None:
            raise KeyError(HOLIDAYS_DONOT_EXIST)

        content = [self.replace_holiday_keywords(i) for i in content]

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

    def process_mcap_file(self, data: pd.DataFrame) -> pd.DataFrame:

        data.columns = ["sr_no", "symbol", "company_name", "market_cap"]
        data = data.loc[~data.sr_no.isna(), :]
        data = data[pd.to_numeric(data.sr_no, errors="coerce").notnull()]
        data.sr_no = data.sr_no.astype(int)
        data.loc[:, "market_cap"] = pd.to_numeric(data.market_cap, errors="coerce")
        data = data.loc[~data.market_cap.isna(), :]
        # Since the values are in Lakhs, we are making it to crores.
        data.loc[:, "market_cap"] = data.market_cap / 100

        return data

    def get_mcap_file_url(self) -> str:
        url = self.main_domain + self.market_cap["page"]
        tags = tuple(self.market_cap["tags"])
        return self.parse_through_html(url, self.advanced_header, tags)

    @cache
    def get_mcap(self) -> pd.DataFrame:
        url = self.get_mcap_file_url()

        try:
            content = self.download_data(url, self.advanced_header)
        except CustomHTTPException:
            content = self.download_data(url, self.simple_headers)

        content = self.process_mcap_file(content)
        return content

    def apply_mcap(self, data: pd.DataFrame) -> pd.DataFrame:
        mcap = self.get_mcap()
        data = pd.merge(mcap, data, how="left")

        return data

    def apply_nse_data_preprocessing(self, data) -> pd.DataFrame:
        data = data.loc[:, ~data.columns.str.contains("^Unnamed")]
        data.columns = [i.lower() for i in data.columns]
        data = data.loc[data.series == "EQ", :]
        data = self.apply_mcap(data)
        return data

    def get_eq_listed_stocks(self) -> List[str]:
        data = self.get_eq_bhavcopy()
        data = self.apply_nse_data_preprocessing(data)
        return data.symbol.unique().tolist()

    def get_eq_stocks_by_mcap(self) -> pd.DataFrame:

        data = self.get_eq_bhavcopy()
        data = self.apply_nse_data_preprocessing(data)

        return data

    def get_nse_stocks(self, nse_top: Optional[int] = None) -> List[str]:

        stock_list = self.get_eq_listed_stocks()

        if nse_top is None:
            return stock_list

        return stock_list[:nse_top]
