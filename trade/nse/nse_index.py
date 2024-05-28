from typing import Literal, Dict, Union
from dataclasses import dataclass, field
from trade.nse.nse_indices_config import NSEIndexConfig, INDICES


# TODO: Insert Option Chain Analysis Logic.

@dataclass
class NSEIndex:

    symbol: Literal[*INDICES]
    dated: str

    def __post_init__(self):
        self._config = NSEIndexConfig(self.dated)
        quotes = self._config.get_quote_index(self.symbol)

        for key, value in quotes.items():
            if key not in ("symbol", "dated"):
                setattr(self, key, value)


@dataclass
class SpotIndices:

    dated: str

    def __post_init__(self):

        self._config = NSEIndexConfig(self.dated)
        self.symbols = [NSEIndex(i, self.dated) for i in INDICES]
        self.vix = self._config.get_vix()
        self.metrics = self._config.get_index_metrics()
