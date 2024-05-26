from dataclasses import dataclass, field
from heapq import nlargest, nsmallest
from typing import Dict, List, Optional, Union

from trade.nse.nse_config import DATE_FMT, NSE_TOP, NSEConfig
from trade.nse.nse_stock import NSEStock

ADV_DEC_TYPE = Dict[Union[bool, None], int]
TOP_BOTTOM_TYPE = Dict[str, Dict[str, float]]


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

    def __getitem__(self, item: str) -> str:
        index_ = self.symbols.index(item)
        return self.symbols[index_]

    def get_advance_decline(self) -> ADV_DEC_TYPE:
        return dict(Counter([i.adv_dec for i in self.symbols]))

    def get_top_bottom(self, nos: int = 5, nse_top: int = 200) -> TOP_BOTTOM_TYPE:

        get_tops_bottoms = [
            (i.symbol, i.pct_change, i.diff) for i in self.symbols[:nse_top]
        ]

        top_nos = nlargest(get_tops_bottoms, nos, key=lambda x: x[1])
        top_nos = {key: {"pct_change": v1, "diff": v2} for key, v1, v2 in top_nos}
        small_nos = nsmallest(get_tops_bottoms, nos, key=lambda x: x[1])
        small_nos = {key: {"pct_change": v1, "diff": v2} for key, v1, v2 in small_nos}

        return {"top": top_nos, "bottom": small_nos}
