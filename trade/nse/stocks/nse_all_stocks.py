from dataclasses import dataclass
from typing import List, Optional, Any, Union
import asyncio
from trade.nse.nse_configs.nse_config import NSE_TOP
from trade.nse.nse_generics.all_data_generics import AllDataGenerics
from trade.nse.stocks.nse_stock import NSEStock


@dataclass
class AllNSEStocks(AllDataGenerics):

    dated: str
    symbols: Optional[List[str]] = None
    nse_top: Optional[int] = None
    _all_ticker_type: str = "stock"

    def __gt__(self, other: Any) -> "AllNSEStocks":
        return AllNSEStocks(
            dated=self.dated,
            symbols=[i for i in self.symbols if i.pct_change >= other],
            nse_top=self.nse_top
        )

    def __lt__(self, other: Any) -> "AllNSEStocks":
        return AllNSEStocks(dated=self.dated,
                            symbols=[i for i in self.symbols if i.pct_change <= other],
                            nse_top=self.nse_top)

    def __lte__(self, other: Any) -> "AllNSEStocks":
        return self.__lt__(other)

    def __gte__(self, other: Any) -> "AllNSEStocks":
        return self.__gt__(other)

    def __len__(self) -> int:
        return len(self.symbols)

    def __post_init__(self):
        if self.nse_top is None:
            self.nse_top = NSE_TOP

        self.set_config()
        self.dated = self._config.working_day.previous_business_day.as_str
        if self.symbols is None:
            self.symbols = self._config.get_nse_stocks(self.nse_top)
            self.symbols = asyncio.run(self.get_symbols_concurrently(self.symbols))

    async def get_symbols_concurrently(self, symbols: list):

        async def get_nse_stocks(dated: str, symbol:str):
            return NSEStock(dated=dated, symbol=symbol)

        return await asyncio.gather(*[get_nse_stocks(self.dated, symbol)
                                      for symbol in symbols])

    def get_historical_data(self):
        return asyncio.run(self.get_history_concurrently())

    async def get_history_concurrently(self):
        return await asyncio.gather(*[symbol.history for symbol in self.symbols])

    def __getitem__(self, index: int) -> Union["AllNSEStocks", "NSEStock"]:
        if isinstance(index, slice):
            start = index.start if index.start is not None else 0
            stop = index.stop if index.stop is not None else self.nse_top
            step = index.step if index.step is not None else 1
            return AllNSEStocks(dated=self.dated,
                                symbols=self.symbols[start: stop],
                                nse_top=self.nse_top)

        return self.symbols[index]
