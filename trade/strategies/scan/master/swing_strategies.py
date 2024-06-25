from trade.nse.stocks import AllNSEStocks
from trade.strategies.scan.master.strategies_generic import StockScanMaster


class StockSwingScanMaster(StockScanMaster):

    def __init__(self, data: AllNSEStocks, strategy_name: str, top: int):
        super().__init__(data, strategy_name, "Swing", top)
