from abc import abstractmethod
from datetime import date
from trade.strategies.master.strategies_generic import StockStrategyMaster


TOP_STOCKS = 1000
DATE_FMT = "%d-%b-%Y"
TODAY = date.today().strftime(DATE_FMT)


class StockSwingStrategyMaster(StockStrategyMaster):

    def __init__(self, strategy_name:str, dated:str = TODAY, top:int = TOP_STOCKS):
        self.strategy_type = "Swing"
        super().__init__(strategy_name, self.strategy_type, dated, top)
