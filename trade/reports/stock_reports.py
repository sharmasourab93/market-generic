from trade.nse.nse_configs import DATE_FMT
from trade.nse.stocks import AllNSEStocks
from trade.strategies.scan import ScanStocks
from trade.utils.notify import Notifier

STRATEGIES = {
    "swings": {"top": 1000},
    "btst": {"top": 500},
    "positional": {"top": 1000},
}


class StockReporter:

    def __init__(self, strategy: str, data):
        self.strategy = strategy
        self.strategy_params = STRATEGIES[strategy]
        self.strategy_params.update({"data": data})

    def execute_report(self) -> Dict[str, List[AllNSEStocks]]:

        return ScanStocks.execute_scans(self.strategy, **self.strategy_params)

    def notify_report(self) -> None:

        result = self.execute_report()
        for name, data in result.items():
            strategy_text = self.strategy.capitalize() + "-" + name

            if len(data) == 2:
                data, columns = data
                Notifier.to_telegram(
                    data.as_dataframe(), additional_text=strategy_text, cols=columns
                )
            else:
                Notifier.to_telegram(data.as_dataframe(), additional_text=strategy_text)


if __name__ == "__main__":
    from datetime import date

    data = AllNSEStocks(dated=date.today().strftime(DATE_FMT), nse_top=1000)
    obj = StockReporter("swings", data)
    obj.notify_report()
