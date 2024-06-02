from abc import ABC, abstractmethod

import pandas as pd

INDICATOR_MANDATE_KEYS = ("open", "high", "low", "close", "volume")
INVALID_DATA_FORMAT = "Invalid Data Format provided for Indicator"


class GenericIndicator(ABC):

    def __init__(self, data, **kwargs):

        if isinstance(data, dict):
            if all(keys in INDICATOR_MANDATE_KEYS for keys in data.keys()):
                self.data = data

        elif isinstance(data, pd.DataFrame):
            if all(column in data.columns for column in INDICATOR_MANDATE_KEYS):
                self.data = data

        else:
            raise ValueError(INVALID_DATA_FORMAT)

    @abstractmethod
    def apply_indicator(self, *args, **kwargs): ...
