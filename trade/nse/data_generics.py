from typing import Literal, Optional, TypeVar


class NSEDataGeneric:

    def get_option_chain_analysis(
        self, oc_type: Literal["index", "equity"]
    ) -> "OptionChainType":

        match oc_type:

            case "index":
                return self.option_chain_result("IndexChainType")

            case "equity":
                return (
                    self.option_chain_result("EquityOptionCHainType")
                    if self.is_fno
                    else None
                )

            case _:
                raise KeyError()

    def option_chain_result(self, OptionChain: type):

        option_chain_data = self._nse_config.get_option_chain.get_option_chain(
            self.symbol
        )

        oc_obj = OptionChain(option_chain_data, type="")

        return oc_obj
