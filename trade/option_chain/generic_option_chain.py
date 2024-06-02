from abc import ABC, abstractmethod
from typing import Dict, Literal, Optional, Tuple, Union

import pandas as pd
from pandas import DataFrame, json_normalize

from trade.nse.indices.nse_indices_config import NSEIndexConfig
from trade.nse.nse_config import NSEConfig
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


class GenericOptionChain(ABC):
    __metaclass__ = UtilityEnabler

    def __init__(
        self,
        symbol: int,
        oc_data: dict,
        dated: str,
        strike_multiples: Optional[dict] = None,
    ):
        self.data = oc_data

        if strike_multiples is None:
            raise ValueError(STRIKE_MULTIPLES_NOT_SET)

        self.strike_multiples = strike_multiples

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
        df = df[columns].round(2)
        df.columns = "{0}_{1}".format(prefix, df.columns)
        df.reset_index(inplace=True)
        return df

    def get_option_chain(self) -> Union[dict, None]:
        """
        Method to process Option Chain for a select symbol and
        selected expiry into algo_trade module consumable format.
        The Data Structure has hard coded values as in the data received
        from NSE officially.
        """
        data = self.data
        records = data["records"]
        filtered = data["filtered"]
        all_expiries: list = records["expiryDates"]
        last_updated: str = records["timestamp"]
        strike_prices: list = records["strikePrices"]
        underlying: float = records["underlyingValue"]

        # Creating A Respone
        response = dict()
        response.update(
            {
                "symbol": symbol,
                "selected_expiry": expiry,
                "all_expiries": all_expiries,
                "last_updated": last_updated,
                "strikes": strike_prices,
                "underlying_value": underlying,
            }
        )

        # DataFrame Operations Section.
        df = DataFrame(json_normalize(data["records"]["data"]))
        df = df.loc[(df.expiryDate == expiry), :]

        if 0 in df.shape:
            return None

        df.set_index("strikePrice", inplace=True)

        # Common Columns
        columns = QUOTE_OPTION_CHAIN_COLS

        options = ["Calls", "Puts"]

        ce_data = self._maintain_calls_puts(ce_data, "CE")
        pe_data = self._maintain_calls_puts(pe_data, "PE")

        # Merge Call & Put data.
        merged_call_put = pd.merge(ce_data, pe_data, on="strikePrice", how="left")

        # Put Call Ration calculation.
        merged_call_put["pcr_oi"] = (
            merged_call_put.PE_openInterest / merged_call_put.CE_openInterest
        )
        merged_call_put["pcr_oi"] = merged_call_put.pcr_oi.replace(inf, 10.0)
        merged_call_put.loc[merged_call_put.pcr_oi >= 10, "pcr_oi"] = 10.0
        overall_pcr = round((filtered["PE"]["totOI"] / filtered["CE"]["totOI"]), 2)
        pcr_verdict = self.pcr_verdict(overall_pcr)

        # Updating the final response.
        response.update(
            {
                "OptionChain": merged_call_put.round(2),
                "ResponseGenerateTime": datetime.now(tz=TIME_ZONE),
                "overall_pcr": overall_pcr,
                "pcr_verdict": pcr_verdict,
            }
        )

        return response

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
                "PCR": call_put_max[0]["pcr_oi"],
                "Max Call OI": call_put_max[1]["strikePrice"],
                "Max PCR OI": call_put_max[1]["pcr_oi"],
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

    def get_strike_price(self, symbol: str, underlying: float) -> int:
        # TODO: Needs to be extended for stock prices of varying range.
        multiple = self.strike_multiples[symbol]
        strike_price = ceil(underlying / multiple) * multiple

        return strike_price

    @abstractmethod
    def option_chain_output(self):

        NotImplementedError("Yet to be implemented.")
