import os
from datetime import datetime
from functools import cache
from pathlib import Path
from typing import Dict, List, Optional, Union

import pandas as pd

from trade.calendar.calendar_data import (
    MarketHolidayType,
    MarketTimings,
    MarketTimingType,
)
from trade.exchange import Exchange
from trade.nse.nse_configs.nse_fno import NSEFNO
from trade.utils import LoggingType
from trade.utils.network_tools import CustomHTTPException
from trade.utils.utility_enabler import UtilityEnabler

DATE_FMT = "%d-%b-%Y"
TODAY = datetime.today().date().strftime(DATE_FMT)
TZ = "Asia/Kolkata"
CONFIG_FILE = Path(__file__).parent.parent.parent.parent / Path("configs/nse.json")
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
TOP_BOTTOM_TYPE = Dict[str, Dict[str, float]]
ENABLE_TIME = bool(os.getenv("ENABLE_TIME", False))
ENABLE_PROFILE = bool(os.getenv("ENABLE_PROFILE", False))
FII_DII_REPORT = List[Dict[str, str]]


class NSEConfig(Exchange, NSEFNO):
    __metaclass__ = UtilityEnabler

    def __init__(
        self,
        today: str,
        date_fmt: str = DATE_FMT,
        config: Union[Path, str] = os.getenv("CONFIG_FILE", CONFIG_FILE),
        market: str = MARKET,
        country: str = COUNTRY,
        market_timings: MarketTimingType = TIMINGS,
        ticker_mod: Optional[Dict[str, str]] = None,
        log_config: Optional[LoggingType] = None,
        enable_time: bool = ENABLE_TIME,
        enable_profile: bool = ENABLE_PROFILE,
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

    def get_top_bottom(self, nos: int = 5, nse_top: int = 200) -> TOP_BOTTOM_TYPE:
        symbols = self.get_nse_stocks()
        get_tops_bottoms = [(i.symbol, i.pct_change, i.diff) for i in symbols[:nse_top]]

        top_nos = nlargest(get_tops_bottoms, nos, key=lambda x: x[1])
        top_nos = {key: {"pct_change": v1, "diff": v2} for key, v1, v2 in top_nos}
        small_nos = nsmallest(get_tops_bottoms, nos, key=lambda x: x[1])
        small_nos = {key: {"pct_change": v1, "diff": v2} for key, v1, v2 in small_nos}
        return {"top": top_nos, "bottom": small_nos}

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

    @cache
    def get_eq_bhavcopy(self) -> pd.DataFrame:
        headers = self.advanced_header
        url = self.eq_bhavcopy["url"] + self.eq_bhavcopy["url_params"]
        today = self.working_day.curr_bday.as_str
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

    @cache
    def get_eq_listed_stocks(self) -> List[str]:
        data = self.get_eq_bhavcopy()
        data = self.apply_nse_data_preprocessing(data)
        return data.symbol.unique().tolist()

    @cache
    def get_eq_stocks_by_mcap(self) -> pd.DataFrame:

        data = self.get_eq_bhavcopy()
        data = self.apply_nse_data_preprocessing(data)
        data = data.rename(columns={"tottrdqty": "volume", "prevclose": "prev_close"})
        data["pct_change"] = (data.close - data.prev_close) / data.prev_close
        data = data.loc[
            :,
            [
                "sr_no",
                "symbol",
                "company_name",
                "market_cap",
                "open",
                "high",
                "low",
                "close",
                "prev_close",
                "volume",
                "pct_change",
            ],
        ]
        filter_out = (
            data.open.isna()
            | data.close.isna()
            | data.high.isna()
            | data.low.isna()
            | data.volume.isna()
        )
        data = data.loc[~filter_out, :]
        return data

    @cache
    def get_nse_stocks(self, nse_top: Optional[int] = None) -> List[str]:

        stock_list = self.get_eq_listed_stocks()

        if nse_top is None:
            return stock_list

        return stock_list[:nse_top]

    @cache
    def get_all_sectors_industries(self) -> pd.DataFrame:
        """A Dataframe of All stocks and its relevant sectors/industry."""

        sectors = self.sectoral_indices

        sectoral_data = {
            sector: self.download_data(url) for sector, url in sectors.items()
        }

        sectoral_list = list()

        for sector, data in sectoral_data.items():
            data["index"] = sector
            sectoral_list.append(data)

        data = pd.concat(sectoral_list)

        return data

    def get_all_etfs(self):

        url = self.main_domain + self.etf_all
        data = self.get_request_api(url, self.advanced_header).json()

        return data

    def get_fii_dii_report(self) -> FII_DII_REPORT:

        url = self.main_domain + self.fii_dii_report
        data = self.get_request_api(url, self.advanced_header).json()

        return data
