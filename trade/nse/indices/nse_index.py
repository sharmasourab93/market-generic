from dataclasses import dataclass

from trade.nse.nse_configs.nse_indices_config import (
    INDEX_NAME_TYPE,
    INDICES,
    INDICES_API,
    INDICES_MAPPING,
    NSEIndexConfig,
)
from trade.nse.nse_generics.data_generics import NSEDataGeneric


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
        ohlc = quotes.pop("ohlc")
        ohlc.update({"prev_volume": 0.0})
        self._set_attributes(ohlc)
        self._set_attributes(quotes)

    @property
    def lot_size(self) -> int:
        return self._config.indices_lot_size[self.symbol]

    @property
    def strike_multiples(self):
        mapped_symbol = INDICES_MAPPING[self.symbol]
        return self._config.get_strike_mul_by_symbol(mapped_symbol, INDICES_API)[
            mapped_symbol
        ]

    @property
    def expiries(self):
        mapped_symbol = INDICES_MAPPING[self.symbol]
        return self._config.get_expiry_by_symbol(mapped_symbol, INDICES_API)
