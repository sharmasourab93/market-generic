from abc import ABC
from functools import cache, cached_property
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
