from dataclasses import dataclass
from typing import Dict, Union

import pandas as pd
from numpy import array, float64, inf, int64, searchsorted
from pandas import DataFrame, Series

PIVOT_POINT_TYPE = Dict[str, float]
INVALID_SUPPORTS = "Invalid Support levels. Support level range(1, 5)"
INVALID_RESISTANCES = "Invalid resistance Level. Please choose in the range(1,5)"
PIVOT_POINT_CLASSIFICATIONS = ("Standard", "Woodie", "Camarilla", "Fibonacci", "Demark")
PIVOT_ARG_TYPE = Union[float, Series]
PIVOT_LABELS = ("Narrow CPR", "Compact CPR", "Mid CPR", "Wide CPR", "Very Wide CPR")
PIVOT_BINS = (-inf, 0.25, 0.5, 0.75, 0.9, inf)
X_VALUE = 2500


@dataclass
class StandardPivotPoints:

    open: PIVOT_ARG_TYPE
    high: PIVOT_ARG_TYPE
    low: PIVOT_ARG_TYPE
    close: PIVOT_ARG_TYPE

    @property
    def pivot(self) -> PIVOT_ARG_TYPE:
        return (self.high + self.low + self.close) / 3

    @property
    def bcpr(self) -> PIVOT_ARG_TYPE:
        return (self.high + self.low) / 2

    @property
    def tcpr(self) -> PIVOT_ARG_TYPE:
        return (self.pivot - self.bcpr) + self.pivot

    def _apply_xfactor(self, price: float) -> float:
        x_array = [X_VALUE * (2**j) for j in range(8)]
        return searchsorted(array(x_array), price)

    @property
    def cpr_width(self) -> float:
        cpr_width = round((abs(self.tcpr - self.bcpr) / self.pivot) * 100, 2)
        x_factor = self._apply_xfactor(self.close)

        if isinstance(x_factor, float64) or isinstance(x_factor, int64):
            return cpr_width * x_factor if x_factor != 0 else cpr_width

        return cpr_width * x_factor if all(x_factor) != 0 else cpr_width

    def _cpr_classifications_series(self, cpr_width: float):

        for i in range(len(PIVOT_BINS) - 1):
            if PIVOT_BINS[i] <= cpr_width <= PIVOT_BINS[i + 1]:
                return PIVOT_LABELS[i]

        return PIVOT_LABELS[-1]

    @property
    def cpr_classification(self) -> str:
        if isinstance(self.cpr_width, Series):
            return self.cpr_width.apply(self._cpr_classifications_series)

        return self._cpr_classifications_series(self.cpr_width)

    def _calculate_support(self, level: int) -> float:

        match level:
            case 1:
                return (2 * self.pivot) - self.high
            case 2:
                return self.pivot - (self.high - self.low)

            case 3:
                return self.pivot + self._calculate_support(1) / 2

            case 4:
                return self.low - 2 * (self.high - self.pivot)

            case 5:
                return self.pivot - (2 * (self.high - self.low))

            case _:
                raise ValueError(INVALID_SUPPORT)

    def _calculate_resistances(self, level: int) -> float:

        match level:
            case 1:
                return (2 * self.pivot) - self.low

            case 2:
                return self.pivot + (self.high - self.low)

            case 3:
                return (self.pivot + self._calculate_resistances(1)) / 2

            case 4:
                return self.high + 2 * (self.pivot - self.low)

            case 5:
                return self.pivot + 2 * (self.high - self.low)

            case _:
                raise ValueError(INVALID_RESISTANCES)

    @property
    def resistances(self) -> Dict[str, float]:
        return {f"r{i}": self._calculate_resistances(i) for i in range(1, 6)}

    @property
    def supports(self) -> Dict[str, float]:
        return {f"s{i}": self._calculate_support(i) for i in range(1, 6)}

    def consolidate(self) -> Dict[str, PIVOT_ARG_TYPE]:
        result = {
            "open": self.open,
            "high": self.high,
            "low": self.low,
            "close": self.close,
            "pivot": self.pivot,
            "bcpr": self.bcpr,
            "tcpr": self.tcpr,
            "resistances": self.resistances,
            "supports": self.supports,
            "cpr_width": self.cpr_width,
            "cpr": self.cpr_classification,
        }

        if not any(isinstance(val, Series) for val in result.values()):
            return result

        result_to_dict = {
            i: j for i, j in result.items() if i not in ("resistances", "supports")
        }
        result_to_dict.update(result["resistances"])
        result_to_dict.update(result["supports"])

        return pd.DataFrame(result_to_dict)

    @classmethod
    def apply_pivot_points(
        cls, open, high, low, close
    ) -> Dict[str, Union[DataFrame, float]]:

        return cls(open, high, low, close).consolidate()
