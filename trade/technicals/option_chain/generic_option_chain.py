from abc import ABC, abstractmethod
from math import ceil
from typing import Dict, Literal, Optional, Tuple, Union

import pandas as pd
from numpy import inf
from pandas import DataFrame, json_normalize

from trade.utils.utility_enabler import UtilityEnabler

PCR_VERDICT_RANGE = {
    (0, 0.4): "Over Sold",
    (0.4, 0.6): "Very Bearish",
    (0.6, 0.8): "Bearish",
    (0.8, 1.0): "Mildly Bullish",
    (1.0, 1.2): "Bullish",
    (1.2, 1.5): "Very Bullish",
    (1.5, float("inf")): "Over Bought",
}

STRIKE_TYPE = Union[float, int]
STRIKE_MULTIPLES_NOT_SET = "Strike Multiples  NOTSET."
VERDICT_RANGE_TYPE = Dict[Tuple[float, float], str]
OPTION_ANALYSIS_FOR = "Option Chain Analysis for {0}"
NO_SUPPORT = "Very little to no support. Reversal possible."
NOT_MANY_RESISTANCE = "Not many resistances. Reversal possible."
QUOTE_OPTION_CHAIN_COLS = [
    "openInterest",
    "changeinOpenInterest",
    "pchangeinOpenInterest",
    "totalTradedVolume",
    "impliedVolatility",
    "lastPrice",
    "change",
    "pChange",
    "totalBuyQuantity",
    "totalSellQuantity",
    "bidQty",
    "bidprice",
    "askQty",
    "askPrice",
]
OPTION_CHAIN_OUTPUT = Dict[
    str, Union[Dict[str, Union[str, int, float]], str, int, float]
]


class GenericOptionChain(ABC):
    __metaclass__ = UtilityEnabler

    @classmethod
    def analyze_option_chain(cls, *args, **kwargs):
        return cls(*args, **kwargs)

    def __init__(
        self,
        symbol: int,
        dated: str,
        oc_data: dict,
        lot_size: int,
        strike_multiple: Union[float, int],
        expiry: Literal[0, 1] = 0,
        delta: int = 5,
    ):
        self.symbol = symbol
        self.dated = dated
        self.records = oc_data["records"]
        self.filtered = oc_data["filtered"]
        self.lot_size = lot_size
        self.underlying = self.records.pop("underlyingValue")
        self.last_updated = self.records.pop("timestamp")
        self.delta = delta
        self.net_oi = {"CE": self.filtered.pop("CE"), "PE": self.filtered.pop("PE")}
        self._extract_data(oc_data, expiry)
        self._get_strike_multiples(strike_multiple)

    def _get_strike_multiples(self, strike_multiple) -> None:
        if strike_multiple is None:
            raise ValueError(STRIKE_MULTIPLES_NOT_SET)
        self.strike_multiple = strike_multiple

    def _all_expiry_dates(self, oc_data) -> None:
        self.expiry = oc_data["records"].get("expiryDates", None)

        if self.expiry is None:
            raise ValueError("Expiry not found.")

    def _curr_expiry(self, oc_data, expiry) -> None:
        self._all_expiry_dates(oc_data)
        self._curr_expiry = self.expiry[expiry]

    def _extract_data(self, oc_data, expiry) -> None:
        self._curr_expiry(oc_data, expiry)
        data = oc_data["records"].get("data")
        data = DataFrame(json_normalize(data))
        self.data = data.loc[(data.expiryDate == self._curr_expiry), :]
        self.data.set_index("strikePrice", inplace=True)

        if self.data.empty:
            raise ValueError(f"No Data for found for Expiry: {self._curr_expiry}.")

    def _available_strikes(self, oc_data) -> None:
        self.available_strikes = oc_data["records"].get("strikePrices")

    def pcr_verdict(
        self, pcr: float, verdict_range: VERDICT_RANGE_TYPE = PCR_VERDICT_RANGE
    ) -> str:
        """Based on the provided pcr, returns a Verdict."""

        for limits, classification in verdict_range.items():
            lower_limit, upper_limit = limits

            if lower_limit <= pcr < upper_limit:
                return classification

        return "Invalid"

    def _maintain_calls_puts(self, df, prefix: Literal["CE", "PE"]):
        df = df.loc[:, df.columns.str.match(f"^({prefix}|expiryDate)")]
        df.columns = df.columns.str.replace(rf"{prefix}.", "")
        df = df[QUOTE_OPTION_CHAIN_COLS].round(2)
        df.columns = ["{0}_{1}".format(prefix, cols) for cols in df.columns]
        df.reset_index(inplace=True)
        return df

    def get_processed_option_chain(self) -> Union[dict, None]:
        """
        Method to process Option Chain for a select symbol and
        selected expiry into algo_trade module consumable format.
        The Data Structure has hard coded values as in the data received
        from NSE officially.
        """
        df = self.data
        # Common Columns
        columns = QUOTE_OPTION_CHAIN_COLS

        options = ["Calls", "Puts"]

        ce_data = self._maintain_calls_puts(df, "CE")
        pe_data = self._maintain_calls_puts(df, "PE")

        # Merge Call & Put data.
        merged_call_put = pd.merge(ce_data, pe_data, on="strikePrice", how="left")

        # Put Call Ration calculation.
        merged_call_put["pcr_oi"] = (
            merged_call_put.PE_openInterest / merged_call_put.CE_openInterest
        )
        merged_call_put["pcr_oi"] = merged_call_put.pcr_oi.replace(inf, 10.0)
        merged_call_put.loc[merged_call_put.pcr_oi >= 10, "pcr_oi"] = 10.0

        return merged_call_put.round(2)

    @property
    def overall_pcr(self) -> float:
        return round(self.net_oi["PE"]["totOI"] / self.net_oi["CE"]["totOI"], 2)

    def get_support_or_resistance(
        self, call_put_max, min_max_pcr, strike_price
    ) -> dict:
        result_dict = dict()

        if len(call_put_max) == 2:

            support = min_max_pcr.loc[
                (min_max_pcr.strikePrice < strike_price)
                & ((min_max_pcr.pcr_oi <= 2) & (min_max_pcr.pcr_oi >= 0.8)),
                :,
            ]

            resistance = min_max_pcr.loc[
                (min_max_pcr.strikePrice >= strike_price)
                & ((min_max_pcr.pcr_oi < 0.8) & (min_max_pcr.pcr_oi >= 0.1)),
                :,
            ]

            resistance = min_max_pcr.loc[
                (min_max_pcr.CE_openInterest == min_max_pcr.CE_openInterest.max()),
                :,
            ]

            if 0 not in support.shape:
                if 1 in support.shape:
                    result_dict.update(
                        {"Nearest Support": int(support.strikePrice.iloc[0])}
                    )

                else:
                    result_dict.update(
                        {
                            "Nearest Support": ",".join(
                                map(str, support.strikePrice.to_list()[::-1])
                            )
                        }
                    )
            else:
                result_dict.update({"Nearest Support": NO_SUPPORT})

            if 0 not in resistance.shape:
                if 1 in resistance.shape:
                    result_dict.update(
                        {"Resistance at": int(resistance.strikePrice.iloc[0])}
                    )

                else:
                    result_dict.update(
                        {
                            "Resistance at": ", ".join(
                                map(str, resistance.strikePrice.to_list())
                            )
                        }
                    )

            else:
                result_dict.update({"Resistance at": NOT_MANY_RESISTANCE})

        else:
            call_put_max = call_put_max[0]

            support = min_max_pcr.loc[(min_max_pcr.strikePrice < strike_price), :]
            support = int(
                support.loc[
                    (support.PE_openInterest == support.PE_openInterest.max()), :
                ].strikePrice.iloc[0]
            )
            resistance = min_max_pcr.loc[min_max_pcr.strikePrice > strike_price, :]
            resistance = int(
                resistance.loc[
                    (resistance.CE_openInterest == resistance.CE_openInterest.max()),
                    :,
                ].strikePrice.iloc[0]
            )
            result_dict.update({"Support at: ": support, "Resistance at: ": resistance})

        return result_dict

    def get_max_put_call_oi(self, call_put_max):

        if len(call_put_max) == 2:

            return {
                "Max Put OI": call_put_max[0]["strikePrice"],
                "PCR at Max": call_put_max[0]["pcr_oi"],
                "Max Call OI": call_put_max[1]["strikePrice"],
                "PCR at Min": call_put_max[1]["pcr_oi"],
            }

        else:
            call_put_max = call_put_max[0]

            return {
                "Max Put & Call OI at": (
                    call_put_max["strikePrice"],
                    call_put_max["pcr_oi"],
                )
            }

    def conditional_straddle_identification(
        self,
        option_chain_dict: Union[dict, list, tuple],
        avg_ce_volume,
        avg_pe_volume,
        left_limit: float = 0.8,
        right_limit: float = 1.2,
    ):

        if isinstance(option_chain_dict, list) or isinstance(option_chain_dict, tuple):

            straddle = [
                self.identify_straddle(
                    i, avg_ce_volume, avg_pe_volume, left_limit, right_limit
                )
                for i in option_chain_dict
            ]
            return ",".join([i for i in straddle if i != ""])

        else:
            return self.identify_straddle(
                call_put_max, avg_ce_volume, avg_pe_volume, left_limit, right_limit
            )

    def identify_straddle(
        self,
        option_chain_dict: dict,
        avg_ce_volume: float,
        avg_pe_volume: float,
        left_limit: float,
        right_limit: float,
    ) -> str:
        """
        Method to identify Straddles from the given dictionary.
        The condition is as follows:

        1. If (Left Limit <= PCR <= Right Limit
                or
              left Limit <= price_pe_by_ce <= Right limit)
              and
              ((Call Traded Volume > Avg Call Volumes) and
              (Put Traded Volume > Avg Put Traded Volumes)):
              We identify the strddle.

        2. Else
            Returns Empty string.
        """

        str_result = str()

        if option_chain_dict["CE_askPrice"] == 0:
            price_pe_by_ce = 0

        else:
            price_pe_by_ce = (
                option_chain_dict["PE_askPrice"] / option_chain_dict["CE_askPrice"]
            )
        pcr = option_chain_dict["pcr_oi"]

        condition_1 = (left_limit <= pcr <= right_limit) or (
            left_limit <= price_pe_by_ce <= right_limit
        )
        condition_2 = (option_chain_dict["CE_totalTradedVolume"] > avg_ce_volume) and (
            option_chain_dict["PE_totalTradedVolume"] > avg_pe_volume
        )

        if condition_1 and condition_2:
            str_result = "Straddles written at {0}.\n".format(
                option_chain_dict["strikePrice"]
            )

            return str_result

        return ""

    @property
    def strike_price(self) -> STRIKE_TYPE:
        return ceil(self.underlying / self.strike_multiple) * self.strike_multiple

    @property
    def strike_min(self) -> STRIKE_TYPE:
        return self.strike_price - (self.strike_multiple * self.delta)

    @property
    def strike_max(self) -> STRIKE_TYPE:
        return (
            self.strike_price
            + (self.strike_multiple * self.delta)
            + self.strike_multiple
        )

    @property
    def strike_range(self) -> range:
        return range(self.strike_min, self.strike_max, self.strike_multiple)

    def extract_data_near_strike(self, data: pd.DataFrame) -> dict:
        result = {}
        data = data.loc[data.strikePrice.isin(self.strike_range), :]
        for i, j in data.iterrows():
            sub_result = {
                "puts_oi": int(j["PE_openInterest"]),
                "calls_oi": int(j["CE_openInterest"]),
                "pcr": float(j["pcr_oi"]),
                "ce_ltp": float(j["CE_lastPrice"]),
                "pe_ltp": float(j["PE_lastPrice"]),
            }
            result.update({j["strikePrice"]: sub_result})

        return result

    def option_chain_output(self) -> OPTION_CHAIN_OUTPUT:
        oc_df = self.get_processed_option_chain()
        analysis_range = self.strike_multiple * self.delta

        analysis_range = list(
            range(
                int(self.strike_price - analysis_range),
                int(self.strike_price + analysis_range),
                int(analysis_range / self.delta),
            )
        )

        # Identify Max Call & Put OI. Can give 2 records or give 1 record.
        call_put_max = oc_df.loc[
            (oc_df.CE_openInterest == oc_df.CE_openInterest.max())
            | (oc_df.PE_openInterest == oc_df.PE_openInterest.max()),
            :,
        ].to_dict(orient="records")

        # This section only covers most liquid and actively trade options in
        # the option chain. The OI values are roughly between 0.1 and 10.
        around_strike = self.extract_data_near_strike(oc_df)
        min_max_pcr = oc_df.loc[(0.1 <= oc_df.pcr_oi) & (oc_df.pcr_oi < 10), :]

        avg_pe_volume = round(float(min_max_pcr.PE_openInterest.mean()), 2)
        avg_ce_volume = round(float(min_max_pcr.CE_openInterest.mean()), 2)

        result_dict = {"symbol": self.symbol, "Expiry": self._curr_expiry}

        # If we have 2 items in the Option chain with Max Calls and Max Puts.
        # We will have two strikes to identify and also mention Supports and
        # lower levels and resistances at higher levels.
        # Else:
        # We have situation where there are enough straddles to be looked at
        # with very little resistance and support within active/liquid strikes.
        result_dict.update(self.get_max_put_call_oi(call_put_max))
        result_dict.update(
            self.get_support_or_resistance(call_put_max, min_max_pcr, self.strike_price)
        )
        result_dict.update(
            {
                "near_strike_info": around_strike,
                "Straddle": self.conditional_straddle_identification(
                    call_put_max, avg_ce_volume, avg_pe_volume
                ),
                "Overall PCR": self.overall_pcr,
                "Verdict": self.pcr_verdict(self.overall_pcr),
            }
        )

        return result_dict
