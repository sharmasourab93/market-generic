from abc import ABC
from typing import Dict, Union
from trade.nse.nse_configs.nse_config import NSEConfig
from trade.nse.nse_configs.nse_indices_config import NSEIndexConfig
from trade.technicals.indicators import GenericIndicator
import pandas as pd

INDICATOR_IMPLIED_TYPE = Dict[str, GenericIndicator]
ADV_DEC_TYPE = Dict[Union[bool, None], int]
INDICATOR_NOT_ALLOWED = "Cannot apply indicators to stocks. " \
                        "Only permissible for index."


class AllDataGenerics(ABC):

    def set_config(self) -> None:
        match self._all_ticker_type:
            case "stock":
                self._config = NSEConfig(self.dated)
            case "index":
                self._config = NSEIndexConfig(self.dated)

            case _:
                raise KeyError("Undefined All NSE Data class.")

    @property
    def as_dataframe(self):
        return pd.DataFrame([i.as_dict for i in self.symbols])

    def apply_indicators(self,
                         gen_indicators: INDICATOR_IMPLIED_TYPE,
                         period: str = "1y",
                         interval: str = "1d") -> Dict[str, Dict[str, float]]:
        if self._all_ticker_type == "index":
            symbols = list(self.symbols.values()) if self._all_ticker_type == "index" \
                else self.symbols
            result = dict()

            for symbol in symbols:
                sub_data = symbol.with_indicators(gen_indicators, period, interval)
                result.update({str(symbol): sub_data})

            return result
        else:
            raise IOError(INDICATOR_NOT_ALLOWED)

    @property
    def adv_dev(self) -> Dict[str, int]:
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
