from typing import Union
from trade.nse.nse_configs.nse_config import NSEConfig
from trade.nse.nse_configs.nse_indices_config import INDICES
from trade.technicals.option_chain.index_option_chain import IndexOptionChainAnalysis
from trade.technicals.option_chain.stock_option_chain import StockOptionChainAnalysis


OptionChainAnalysisType = Union[IndexOptionChainAnalysis, StockOptionChainAnalysis]


class OptionChain:

    @classmethod
    def analyze_option_chain(cls,
                             symbol: str,
                             dated: str,
                             data: dict,
                             lot_size: int,
                             strike_multiples: Union[float, int]) -> \
            OptionChainAnalysisType:

        if symbol in INDICES:

            return IndexOptionChainAnalysis.analyze_option_chain(symbol, dated, data,
                                                                 lot_size,
                                                                 strike_multiples)

        else:
            return StockOptionChainAnalysis.analyze_option_chain(symbol, dated, data,
                                                                 lot_size,
                                                                 strike_multiples)


if __name__ == '__main__':
    oc_data = NSEConfig("12-Jun-2024").get_option_chain_data("RELIANCE")
    args = ("RELIANCE", "12-Jun-2024", oc_data, 15, 100)

    option_chain = OptionChain.analyze_option_chain(*args)
    result = option_chain.option_chain_output()
