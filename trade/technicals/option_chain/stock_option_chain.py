from trade.nse.nse_config import NSEConfig
from trade.technicals.option_chain.generic_option_chain import GenericOptionChain


class StockOptionChainAnalysis(GenericOptionChain):
    def __init__(
        self,
        symbol: str,
        oc_data: dict,
        dated: str,
        strike_multiples: dict,
        Config: type = NSEConfig,
    ):
        super().__init__(symbol, oc_data, strike_multiples)
        self._config = Config(dated)

    def get_select_stock_options_bhavcopy(self, symbol: str, expiry: str):
        expiry_set: list = self.get_all_monthly_expiries()
        fo_symbols: list = self._config.get_fno_stocks()
        ce_data, pe_data = self.get_stock_options_bhavcopy()

        if expiry in expiry_set and symbol in fo_symbols:
            ce_data = ce_data.loc[
                (ce_data.Symbol == symbol) & (ce_data.Expiry_dt == expiry), :
            ]
            pe_data = pe_data.loc[
                (pe_data.Symbol == symbol) & (pe_data.Expiry_dt == expiry), :
            ]

            return ce_data.round(2), pe_data.round(2)

        return None

    def stock_option_chain(
        self, symbol: str, delta: int = 5, expiry_delta: int = 1
    ) -> str:
        """
        Stock Option Chain Analysis method.
        :param symbol:
        :param delta:
        :param expiry_delta:
        :return:
        """

        # TODO: Identify ATM Strike based on the underlying value.
        # TODO:

        option_chain, expiry = obj.get_option_chain(symbol, "equity", expiry_delta)

        underlying_value = option_chain["underlying_value"]
        oc_df = option_chain["OptionChain"]

        return option_chain
