from abc import ABC, abstractproperty
from typing import Dict, Union

import pandas as pd
from yfinance import Ticker

from trade.calendar import DateObj
from trade.nse.nse_configs.nse_config import DATE_FMT, NSEConfig
from trade.nse.nse_configs.nse_indices_config import NSEIndexConfig
from trade.technicals.indicators import GenericIndicator
from trade.technicals.option_chain import OptionChain


INDICATOR_IMPLIED_TYPE = Dict[str, GenericIndicator]
OHLC_TYPE = Dict[str, Dict[str, Union[str, int]]]
DEFAULT_PRICES = {
    "open": 0.0,
    "high": 0.0,
    "low": 0.0,
    "close": 0.0,
    "volume": 0.0,
    "prev_volume": 0.0,
    "prev_close": 0.0,
    "pct_change": 0.0,
}


class NSEDataGeneric(ABC):

    def __str__(self):
        return self.symbol

    def __eq__(self, other):
        return self.symbol == other

    def _set_attributes(self, dict_obj: dict, exceptions: tuple = None):
        for key, value in dict_obj.items():
            if exceptions is not None:
                if key not in exceptions:
                    setattr(self, key, value)
            else:
                setattr(self, key, value)

    def set_config(self) -> None:
        match self._ticker_type:
            case "stock":
                self._config = NSEConfig(self.dated)

            case "index":
                self._config = NSEIndexConfig(self.dated)

            case _:
                raise KeyError("Undefined NSE Class.")

    @abstractproperty
    def lot_size(self): ...

    @abstractproperty
    def strike_multiples(self): ...

    @abstractproperty
    def expiries(self): ...

    @property
    def volume_diff(self) -> float:
        if self.prev_volume == 0.0:
            return 0.0

        return round(self.volume / self.prev_volume, 2)

    def yfin_symbol(self) -> str:
        return (
            self.symbol
            if self.symbol not in self._config.yfin_nse_symbols.keys()
            else self._config.yfin_nse_symbols[self.symbol]
        )

    @property
    def price_diff(self) -> float:
        return self.close - self.prev_close

    @property
    def ohlc(self):
        return {
            "open": float(self.open),
            "low": float(self.low),
            "high": float(self.high),
            "close": float(self.close),
            "price_diff": float(self.price_diff),
            "prev_close": float(self.prev_close),
            "pct_change": float(self.pct_change),
            "volume": int(self.volume),
            "prev_volume": int(self.prev_volume),
            "volume_diff": float(self.volume_diff),
        }

    def get_ohlc(self) -> OHLC_TYPE:
        return {self.symbol: self.ohlc}

    @property
    def as_dict(self):
        return {
            "symbol": self.symbol,
            "dated": self.dated,
            **self.ohlc,
        }

    def get_history_data(self, period: str, interval: str) -> pd.DataFrame:
        # Assuming this to be at daily Timeframe.
        symbol = self._config.yfin_nse_symbols[self.symbol]
        return self._config.get_period_data(
            symbol, period=period, interval=interval, index=True
        )[::-1]

    def apply_indicators(
        self,
        gen_indicators: INDICATOR_IMPLIED_TYPE,
        period: str = "1y",
        interval: str = "1d",
    ) -> Dict[str, Dict[str, float]]:

        data = self.get_history_data(period, interval)

        result = {}
        for key, Indicators in gen_indicators.items():
            data = Indicators.apply_indicator(data)
            result.update({key: Indicators.get_df_top_values(data)})

        return result

    def with_indicators(
        self,
        gen_indicators: INDICATOR_IMPLIED_TYPE,
        period: str = "1y",
        interval: str = "1d",
    ) -> Dict[str, Union[float, str]]:

        data = self.as_dict
        indicators = self.apply_indicators(gen_indicators, period, interval)
        data.update(**indicators)
        return data

    def _get_result_data(self, start_date, end_date):

        return self._config.get_period_data(
            self.symbol,
            start=start_date.as_date,
            end=end_date.as_date,
            interval=self.tf,
        )

    def get_curr_bhav(self):
        curr_date = DateObj(self.dated, date_fmt=DATE_FMT)
        start_date = curr_date - 4
        end_date = curr_date + 1
        result = self._get_result_data(start_date, end_date)
        self._set_values(result)

    @property
    def ticker(self) -> Ticker:
        return self._config.yf.Ticker(self._yfsymbol)

    def _set_values(self, result):
        if len(result) > 1:
            try:
                self.prev_volume = int(result.iloc[-2]["volume"])
            except IndexError:
                self.prev_volume = 0

            (
                _,
                self.open,
                self.high,
                self.low,
                self.close,
                self.volume,
                self.prev_close,
                self.pct_change,
            ) = result.iloc[-1]

        else:
            for key, value in DEFAULT_PRICES.items():
                if not hasattr(self, key):
                    setattr(self, key, value)

    def get_option_chain_analysis(self) -> Dict[str, Union[str, int, float]]:
        if hasattr(self, "_oc_analysis"):
            if self._oc_analysis is not None:
                return self._oc_analysis

        if self._ticker_type == "index":
            sym = self._apisymbol
        else:
            sym = self.symbol

        oc_data = self._config.get_option_chain_data(sym)
        month_year = self._config.working_day.as_month_year
        lot_size = self.lot_size
        strike_multiple = self.strike_multiples[self.symbol]
        oc_obj = OptionChain.analyze_option_chain(self.symbol, self.dated,
                                                       oc_data, lot_size,
                                                       strike_multiple)
        self._oc_analysis = oc_obj.option_chain_output()
        return self._oc_analysis
