from typing import List, TypeVar
from trade.nse.stocks import AllNSEStocks
from trade.nse.nse_configs import DATE_FMT
from trade.strategies.scan.master.swing_strategies import StockSwingScanMaster

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

    def __init__(self, data: AllNSEStocks, top: int = None):
        strategy_name = self.strategy_from_file_name(__file__)
        super().__init__(data, strategy_name, top=top)

    def strategy_filters(self) -> STOCK_LISTS:
        min_pct_change = 5
        min_volume_diff = 10.0
        _strategy_data = self.stocks > min_pct_change
        filtered_result = [
            i for i in _strategy_data if i.volume_diff >= min_volume_diff
        ]

        return filtered_result

    def strategy_output(self):
        return self.strategy_filters()


if __name__ == '__main__':
    from time import perf_counter
    from datetime import datetime
    import cProfile
    import pstats

    profilers = cProfile.Profile()
    profilers.enable()
    start = perf_counter()
    today = datetime.today().strftime(DATE_FMT)
    data = AllNSEStocks(dated=today, nse_top=100)
    obj = BigBangVolume(data).strategy_output()
    end = perf_counter()
    ttl = end - start
    print(ttl, ttl / 60)
    profilers.disable()
    pstats.Stats(profilers).sort_stats(pstats.SortKey.CUMULATIVE).print_stats(1000)