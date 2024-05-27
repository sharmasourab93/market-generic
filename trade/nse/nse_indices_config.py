import pandas as pd
from typing import List, Dict, Optional, Literal, Union
from trade.nse.nse_config import NSEConfig

INDICES = ["NIFTY 50", "NIFTY BANK", "NIFTY FINANCIAL SERVICES", "NIFTY NEXT 50", "NIFTY MIDCAP 50"]
INDICES_API = ["NIFTY", "NIFTYNXT50", "FINNIFTY", "BANKNIFTY", "MIDCPNIFTY"]
INDEX_NAME_TYPE = Union[Literal[*INDICES]]

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
            "last": "close"
        }

        data["adv-dec"] = data.advances.fillna(0).astype(str) \
                              + "-" \
                              + data.unchanged.fillna(0).astype(str) \
                              + "-" \
                              + data.declines.fillna(0).astype(str)
        selected_cols = ["key", "index", "symbol",
                         "open", "high", "low", "close", "prev_close",
                         "pct_change", "30d_change", "1yr_change",
                         "adv-dec", "pe", "pb", "dy", ]
        data = data.rename(columns=col_renames)
        data = data.loc[:, selected_cols].replace(str(), 0)
        processed_indices = dict()
        spot_indices_list = INDICES + ["INDIA VIX"]
        excluded_cols = ["index", "key"]
        spot_indices = data.loc[data["index"].isin(spot_indices_list), [col for col in data.columns if col not in excluded_cols]]
        processed_indices.update({"SPOT": spot_indices})
        categories = ("SECTORAL INDICES", "STRATEGY INDICES", "THEMATIC INDICES",
                      "FIXED INCOME INDICES")
        processed_indices.update({
            i: data.loc[data.key == i, [col for col in data.columns if col not in excluded_cols]] for i in categories
        })

        return processed_indices

    def get_all_indices(self) -> Dict[str, pd.DataFrame]:

        url = self.main_domain + self.indices
        response = self.get_request_api(url, self.advanced_header)
        data = pd.DataFrame(response.json()["data"])
        data = self.process_all_indices_data(data)
        return data

    def get_spot_indices(self) -> pd.DataFrame:

        return self.get_all_indices()["SPOT"]

    def process_quoted_index(self, data: dict) -> MODIFIED_INDEX_QUOTE_TYPE:
        new_data = dict()
        new_data["symbol"] = data["name"]
        advances = data["advance"]
        new_data["adv-dec"] = str(advances["advances"]) \
                              + "-" \
                              + str(advances["unchanged"]) \
                              + "-" \
                              + str(advances["declines"])
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
            "volume": meta_data["totalTradedVolume"]
        }
        new_data["dated"] = data["timestamp"]
        new_data["status"] = data['marketStatus']['marketStatus']

        return new_data

    def get_quote_index(self, index: INDEX_NAME_TYPE) -> MODIFIED_INDEX_QUOTE_TYPE:

        index = index.upper()
        url = self.main_domain + self.quote_index
        url = url.format(index)

        response = self.get_request_api(url, self.advanced_header)
        response = response.json()

        response = self.process_quoted_index(response)
        return response
