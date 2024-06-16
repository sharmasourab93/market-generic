from abc import ABC, abstractclassmethod, abstractmethod
from pathlib import Path
from typing import Dict, List, Literal, Tuple, TypeVar, Union

import pandas as pd

from trade.calendar import WorkingDayDate
from trade.nse.stocks import AllNSEStocks

STRATEGY_TYPE = Literal[
    "Intraday", "BTST", "Weekly", "Swing", "Positional", "Short-term", "Long-Term"
]
HISTORICAL_DATASET = Dict[str, pd.DataFrame]
Indicators = TypeVar("Indicators")
INDICATORS = Union[List[Indicators], Tuple[Indicators]]


class StockScanMaster(ABC):
    def __init__(
        self, strategy_name: str, strategy_type: STRATEGY_TYPE, dated: str, top: int
    ):

        self.__name__ = strategy_name
        self.__type__ = strategy_type
        self.stocks = AllNSEStocks(dated, nse_top=top)

    def filter_by_pct_change(
        self, pct_change: Union[float, int], compare: str = Literal["gt", "lt"]
    ):

        match compare:
            case "gt":
                return self.stocks > pct_change

            case "lt":
                return self.stocks < pct_change

            case _:
                raise KeyError("Invalid comparator")

    def historical_data(self, period: str, interval: str) -> HISTORICAL_DATASET:

        return self.stocks.get_history_data(period, interval)

    def apply_indicators(
        self, data: HISTORICAL_DATASET, indicators: INDICATORS
    ) -> HISTORICAL_DATASET:
        result_set = dict()
        for symbol, ohlc_data in data.items():
            data = ohlc_data.copy()
            for indicator in indicators:
                data = indicator.apply_indicator(data)

            result_set.update({symbol: data})

        return result_set

    def get_historical_data_with_indicators(
        self, period: str, interval: str, indicators: INDICATORS
    ) -> HISTORICAL_DATASET:
        data = self.historical_data(period, interval)
        data = self.apply_indicators(data, indicators)

        return data

    @abstractmethod
    def strategy_filters(self, *args, **kwargs):
        raise NotImplemented()

    @abstractmethod
    def strategy_output(self):
        raise NotImplemented()

    @property
    def strategy_from_file_name(self) -> str:

        return Path(__file__).name.replace("_", " ").capitalize()
