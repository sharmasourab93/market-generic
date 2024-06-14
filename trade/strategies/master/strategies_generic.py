from typing import Literal, Tuple, TypeVar
from abc import ABC, abstractmethod, abstractclassmethod

import pandas as pd

from trade.nse.stocks import AllNSEStocks


STRATEGY_TYPE = Literal["Intraday",\
                        "BTST", "Weekly", \
                        "Swing", "Positional",\
                        "Short-term", "Long-Term"]
HISTORICAL_DATASET = Dict[str, pd.DataFrame]
Indicators = TypeVar("Indicators")
INDICATORS = Union[List[Indicators], Tuple[Indicators]]


class StockStrategyMaster(ABC):
    def __init__(self,
                 strategy_name:str,
                 strategy_type: STRATEGY_TYPE,
                 dated:str,
                 top: int):

        self.__name__ = strategy_name
        self.__type__ = strategy_type
        self.stocks = AllNSEStocks(dated, nse_top=top)

    def historical_data(self, period: str, interval:str) -> HISTORICAL_DATA_SET:

        return self.stocks.get_history_data(period, interval)

    def apply_indicators(self, data: HISTORICAL_DATASET, indicators: INDICATORS) -> HISTORICAL_DATASET:
        result_set = dict()
        for symbol, ohlc_data in data.items():
            data = ohlc_data.copy()
            for indicator in indicators:
                data = indicator.apply_indicator(data)

            result_set.update({symbol: data})

        return result_set

    def get_historical_data_with_indicators(self, period:str, interval:str,
                                            indicators:INDICATORS) -> HISTORICAL_DATASET:
        data = self.historical_data(period, interval)
        data = self.apply_indicators(data, indicators)

        return data

    @abstractmethod
    def strategy_filters(self, *args, **kwargs):
        raise NotImplemented()

    @abstractmethod
    def strategy_output(self):
        raise NotImplemented()
