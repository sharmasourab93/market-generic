from dataclasses import dataclass, field
from typing import Dict, List, Optional, Union
from warnings import simplefilter
from yfinance import Ticker
from functools import cached_property
from trade.nse.nse_config import NSEConfig, DATE_FMT
from trade.ticker import StockGenerics
from trade.calendar import DateObj
from trade.utils import operations
import pandas as pd

MARKET_API_QUOTE_TYPE = Dict[str, Union[list, str, bool]]

simplefilter(action='ignore', category=pd.errors.SettingWithCopyWarning)
simplefilter(action='ignore', category=RuntimeWarning)


@dataclass
class NSEStock(StockGenerics):
    symbol: str
    dated: str
    tf: Optional[str] = "1d"

    def __post_init__(self):
        self._nse_config = NSEConfig(self.dated)
        self._yfsymbol = self._nse_config.adjust_yfin_ticker_by_market(self.symbol)
        self.get_curr_bhav()
        self.curr_ohlc = {
            "open": self.open,
            "low": self.low,
            "high": self.high,
            "close": self.close,
            "prev_close": self.prev_close,
            "pct_change": self.pct_change,
            "volume": self.volume,
            "prev_volume": self.prev_volume,
            "volume_diff": self.volume_diff,
        }

    def __str__(self):
        return self.symbol

    @cached_property
    def get_meta_data(self) -> MARKET_API_QUOTE_TYPE:
        return self._nse_config.get_equity_meta(self.symbol)

    @property
    def get_ticker(self) -> Ticker:
        return self._nse_config.yf.Ticker(self._yfsymbol)

    def get_curr_bhav(self):
        curr_date = DateObj(self.dated, date_fmt=DATE_FMT)
        start_date = curr_date - 2
        end_date = curr_date + 1
        result = self._nse_config.get_period_data(
            self.symbol,
            start=start_date.as_date,
            end=end_date.as_date,
            interval=self.tf
        )

        self.prev_volume = result.iloc[-2]["volume"]
        _, self.open, self.high, self.low, self.close, self.volume, \
            self.prev_close, self.pct_change = result.iloc[-1]
        self.volume_diff = (
            operations.calculate_pct_diff(self.volume, self.prev_volume) / 100
        )
