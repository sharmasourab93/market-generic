from datetime import datetime, date
from trade.nse.stocks import AllNSEStocks
from trade.nse.nse_configs import DATE_FMT
from trade.reports import StockReporter, IndexReport


def all_stocks():
    return AllNSEStocks(dated=date.today().strftime(DATE_FMT),
                        nse_top=1000)


def index_reports():
    obj = IndexReport()
    obj.prepare_report()


def stock_reports():
    data = all_stocks()
    obj = StockReporter("swings", data)
    obj.notify_report()


def execute_all_reports():
    index_reports()
    stock_reports()
