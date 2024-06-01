from abc import ABC
from functools import cache
from typing import Dict, List, Union

MARKET_API_QUOTE_TYPE = Dict[str, Union[list, str, bool]]
INVALID_SYMBOL = "Invalid Symbol Chosen."


class NSEFNO(ABC):

    @cache
    def get_fno_stocks(self) -> List[str]:

        url = self.main_domain + self.derivative_master_list
        data = self.get_request_api(url, self.advanced_header).json()
        return data

    def get_option_chain_data(self, symbol: str) -> MARKET_API_QUOTE_TYPE:
        """Based on symbol extract Option Chain data from NSE API."""

        symbol = symbol.upper()

        if symbol in self.derivative_index_choice:
            url = self.get_option_chain_index(symbol)

        elif symbol in self.get_fno_stocks():
            url = self.get_option_chain_equities(symbol)

        else:
            raise KeyError(INVALID_SYMBOL)

        data = self.get_request_api(url, self.advanced_header).json()

        return data

    def get_option_chain_equities(self, symbol: str) -> str:
        return self.main_domain + self.derivative_option_chain.format(symbol)

    def get_option_chain_index(self, symbol: str) -> str:
        return self.main_domain + self.derivative_option_index.format(symbol)
