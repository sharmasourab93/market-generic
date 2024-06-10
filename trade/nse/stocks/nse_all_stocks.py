from dataclasses import dataclass
from typing import List, Optional

from trade.nse.nse_configs.nse_config import NSE_TOP
from trade.nse.stocks.nse_stock import NSEStock
from trade.nse.nse_generics.all_data_generics import AllDataGenerics


@dataclass
class AllNSEStocks(AllDataGenerics):

    dated: str
    symbols: Optional[List[str]] = None
    nse_top: Optional[int] = NSE_TOP
    _all_ticker_type: str = "stock"

    def __len__(self):
        return len(self.symbols)

    def __post_init__(self):
        self.set_config()
        if self.symbols is None:
            self.symbols = self._config.get_nse_stocks(self.nse_top)

            self.symbols = [NSEStock(i, self.dated) for i in self.symbols]

    def __getitem__(self, index: int) -> str:
        if isinstance(index, slice):
            start = index.start if index.start is not None else 0
            stop = index.stop if index.stop is not None else 0
            step = index.step if index.step is not None else 1
            return [self.symbols[i] for i in range(start, stop, step)]

        return self.symbols[index - 1]
