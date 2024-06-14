from abc import ABC
from typing import Dict, Union, List, Tuple, Any

import pandas as pd

from trade.nse.nse_configs.nse_config import NSEConfig
from trade.nse.nse_configs.nse_indices_config import NSEIndexConfig
from trade.nse.nse_generics.data_generics import OHLC_TYPE
from trade.technicals.indicators import GenericIndicator

INDICATOR_IMPLIED_TYPE = Dict[str, GenericIndicator]
ADV_DEC_TYPE = Dict[Union[bool, None], int]
DATA_HISTORY_DATAFRAMES = Union[Tuple[pd.DataFrame], List[pd.DataFrame]]
INDICATOR_NOT_ALLOWED = (
    "Cannot apply indicators to stocks. " "Only permissible for index."
)


class AllDataGenerics(ABC):

    def __gt__(self, other: Any) -> list:
        return [i for i in self.symbols if i >= other]

    def __lt__(self, other: Any) -> list:
        return [i for i in self.symbols if i <= other]

    def __lte__(self, other: Any) -> list:
        return self.__lt__(other)

    def __gte__(self, other: Any) -> list:
        return self.__gt__(other)

    def set_config(self) -> None:
        match self._all_ticker_type:
            case "stock":
                self._config = NSEConfig(self.dated)
            case "index":
                self._config = NSEIndexConfig(self.dated)

            case _:
                raise KeyError("Undefined All NSE Data class.")

    def get_ohlc(self) -> OHLC_TYPE:
        symbols = (
            self.symbols.values() if isinstance(self.symbols, dict) else self.symbols
        )
        resulting_dict = dict()

        for sym in symbols:
            resulting_dict.update(sym.get_ohlc())

        return resulting_dict

    def get_history_data(self, period: str, interval: str) -> DATA_HISTORY_DATAFRAMES:
        return {
            str(symbol): symbol.get_history_data(period, interval)
            for symbol in self.symbols
        }

    @property
    def as_dataframe(self):
        if self._all_ticker_type == "stock":
            return pd.DataFrame([i.as_dict for i in self.symbols])
        else:
            return pd.DataFrame([i.as_dict for i in self.symbols.values()])

    def apply_indicators(
        self,
        gen_indicators: INDICATOR_IMPLIED_TYPE,
        period: str = "1y",
        interval: str = "1d",
    ) -> Dict[str, Dict[str, float]]:
        if self._all_ticker_type == "index":
            symbols = (
                list(self.symbols.values())
                if self._all_ticker_type == "index"
                else self.symbols
            )
            result = dict()

            for symbol in symbols:
                sub_data = symbol.with_indicators(gen_indicators, period, interval)
                result.update({str(symbol): sub_data})

            return result
        else:
            raise IOError(INDICATOR_NOT_ALLOWED)

    @property
    def adv_dev(self) -> Dict[str, int] | None:
        if self._all_ticker_type == "stock":
            return self._get_advance_decline()
        return None

    def _get_advance_decline(self) -> ADV_DEC_TYPE:
        counter_ = list()
        data = self._get_bhavcopy()

        for i in data.iterrows():
            if (i.close - i.prev_close) < 0:
                counter_.append(False)

            elif (i.close - i.prev_close) == 0:
                counter_.append(None)

            else:
                counter_.append(True)

        adv_dec = dict(Counter(counter_))
        adv_dec["Advances"] = adv_dec.pop(True)
        adv_dec["Declines"] = adv_dec.pop(False)
        adv_dec["Unchanged"] = adv_dec.pop(None)

        return adv_dec

    def _get_bhavcopy(self):
        data = self._config.get_eq_stocks_by_mcap()
        return data
