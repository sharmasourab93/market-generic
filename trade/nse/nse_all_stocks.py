from dataclasses import dataclass, field
from heapq import nlargest, nsmallest
from typing import Dict, List, Optional, Union

from trade.nse.nse_config import DATE_FMT, NSE_TOP, NSEConfig
from trade.nse.nse_stock import NSEStock


@dataclass
class AllNSEStocks:

    dated: str
    symbols: Optional[List[str]] = None
    nse_top: Optional[int] = NSE_TOP

    def __len__(self):
        return len(self.symbols)

    def __post_init__(self):
        self._nse_config = NSEConfig(self.dated)
        if self.symbols is None:
            self.symbols = self._nse_config.get_nse_stocks(self.nse_top)

        self.symbols = [NSEStock(i, self.dated) for i in self.symbols]

    def __getitem__(self, index: int) -> str:
        if isinstance(index, slice):
            start = index.start if index.start is not None else 0
            stop = index.stop if index.stop is not None else 0
            step = index.step if index.step is not None else 1
            return [self.symbols[i] for i in range(start, stop, step)]

        return self.symbols[index]
