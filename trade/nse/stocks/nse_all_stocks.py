from dataclasses import dataclass
from typing import List, Optional

from trade.nse.nse_configs.nse_config import NSE_TOP
from trade.nse.nse_generics.all_data_generics import AllDataGenerics
from trade.nse.stocks.nse_stock import NSEStock


@dataclass
class AllNSEStocks(AllDataGenerics):

    dated: str
    symbols: Optional[List[str]] = None
    nse_top: Optional[int] = NSE_TOP
    _all_ticker_type: str = "stock"

    def __gt__(self, other: Any) -> "AllNSEStocks":
        return self.__class__(
            dated=self.dated,
            symbol=[i for i in self.symbols if i.pct_change >= other])

    def __lt__(self, other: Any) -> "AllNSEStocks":
        return self.__class__(dated=self.dated,
                              symbol=[i for i in self.symbols if i.pct_change <= other])

    def __lte__(self, other: Any) -> "AllNSEStocks":
        return self.__lt__(other)

    def __gte__(self, other: Any) -> "AllNSEStocks":
        return self.__gt__(other)

    def __len__(self) -> int:
        return len(self.symbols)

    def __post_init__(self):
        self.set_config()
        self.dated = self._config.working_day.previous_business_day.as_str
        if self.symbols is None:
            self.symbols = self._config.get_nse_stocks(self.nse_top)

            self.symbols = [NSEStock(i, self.dated) for i in self.symbols]

    def __getitem__(self, index: int) -> str:
        if isinstance(index, slice):
            start = index.start if index.start is not None else 0
            stop = index.stop if index.stop is not None else 0
            step = index.step if index.step is not None else 1
            return [self.symbols[i] for i in range(start, stop, step)]

        return self.symbols[index]
