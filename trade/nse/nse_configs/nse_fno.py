from abc import ABC
from io import BytesIO
from functools import cache, cached_property
from typing import Dict, List, Union
import pandas as pd
from trade.utils.op_utils import timed_lru_cache, find_least_difference_strike

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

    def process_downloaded_mklots(
        self, data: pd.DataFrame
    ) -> Dict[str, Dict[str, str]]:
        data.columns = data.columns.str.strip()
        data.columns = data.columns.str.capitalize()
        data = data.loc[
            ~data.Underlying.str.contains("Derivatives"),
            ~data.columns.isin(["Underlying"]),
        ]
        data = data.apply(lambda x: x.str.strip())

        resulting_dict = {
            data_value["Symbol"]: {
                k: v for k, v in data_value.to_dict().items() if v != str()
            }
            for iter, data_value in data.iterrows()
        }

        return resulting_dict

    @cached_property
    def get_fo_mktlots(self) -> Dict[str, Dict[str, str]]:

        data = self.get_request_api(self.fo_mklots["url"], self.simple_headers).content

        # Since data is a csv object, we read the bytes into a dataframe.
        data = pd.read_csv(BytesIO(data))
        data = self.process_downloaded_mklots(data)

        return data

    def get_ticker_folots(self, ticker: str, month: str) -> int:

        if ticker in self.get_fo_mktlots.keys():
            data = self.get_fo_mktlots[ticker]

            if month in data.keys():
                return int(data[month])

        raise KeyError(f"{ticker} or {month} not in NSE FO Lots List.")

    @timed_lru_cache(seconds=300)
    def get_derivative_quote(self, symbol: str) -> dict:

        url = self.main_domain + self.quote_derivative.format(symbol)

        response = self.get_request_api(url, self.advanced_header).json()

        return response

    def strike_multiples(self) -> Dict[str, int]:
        strike_muls = dict()
        for stocks in self.get_fno_stocks():
            strike_price = sorted(list(set(self.get_derivative_quote(stocks)[
                                           "strikePrices"])))
            strike_muls.update({stocks: find_least_difference_strike(strike_price)})

        return strike_muls

    def get_expiries(self) -> Dict[str, Dict[str, str]]:

        expiries = dict()

        for symbol in self.get_fno_stocks():
            symbol_expiry = self.get_derivative_quote(symbol)["expiryDatesByInstrument"]
            symbol_expiry["fut_expiry"] = symbol_expiry.pop("Stock Futures")
            symbol_expiry["opt_expiry"] = symbol_expiry.pop("Stock Options")

            expiries.update({symbol: symbol_expiry})

        return expiries

    def get_strike_mul_by_symbol(self, symbol: str,
                                 symbol_list: List[str] = None) -> Dict[str, int]:

        if symbol_list is None:
            symbol_list = self.get_fno_stocks()

        if symbol in symbol_list:
            strike_price = sorted(list(set(self.get_derivative_quote(symbol)[
                                               "strikePrices"])))
            return {symbol: find_least_difference_strike(strike_price)}

        raise KeyError("Invalid Symbol not found.")

    def get_expiry_by_symbol(self, symbol: str, symbol_list: List[str] = None) -> Dict[str, Dict[str, str]]:

        if symbol_list is None:
            symbol_list = self.get_fno_stocks()
            key = "Stock"
        else:
            key = "Index"

        if symbol in symbol_list:
            expiries = self.get_derivative_quote(symbol)["expiryDatesByInstrument"]
            expiries["fut_expiry"] = expiries.pop(f"{key} Futures")
            expiries["opt_expiry"] = expiries.pop(f"{key} Options")

            return {symbol: expiries}

        raise KeyError("Invalid symbol not found.")
