from dataclasses import dataclass
from typing import Dict, Literal, Union

from trade.nse.data_generics import NSEDataGeneric
from trade.nse.indices.nse_indices_config import (
    INDEX_NAME_TYPE,
    INDICES,
    NSEIndexConfig,
)

OHLC_TYPE = Dict[str, Dict[str, Union[str, int]]]


@dataclass
class NSEIndex(NSEDataGeneric):

    symbol: INDEX_NAME_TYPE
    dated: str

    def __post_init__(self):
        self.symbol = self.symbol.upper()
        self._config = NSEIndexConfig(self.dated)
        quotes = self._config.get_quote_index(self.symbol)

        for key, value in quotes.items():
            if key not in ("symbol", "dated"):
                setattr(self, key, value)

        self.indicators = self.apply_indicators()

    def get_ohlc(self) -> OHLC_TYPE:

        return {self.symbol: self.ohlc}


@dataclass
class SpotIndices:

    dated: str

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


if __name__ == "__main__":
    obj = SpotIndices("31-May-2024")

    print(obj)
