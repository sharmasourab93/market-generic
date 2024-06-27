from abc import ABC
from collections import Counter
from typing import Any, Dict, List, Tuple, Union

import pandas as pd

from trade.nse.nse_configs.nse_config import NSEConfig
from trade.nse.nse_configs.nse_indices_config import NSEIndexConfig
from trade.nse.nse_generics.data_generics import OHLC_TYPE

ADV_DEC_TYPE = Dict[Union[bool, None], int]
DATA_HISTORY_DATAFRAMES = Union[Tuple[pd.DataFrame], List[pd.DataFrame]]


class AllDataGenerics(ABC):

    def __contains__(self, item: str) -> bool:
        if isinstance(self.symbols, list):
            symbols = [i.symbol for i in self.symbols]
        else:
            symbols = self.symbols.keys()

        return item.upper() in symbols

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

    # @property
    def as_dataframe(self):
        if self._all_ticker_type == "stock":
            return pd.DataFrame([i.as_dict for i in self.symbols])
        else:
            return pd.DataFrame([i.as_dict for i in self.symbols.values()])

    # @property
    def adv_dec(self) -> Dict[str, int]:
        return self._get_advance_decline()

    def _get_advance_decline(self) -> ADV_DEC_TYPE:
        counter_ = list()
        data = self._get_bhavcopy()

        for _, i in data.iterrows():
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

    def get_fii_dii_reports(self) -> List[Dict[str, str]]:
        return self._config.get_fii_dii_report()

    def get_option_chain_analysis(self, as_dataframe: bool = True):
        symbols = (
            self.symbols.values() if isinstance(self.symbols, dict) else self.symbols
        )

        data = {str(symbol): symbol.get_option_chain_analysis() for symbol in symbols}

        if as_dataframe:
            return pd.DataFrame(data).transpose().fillna(0)

        return data
