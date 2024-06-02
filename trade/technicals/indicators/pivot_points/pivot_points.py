from pandas import DataFrame
from typing import Union, Tuple, Dict, List
from trade.technicals.indicators.generic_indicator import GenericIndicator, INDICATOR_MANDATE_KEYS
from trade.technicals.indicators.pivot_points.standard_pivot_points import StandardPivotPoints

OHLC = Union[Dict[str, float], Tuple[float, float, float, float]]
PP_INPUT_DATA = Union[DataFrame, Dict[str, OHLC]]
PIVOT_MAP = {
    "Standard": StandardPivotPoints
}


class PivotPoints(GenericIndicator):

    @classmethod
    def apply_indicator(cls,
                        data: PP_INPUT_DATA,
                        pivot_type: str = "Standard") -> OHLC:

        if isinstance(data, dict):
            open, high, low, close = [data[i] for i in INDICATOR_MANDATE_KEYS[:-1]]
            return PIVOT_MAP[pivot_type].apply_pivot_points(open, high, low, close)

        elif isinstance(data, DataFrame):
            return PIVOT_MAP[pivot_type].apply_pivot_points(data.open,
                                                            data.high,
                                                            data.low,
                                                            data.close)

        else:
            return PIVOT_MAP[pivot_type].apply_pivot_points(*data)
