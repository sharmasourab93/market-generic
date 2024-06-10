from dataclasses import dataclass

from trade.nse.nse_generics.data_generics import NSEDataGeneric
from trade.nse.nse_configs.nse_indices_config import (
    INDEX_NAME_TYPE,
    INDICES,
    INDICES_API,
    NSEIndexConfig,
    INDICES_MAPPING
)


@dataclass
class NSEIndex(NSEDataGeneric):

    symbol: INDEX_NAME_TYPE
    dated: str
    _ticker_type: str = "index"

    def __post_init__(self):
        self.set_config()
        self.symbol = self.symbol.upper()
        self._yfsymbol = self.yfin_symbol()
        quotes = self._config.get_quote_index(self.symbol)

        for key, value in quotes.items():
            if key not in ("symbol", "dated"):
                setattr(self, key, value)

        self.indicators = self.apply_indicators()

    @property
    def lot_size(self) -> int:
        return self._config.indices_lot_size[self.symbol]

    @property
    def strike_multiples(self):
        mapped_symbol = INDICES_MAPPING[self.symbol]
        return self._config.get_strike_mul_by_symbol(mapped_symbol,
                                                     INDICES_API)[mapped_symbol]

    @property
    def expiries(self):
        mapped_symbol = INDICES_MAPPING[self.symbol]
        return self._config.get_expiry_by_symbol(mapped_symbol,
                                                 INDICES_API)[mapped_symbol]


@dataclass
class SpotIndices:

    dated: str
    _all_ticker_type: str = "index"

    def __post_init__(self):

        self._config = NSEIndexConfig(self.dated)
        self.symbols = {i: NSEIndex(i, self.dated) for i in INDICES}
        self.vix = self._config.get_vix()
        self.metrics = self._config.get_index_metrics()

    def __getitem__(self, item: str) -> NSEIndex | None:
        return self.symbols.get(item, None)

    def get_ohlc(self) -> OHLC_TYPE:

        resulting_dict = dict()
        for sym in self.symbols.values():
            resulting_dict.update(sym.get_ohlc())

        return resulting_dict
