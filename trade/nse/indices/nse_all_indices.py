from dataclasses import dataclass

from trade.nse.indices.nse_index import INDICES, NSEIndex
from trade.nse.nse_configs.nse_indices_config import NSEIndexConfig
from trade.nse.nse_generics.all_data_generics import AllDataGenerics


@dataclass
class SpotIndices(AllDataGenerics):

    dated: str
    _all_ticker_type: str = "index"

    def __post_init__(self):

        self._config = NSEIndexConfig(self.dated)
        self.symbols = {i: NSEIndex(i, self.dated) for i in INDICES}
        self.vix = self._config.get_vix()
        self.metrics = self._config.get_index_metrics()

    def __getitem__(self, item: str) -> NSEIndex | None:
        return self.symbols.get(item, None)
