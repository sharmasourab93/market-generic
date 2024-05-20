from abc import ABC
from collections.abc import Sequence

from pandas import DataFrame


class StockGenerics(ABC):
    history = None

    def backtest_conditions(self, conditions): ...

    def apply_indicator(self, indicator: ...): ...

    def apply_condition(self, conditions): ...

    def filter_post_conditions(self, indicators: Sequence[...], conditions): ...

    def fetch_period_data(self, period: str = "1yr", interval: str = "1d") -> None:

        self.history = self._nse_config.get_period_data(self.symbol, period, interval)
        self.history.fillna(0.0, inplace=True)
