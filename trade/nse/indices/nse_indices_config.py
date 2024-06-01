from functools import cache
from typing import Dict, List, Literal, Optional, Union

import pandas as pd

from trade.nse.nse_config import NSEConfig

INDICES = [
    "NIFTY 50",
    "NIFTY BANK",
    "NIFTY FINANCIAL SERVICES",
    "NIFTY NEXT 50",
    "NIFTY MIDCAP 50",
]
INDICES_API = ["NIFTY", "NIFTYNXT50", "FINNIFTY", "BANKNIFTY", "MIDCPNIFTY"]
INDEX_NAME_TYPE = Union[
    Literal["NIFTY 50"],
    Literal["NIFTY BANK"],
    Literal["NIFTY FINANCIAL SERVICES"],
    Literal["NIFTY NEXT 50"],
    Literal["NIFTY MIDCAP 50"],
]
INDIA_VIX = "INDIA VIX"
INVALID_SYMBOL = "Invalid Symbol Chosen."
MODIFIED_INDEX_QUOTE_TYPE = Dict[str, Union[str, Dict[str, str]]]


class NSEIndexConfig(NSEConfig):

    def get_fii_dii_report(self) -> List[Dict[str, str]]:

        url = self.main_domain + self.fii_dii_report
        response = self.get_request_api(url, self.advanced_header)
        # TODO: Handle Exception when Report not updated.
        return self.match_http(response.json(), response.status_code)

    def process_all_indices_data(self, data: pd.DataFrame) -> Dict[str, pd.DataFrame]:

        col_renames = {
            "indexSymbol": "symbol",
            "previousClose": "prev_close",
            "percentChange": "pct_change",
            "yearHigh": "52wk_high",
            "yearLow": "52wk_low",
            "perChange30d": "30d_change",
            "perChange365d": "1yr_change",
            "last": "close",
        }

        data["adv-dec"] = (
            data.advances.fillna(0).astype(str)
            + "-"
            + data.unchanged.fillna(0).astype(str)
            + "-"
            + data.declines.fillna(0).astype(str)
        )
        selected_cols = [
            "key",
            "index",
            "symbol",
            "open",
            "high",
            "low",
            "close",
            "prev_close",
            "pct_change",
            "30d_change",
            "1yr_change",
            "adv-dec",
            "pe",
            "pb",
            "dy",
        ]
        data = data.rename(columns=col_renames)
        data = data.loc[:, selected_cols].replace(str(), 0)
        processed_indices = dict()
        spot_indices_list = INDICES + ["INDIA VIX"]
        excluded_cols = ["index", "key"]
        spot_indices = data.loc[
            data["index"].isin(spot_indices_list),
            [col for col in data.columns if col not in excluded_cols],
        ]
        processed_indices.update({"SPOT": spot_indices})
        processed_indices.update(
            {
                i: data.loc[
                    data.key == i,
                    [col for col in data.columns if col not in excluded_cols],
                ]
                for i in (
                    "SECTORAL INDICES",
                    "STRATEGY INDICES",
                    "THEMATIC INDICES",
                    "FIXED INCOME INDICES",
                )
            }
        )

        return processed_indices

    def get_sectoral_indices(self) -> pd.DataFrame:

        return self.get_all_indices()["SECTORAL INDICES"]

    def get_top_bottom_sectoral_indices(self):

        data = self.get_sectoral_indices()
        # TODO: return top 3 and bottom three sectoral indices.
        # Look for a generic implementation.
        return data

    def get_all_indices(self) -> Dict[str, pd.DataFrame]:

        url = self.main_domain + self.indices
        response = self.get_request_api(url, self.advanced_header)
        data = pd.DataFrame(response.json()["data"])
        data = self.process_all_indices_data(data)
        return data

    @cache
    def get_vix(self) -> Dict[str, str]:

        data = self.get_all_indices()["SPOT"]
        vix = data.loc[data.symbol == INDIA_VIX, :].to_dict(orient="records").pop(0)

        return vix

    @cache
    def get_index_metrics(self) -> Dict[str, Dict[str, str]]:
        """
        Objective is to return
            - Price to Earning,
            - Price to Book
            - Dividend Yield
        For each tradeable index as listed in INDICES.
        """

        data = self.get_all_indices()["SPOT"]
        metrics = [
            data.loc[data.symbol == i, ["pe", "pb", "dy"]].to_dict(orient="records")
            for i in INDICES
        ]
        metrics = [i.pop(0) if len(i) > 0 else {} for i in metrics]

        return dict(zip(INDICES, metrics))

    def get_spot_indices(self) -> pd.DataFrame:
        data = self.get_all_indices()["SPOT"]
        data = data.loc[data.symbol != INDIA_VIX, :]
        return data

    def process_quoted_index(self, data: dict) -> MODIFIED_INDEX_QUOTE_TYPE:
        new_data = dict()
        new_data["symbol"] = data["name"]
        advances = data["advance"]
        new_data["adv-dec"] = (
            str(advances["advances"])
            + "-"
            + str(advances["unchanged"])
            + "-"
            + str(advances["declines"])
        )
        meta_data = data["metadata"]
        new_data["ohlc"] = {
            "open": meta_data["open"],
            "high": meta_data["high"],
            "low": meta_data["low"],
            "close": meta_data["last"],
            "prev_close": meta_data["previousClose"],
            "pct_change": meta_data["percChange"],
            "52wk_high": meta_data["yearHigh"],
            "52wk_low": meta_data["yearLow"],
            "volume": meta_data["totalTradedVolume"],
        }
        new_data["dated"] = data["timestamp"]
        new_data["status"] = data["marketStatus"]["marketStatus"]

        return new_data

    @cache
    def get_quote_index(self, index: INDEX_NAME_TYPE) -> MODIFIED_INDEX_QUOTE_TYPE:

        index = index.upper()
        url = self.main_domain + self.quote_index
        url = url.format(index)

        response = self.get_request_api(url, self.advanced_header)
        response = response.json()

        if response == {}:
            return response

        response = self.process_quoted_index(response)
        return response

    def get_vix_history(self, start: str, end: str):
        """This method gets you history of INDIA VIX from x1 date to x2 date.
        Expecting params
        : start:
        : end:
        to be in %d-%m-%Y format.
        """

        url = self.main_domain + self.vix.format(start, end)
        data = self.get_request_api(url, self.advanced_header).json()

        return data
