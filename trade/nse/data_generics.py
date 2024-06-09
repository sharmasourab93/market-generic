from abc import ABC
from typing import Dict, Literal, Tuple

from trade.technicals.indicators import MovingAverages, PivotPoints
from trade.technicals.option_chain import (
    IndexOptionChainAnalysis,
    StockOptionChainAnalysis,
)


class NSEDataGeneric(ABC):

    def get_option_chain_analysis(
        self, oc_type: Literal["index", "equity"]
    ) -> "OptionChainType":

        match oc_type:

            case "index":
                return self.option_chain_result(IndexOptionChainAnalysis)

            case "equity":
                return (
                    self.option_chain_result(StockOptionChain) if self.is_fno else None
                )

            case _:
                raise KeyError()

    def option_chain_result(self, OptionChain: type):

        option_chain_data = (
            self._nse_config.get_option_chain_data(self.symbol)
        )

        oc_obj = OptionChain(symbol, option_chain_data, self.dated, strike_multiples)

        return oc_obj.option_chain_output()

    def get_history_data(self, period: str, interval: str) -> None:
        # Assuming this to be at daily Timeframe.
        symbol = self._config.yfin_nse_symbols[self.symbol]
        self._history = self._config.get_period_data(
            symbol, period=period, interval=interval, index=True
        )[::-1]

    def apply_indicators(self) -> Dict[str, Dict[str, float]]:

        self.get_history_data("1y", "1d")
        gen_indicators = {"ma": MovingAverages, "pivots": PivotPoints}
        result = {}
        for key, Indicators in gen_indicators.items():
            self._history = Indicators.apply_indicator(self._history)
            result.update({key: Indicators.get_df_top_values(self._history)})
        return result

    @property
    def lot_size(self) -> int:
        month_year = self._config.working_day.as_month_year
        return self._config.get_ticker_folots(self.symbol, month_year)

    def next_expiry(self):
        count_index = 0
        yield self.get_expiries[count_index]

        if count_index < self.get_expiries:
            count_index += 1
        else:
            count_index = 0
