from datetime import date

from trade.nse.indices import SpotIndices
from trade.nse.nse_configs import DATE_FMT
from trade.technicals.indicators import MovingAverages, PivotPoints
from trade.utils.notify import Notifier
from trade.utils.notify.outputs import formatters


class IndexReport:

    def __init__(self, to_telegram: bool = True, to_gsheet: bool = True):

        dated = date.today().strftime(DATE_FMT)
        self.indices = SpotIndices(dated)
        self.notify = Notifier

    def prepare_report(self):
        """
        We are preparing reports as follows:
        1. Analysis + Option Chain of Nifty, Banknifty, Fin Nifty, Midcap Nifty
        2. India VIX
        3. Advance - Decline
        4. FII - DII

        There are two ways to do it
        1. Update each Index Analysis Separately & ADv-dec, FII-DII separately on
        Telegram
        2. Update Google Sheet and Notify update on telegram.
        """
        report = self.indices.comprehensive_report_as_dataframe()
        text_data = formatters.format_market_data(report)
        self.notify.to_telegram(text_data)


if __name__ == "__main__":
    obj = IndexReport()
    obj.prepare_report()
