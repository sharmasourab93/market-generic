from trade.nse.indices.nse_indices_config import INDICES, NSEIndexConfig
from trade.technicals.option_chain.generic_option_chain import GenericOptionChain

WEEKLY_EXPIRY = (3, 2, 1, 9999, 0)
INDICES_WEEKLY_EXPIRY = {index: expiry for index, expiry in zip(INDICES, WEEKLY_EXPIRY)}
INDICES_FREQUENCY = {
    i: ("Weekly" if INDICES != "NIFTY NEXT 50" else "Monthly", INDICES_WEEKLY_EXPIRY[i])
    for i in INDICES
}


class IndexOptionChainAnalysis(GenericOptionChain):

    def __init__(
        self,
        symbol: str,
        oc_data: dict,
        dated: str,
        strike_multiples: dict,
        Config: type = NSEIndexConfig,
    ):

        super().__init__(symbol, oc_data, strike_multiples)
        self._config = Config(dated)

    def index_option_chain_analysis(
        self, symbol: str, expiry_day: int, delta: int = 5, expiry_delta: int = 1
    ) -> str:

        option_chain = self.get_option_chain()
        underlying_value = option_chain["underlying_value"]
        oc_df = option_chain["OptionChain"]

        strike_price = self.get_strike_price(symbol, underlying_value)
        analysis_range = self.strike_multiples[symbol] * delta

        analysis_range = list(
            range(
                int(strike_price - analysis_range),
                int(strike_price + analysis_range),
                int(analysis_range / delta),
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
        min_max_pcr = oc_df.loc[(0.1 <= oc_df.pcr_oi) & (oc_df.pcr_oi < 10), :]

        avg_pe_volume = round(float(min_max_pcr.PE_openInterest.mean()), 2)
        avg_ce_volume = round(float(min_max_pcr.CE_openInterest.mean()), 2)

        result_dict = {"symbol": symbol, "Expiry": expiry_date}

        # If we have 2 items in the Option chain with Max Calls and Max Puts.
        # We will have two strikes to identify and also mention Supports and
        # lower levels and resistances at higher levels.
        # Else:
        # We have situation where there are enough straddles to be looked at
        # with very little resistance and support within active/liquid strikes.
        result_dict.update(self.get_max_put_call_oi(call_put_max))
        result_dict.update(
            self.get_support_or_resistance(call_put_max, min_max_pcr, strike_price)
        )
        result_dict.update(
            {
                "Straddle": self.conditional_straddle_identification(
                    call_put_max, avg_ce_volume, avg_pe_volume
                )
            }
        )
        result_dict.update(
            {
                "Overall PCR": option_chain["overall_pcr"],
                "Verdict": option_chain["pcr_verdict"],
            }
        )

        return result_dict
