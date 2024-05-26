import json
from collections import Counter
from dataclasses import dataclass, field
from datetime import date, datetime
from functools import cached_property
from typing import Dict, List, Optional, Union
from warnings import simplefilter

import pandas as pd
from yfinance import Ticker

from trade.calendar import DateObj
from trade.nse.nse_config import DATE_FMT, NSE_TOP, NSEConfig
from trade.ticker import StockGenerics
from trade.utils import operations

MARKET_API_QUOTE_TYPE = Dict[str, Union[list, str, bool]]
TICKER_MODIFICATION = {"HDFC": "HDFCBANK"}
simplefilter(action="ignore", category=pd.errors.SettingWithCopyWarning)
simplefilter(action="ignore", category=RuntimeWarning)


@dataclass
class NSEStock(StockGenerics):
    symbol: str
    dated: str
    tf: Optional[str] = "1d"

    def __post_init__(self):
        self._nse_config = NSEConfig(self.dated)

        if self.symbol in TICKER_MODIFICATION.keys():
            self.symbol = TICKER_MODIFICATION[self.symbol]

        self._yfsymbol = self._nse_config.adjust_yfin_ticker_by_market(self.symbol)
        self.get_curr_bhav()
        self._curr_ohlc = {
            "open": self.open,
            "low": self.low,
            "high": self.high,
            "close": self.close,
            "diff": self.diff,
            "prev_close": self.prev_close,
            "pct_change": self.pct_change,
            "volume": self.volume,
            "prev_volume": self.prev_volume,
            "volume_diff": self.volume_diff,
        }

    @property
    def ohlc(self):
        return self._curr_ohlc

    def __str__(self):
        return self.symbol

    def __eq__(self, other):
        return self.symbol == other

    @cached_property
    def get_meta_data(self) -> MARKET_API_QUOTE_TYPE:
        return self._nse_config.get_equity_meta(self.symbol)

    @property
    def ticker(self) -> Ticker:
        return self._nse_config.yf.Ticker(self._yfsymbol)

    @property
    def adv_dec(self):

        match self.diff:

            case self.diff if self.diff > 0:
                return True

            case self.diff if self.diff < 0:
                return Fals

            case _:
                return None

    def get_curr_bhav(self):
        curr_date = DateObj(self.dated, date_fmt=DATE_FMT)
        start_date = curr_date - 2
        end_date = curr_date + 1
        result = self._nse_config.get_period_data(
            self.symbol,
            start=start_date.as_date,
            end=end_date.as_date,
            interval=self.tf,
        )
        try:
            self.prev_volume = result.iloc[-2]["volume"]
        except IndexError:
            print()
        (
            _,
            self.open,
            self.high,
            self.low,
            self.close,
            self.volume,
            self.prev_close,
            self.pct_change,
        ) = result.iloc[-1]
        self.volume_diff = (
            operations.calculate_pct_diff(self.volume, self.prev_volume) / 100
        )
        self.diff = self.close - self.prev_close
