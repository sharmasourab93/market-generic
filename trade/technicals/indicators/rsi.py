from abc import ABC, abstractmethod
from typing import Dict, Union

import pandas as pd
from pandas import DataFrame

from trade.technicals.indicators.generic_indicator import GenericIndicator


class RSI(GenericIndicator):
    __name__ = "Relative Strength Index (RSI)"

    def __init__(self, data: DataFrame, period: int = 14):
        super().__init__(data)
        self.data = data
        self.period = period

    def calculate_rsi(self) -> DataFrame:
        delta = self.data["close"].diff().dropna()
        up, down = delta.copy(), delta.copy()
        up[up < 0] = 0
        down[down > 0] = 0
        roll_up = up.rolling(window=self.period).mean()
        roll_down = down.rolling(window=self.period).mean().abs()
        RS = roll_up / roll_down
        RSI = 100.0 - (100.0 / (1.0 + RS))
        self.data["RSI"] = RSI
        return self.data[::-1]

    @classmethod
    def apply_indicator(
        cls,
        data: pd.DataFrame,
        period: int = 14,
    ) -> DataFrame:
        return cls(data, period).calculate_rsi()
