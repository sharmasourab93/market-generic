from dataclasses import dataclass
from typing import Dict, List, Union

import pandas as pd

from trade.nse.indices.nse_index import INDICES, NSEIndex
from trade.nse.nse_configs.nse_indices_config import NSEIndexConfig
from trade.nse.nse_generics.all_data_generics import AllDataGenerics
from trade.technicals.indicators import GenericIndicator, MovingAverages, PivotPoints

INDICATOR_IMPLIED_TYPE = Dict[str, GenericIndicator]
REPORT_FORMAT = Dict[str, Union[Dict[str, Union[str, float, list]], Dict[str, str]]]
INDEX_DEFAULT_INDICATORS = {"pivots": PivotPoints, "mas": MovingAverages}
PICKED_COLS = [
    "symbol",
    "pct_change",
    "cpr",
    "cpr_width",
    "EMA20",
    "EMA50",
    "EMA200",
    "pe",
    "Expiry",
    "Max Put OI",
    "PCR at Max",
    "Max Call OI",
    "PCR at Min",
    "Nearest Support",
    "Resistance at",
    "Straddle",
    "Overall PCR",
    "Verdict",
    "Max Put & Call OI at",
]


@dataclass
class SpotIndices(AllDataGenerics):

    dated: str
    _all_ticker_type: str = "index"

    def __post_init__(self):

        self._config = NSEIndexConfig(self.dated)
        self.dated = self._config.working_day.day.as_str
        self.symbols = {i: NSEIndex(i, self.dated) for i in INDICES}
        self.vix = self._config.get_vix()
        self.metrics = self._config.get_index_metrics()

    def __getitem__(self, item: str) -> NSEIndex | None:
        return self.symbols.get(item, None)

    def keys(self):
        return INDICES

    def values(self):
        return self.symbols.values()

    def apply_indicators(
        self,
        gen_indicators: INDICATOR_IMPLIED_TYPE = INDEX_DEFAULT_INDICATORS,
        period: str = "1y",
        interval: str = "1d",
    ) -> Dict[str, Dict[str, float]]:

        symbols = (
            list(self.symbols.values())
            if self._all_ticker_type == "index"
            else self.symbols
        )
        result = dict()

        for symbol in symbols:
            sub_data = symbol.with_indicators(gen_indicators, period, interval)
            result.update({str(symbol): sub_data})

        return result

    def comprehensive_report(self):
        return {
            "index_windic": self.apply_indicators(),
            "vix": self.vix,
            "metrics": self.metrics,
            "adv_dec": self.adv_dec(),
            "fii_dii": self.get_fii_dii_reports(),
        }

    def get_top_bottom(self, top_n: int = 200, n_value: int = 5):

        data = self._get_bhavcopy()
        data = data.loc[data.index <= top_n, :]
        data["pct_change"] = data["pct_change"] * 100
        largest = data.nlargest(n_value, "pct_change")[
            ["symbol", "pct_change"]
        ].to_dict(orient="records")
        smallest = data.nsmallest(n_value, "pct_change")[
            ["symbol", "pct_change"]
        ].to_dict(orient="records")
        return {"top_n": largest, "bottom_n": smallest}

    def comprehensive_report_as_dataframe(self) -> REPORT_FORMAT:
        index_data = pd.DataFrame.from_dict(self.apply_indicators(), orient="index")
        metrics = pd.DataFrame.from_dict(self.metrics, orient="index")
        pivots = pd.json_normalize(index_data.pivots)
        mas = pd.json_normalize(index_data.mas)

        # Merge with Pivots & Moving Averages.
        index_data = pd.concat([index_data.reset_index(), pivots, mas], axis=1).drop(
            ["pivots", "mas"], axis=1
        )
        index_data = pd.concat([index_data, metrics.reset_index()], axis=1).drop(
            "index", axis=1
        )

        # Merge with Vix
        vix = pd.DataFrame(self.vix.items()).set_index(0).transpose()
        index_data = (
            pd.concat([index_data, vix], axis=0).drop("adv-dec", axis=1).fillna("")
        )
        index_data.loc[index_data.symbol == "INDIA VIX", "dated"] = self.dated

        # Merge with Option Chain Data
        option_chain = self.get_option_chain_analysis()
        index_data = pd.merge(index_data, option_chain, on="symbol", how="left").fillna(
            ""
        )

        index_data = index_data[PICKED_COLS]

        return {
            "index": index_data.to_dict(orient="records"),
            "adv_dec": self.adv_dec(),
            "fii_dii": self.get_fii_dii_reports(),
            "top_bottom": self.get_top_bottom(),
        }
