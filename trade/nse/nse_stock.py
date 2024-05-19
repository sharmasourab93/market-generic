from dataclasses import dataclass, field
from typing import Dict, List, Optional, Union

from yfinance import Ticker

from trade.nse.nse_config import NSEConfig
from trade.ticker import StockGenerics

MARKET_API_QUOTE_TYPE = Dict[str, Union[list, str, bool]]


@dataclass
class NSEStock(StockGenerics):
    dated: str
    symbol: str
    tf: Optional[str] = "1d"

    def __post_init__(self):
        self._nse_config = NSEConfig(self.dated)
        self._yfsymbol = self._nse_config.adjust_yfin_ticker_by_market(self.symbol)
        self.get_curr_bhav(period=self.tf, interval=self.tf)

    def __str__(self):
        return self.symbol

    @cached_property
    def get_meta_data(self) -> MARKET_API_QUOTE_TYPE:
        return self._nse_config.get_equity_meta(self.symbol)

    @property
    def get_ticker(self) -> Ticker:
        return self._nse_config.yf.Ticker(self._yfsymbol)

    def get_curr_bhav(self, period: str = "1d", interval: str = "1d"):
        result = self._nse_config.get_period_data(
            self.symbol, period=period, interval=interval
        )
        self.prev_close = result.iloc[0]["Close"]
        self.prev_volume = result.iloc[0]["Volume"]
        self.open, self.high, self.low, self.close, self.volume = result.iloc[-1]
        self.pct_change = operations.calculate_pct_diff(self.close, self.prev_close)
        self.volume_diff = (
            operations.calculate_pct_diff(self.volume, self.prev_volume) / 100
        )
