from typing import Dict, List, Tuple, Union

from pandas import DataFrame

from trade.technicals.indicators.generic_indicator import (
    INDICATOR_MANDATE_KEYS,
    GenericIndicator,
)
from trade.technicals.indicators.pivot_points.standard_pivot_points import (
    StandardPivotPoints,
)

OHLC = Union[Dict[str, float], Tuple[float, float, float, float]]
PP_INPUT_DATA = Union[DataFrame, Dict[str, OHLC]]
PIVOT_MAP = {"Standard": StandardPivotPoints}


class PivotPoints(GenericIndicator):

    @classmethod
    def apply_indicator(cls, data: PP_INPUT_DATA, pivot_type: str = "Standard") -> OHLC:

        if isinstance(data, dict):
            open, high, low, close = [data[i] for i in INDICATOR_MANDATE_KEYS[:-1]]
            return PIVOT_MAP[pivot_type].apply_pivot_points(open, high, low, close)

        elif isinstance(data, DataFrame):
            return PIVOT_MAP[pivot_type].apply_pivot_points(
                data.open, data.high, data.low, data.close
            )

        else:
            return PIVOT_MAP[pivot_type].apply_pivot_points(*data)

    @staticmethod
    def get_df_top_values(data: DataFrame):
        cols_ = (
            "pivot",
            "bcpr",
            "tcpr",
            "r1",
            "r2",
            "r3",
            "s1",
            "s2",
            "s3",
            "cpr_width",
            "cpr",
        )
        try:
            return data.loc[:, cols_].to_dict(orient="records").pop(0)
        except IndexError:
            return None
