from typing import TypeVar, List
from trade.strategies.scan.master import StockSwingScanMaster


Stocks = TypeVar("NSEStocks")
STOCK_LISTS = List[Stocks]


class BigBangVolume(StockSwingScanMaster):
    """
    Strategy 1 - The Big Bang - Trading The Active Ones, The Volume Theory
    Ground Level Strategy:
    1. Daily Price Gain > 5% (Less than this will not indicate volume blast)
    2. Price share being traded must be Rs X minimum
    3. Volume being 10x of daily average & more than prev day volume
    4. If Breakout after Consolidation, Sure shot buy
    5. Fundamental Analysis for the reason of breakout
    6. Broader market must be in an uptrend.

    Entry:
    1. Keep an eye on 1h or 1D candle
    2. Can be followed by 2.5 days of consolidation to a 10, 20 or 50 EMA.
    3. SL at 1%-2% of the capital, can stretch upto 8% if momentum is expected to be big.

    Exit 1:3 Min, if Higher, start pyramiding.
    """

    def __init__(self):
        super().__init__(self.strategy_from_file_name)

    def strategy_filters(self) -> STOCK_LISTS:
        min_pct_change = 5 / 100
        compare = "gt"
        min_volume_diff = 10.0
        _strategy_data = self.filter_by_pct_change(min_pct_change,
                                                   compare)
        filtered_result = [i for i in _strategy_data
                            if i.volume_diff >= min_volume_diff]

        return filtered_result

    def strategy_output(self):
        return self.strategy_filters()
