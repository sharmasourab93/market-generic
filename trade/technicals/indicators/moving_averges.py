from typing import Union, Literal, Tuple, List, Optional

import pandas as pd
from pandas import DataFrame
from numpy import select
import pandas_ta as ta
from trade.technicals.indicators.generic_indicator import GenericIndicator

MOVING_AVERAGE_INTS_TYPE = Union[Tuple[int], List[int]]
MOVING_AVERAGES = Literal["EMA", "SMA", "DMA"]
TYPICAL_MOVING_AVERAGES = (10, 20, 50, 100, 200)
INVALID_MOVING_AVERAGES = "Invalid moving average type"
CROSSOVERS = ("Upside", "Downside", "No Crossover")


class MovingAverages(GenericIndicator):
    __name__ = "Moving Averages"

    def __init__(self,
                 data: Union[dict, DataFrame],
                 ma: MOVING_AVERAGES,
                 on_col: str,
                 ma_range: MOVING_AVERAGE_INTS_TYPE):

        super().__init__(data)
        self.data = data
        self.ma = ma
        self.on_col = on_col
        self.ma_range = ma_range

    def ema(self) -> DataFrame:
        for i in self.ma_range:
            col = f"{self.ma}{i}"
            self.data[col] = ta.ema(self.data[self.on_col], window=i)

        return self.data

    def dma(self) -> DataFrame:
        for i in self.ma_range:
            col = f"{self.ma}{i}"
            self.data[col] = ta.sma(self.data[self.on_col], window=i)

        return self.data

    def add_moving_averages(self) -> pd.DataFrame:

        match self.ma:
            case self.ma if self.ma in ("SMA", "DMA"):
                return self.dma()

            case self.ma if self.ma == "EMA":
                return self.ema()

            case _:
                raise KeyError(INVALID_MOVING_AVERAGES)

    @staticmethod
    def moving_average_crossover(data: DataFrame, ma1: str, ma2: str) -> DataFrame:
        prev_1 = data[ma1].shift(1)
        prev_2 = data[ma2].shift(1)

        cross1 = (data[ma1] <= data[ma2]) & (prev_1 >= prev_2)
        cross2 = (data[ma1] >= data[ma2]) & (prev_1 <= prev_2)

        column = f"{ma1}X{ma2}"

        data[column] = cross1 | cross2
        data[column + "Up_Down"] = select(
            [
                ((data[column] == True) & (data[ma1] >= data[ma2])),
                ((data[column] == True) & (data[ma1] < data[ma2])),
                (data[column] == False),
            ],
            CROSSOVERS,
        )

        return tuple(data.iloc[-1].iloc[-2:].values.tolist())

    @classmethod
    def apply_indicator(cls,
                        data: pd.DataFrame,
                        ma: MOVING_AVERAGES,
                        on_col: str,
                        ma_range: Optional[MOVING_AVERAGE_INTS_TYPE] =
                        TYPICAL_MOVING_AVERAGES) -> DataFrame:
        return cls(data, ma, on_col, ma_range).add_moving_averages()
