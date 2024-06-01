import abc
from typing import Dict, Tuple, Union

import pandas as pd

from trade.utils.utility_enabler import UtilityEnabler

PCR_VERDICT_RANGE = {
    (0, 0.4): "Over Sold",
    (0.4, 0.6): "Very Bearish",
    (0.6, 0.8): "Bearish",
    (0.8, 1.0): "Mildly Bullish",
    (1.0, 1.2): "Bullish",
    (1.2, 1.5): "Very Bullish",
    (1.5, float("inf")): "Over Bought",
}

VERDICT_RANGE_TYPE = Dict[Tuple[float, float], str]


class GenericOptionChain(metaclass=UtilityEnabler):

    def __init__(self, oc_data: pd.DataFrame):
        self.data = oc_data

    def pcr_verdict(
        self, pcr: float, verdict_range: VERDICT_RANGE_TYPE = PCR_VERDICT_RANGE
    ) -> str:
        """Based on the provided pcr, returns a Verdict."""

        for limits, classification in verdict_range.items():
            lower_limit, upper_limit = limits

            if lower_limit <= pcr < upper_limit:
                return classification

        return "Invalid"
