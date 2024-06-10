from dataclasses import dataclass
from functools import cached_property
from typing import Dict, List, Optional, Union
from warnings import simplefilter

import pandas as pd

from trade.nse.nse_generics.data_generics import NSEDataGeneric


MARKET_API_QUOTE_TYPE = Dict[str, Union[list, str, bool]]
simplefilter(action="ignore", category=pd.errors.SettingWithCopyWarning)
simplefilter(action="ignore", category=RuntimeWarning)


@dataclass
class NSEStock(NSEDataGeneric):
    symbol: str
    dated: str
    tf: Optional[str] = "1d"
    _ticker_type: str = "stock"

    def __post_init__(self):
        self.set_config()
        self.symbol = self.symbol.upper()
        self._yfsymbol = self.yfin_symbol()
        self.get_curr_bhav()

    @property
    def lot_size(self) -> Optional[int]:
        if self.is_fno:
            month_year = self._config.working_day.as_month_year
            return self._config.get_ticker_folots(self.symbol, month_year)

        return None

    @property
    def strike_multiples(self) -> int:
        if self.is_fno:
            return self._config.get_strike_mul_by_symbol(self.symbol)
        return None

    @cached_property
    def expiries(self) -> List[str]:
        if self.is_fno:
            return self._config.get_expiry_by_symbol(self.symbol)
        return None

    @property
    def is_fno(self) -> bool:
        return self.symbol in self._config.get_fno_stocks()

    @cached_property
    def get_meta_data(self) -> MARKET_API_QUOTE_TYPE:
        return self._config.get_equity_meta(self.symbol)

    @property
    def adv_dec(self):

        match self.price_diff:

            case self.price_diff if self.price_diff > 0:
                return True

            case self.price_diff if self.price_diff < 0:
                return False

            case _:
                return None
