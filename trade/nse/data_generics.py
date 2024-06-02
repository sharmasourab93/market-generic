from typing import Literal

from trade.technicals.option_chain import IndexOptionChainAnalysis
from trade.technicals.option_chain import StockOptionChain


class NSEDataGeneric:

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
            self._nse_config.get_option_chain_data.get_option_chain_data(self.symbol)
        )

        oc_obj = OptionChain(symbol, option_chain_data, self.dated, strike_multiples)

        return oc_obj.option_chain_output()

    def apply_indicators(self, Indicator: type) -> None: ...
