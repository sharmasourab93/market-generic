import re
from calendar import monthrange
from datetime import date, datetime
from typing import Dict, List, Optional, Tuple

import numpy as np
import pandas as pd
import yfinance as yf

from trade.utils import Logger, MarketDFUtils

SYMBOL_ERROR = "Error Incurred for symbol: {0}"
YFIN_TICKER_BY_COUNTRY = {
    "INDIA": {"BSE": ".BO", "NSE": ".NS"},
    # TODO: Populate this country to extend to all the countries.
}


class YFinance(MarketDFUtils):
    def __init__(
        self,
        market: str,
        country: str,
        date_fmt: str,
        *,
        ticker_modifications: dict = None,
    ):
        self.market = market
        self.country = country
        self.date_fmt = date_fmt
        self.ticker_modifications = ticker_modifications
        self.yf = yf

    def adjust_yfin_ticker_by_market(self, symbol: str, index: bool) -> str:

        if not index:
            if self.country in YFIN_TICKER_BY_COUNTRY.keys():
                suffix = YFIN_TICKER_BY_COUNTRY[self.country].get(self.market, "")

            if suffix != str():
                return symbol.upper() + suffix

        return symbol.upper()

    def log_method(self, message) -> None:
        if hasattr(self, "logger"):
            self.logger.error(message)

    def get_period_data(
        self,
        symbol: str,
        period: str = "1mo",
        interval: str = "1d",
        rounding: bool = True,
        index: bool = False,
        ascending: bool = False,
        auto_adjust: bool = True,
        progress: bool = False,
        **kwargs,
    ) -> pd.DataFrame:

        symbol = self.adjust_yfin_ticker_by_market(symbol, index)

        data = self.yf.download(
            symbol,
            period=period,
            interval=interval,
            rounding=rounding,
            auto_adjust=auto_adjust,
            progress=progress,
            **kwargs,
        )

        if 0 in data.shape:
            message = SYMBOL_ERROR.format(symbol)
            self.log_method(message)

            if self.ticker_modifications is not None:
                if symbol in list(self.ticker_modifications.keys()):
                    return self.get_period_data(
                        self.ticker_modifications[symbol], period, interval
                    )
                return pd.DataFrame()

        data["prev_close"] = data.Close.shift(1)
        data = data.loc[~data.prev_close.isna(), :]
        data = self.calculate_pct_change(data, "Close", "prev_close")
        data = data.sort_index(ascending=ascending)
        data = data.reset_index()

        try:
            data["Date"] = pd.to_datetime(data.Date).apply(lambda x: x.date())
        except AttributeError:
            pass

        data.columns = data.columns.str.lower()

        if self.date_fmt is not None:
            data["date"] = pd.to_datetime(data.date).apply(
                lambda x: x.strftime(self.date_fmt)
            )

        return data.round(2)

    def get_unique_ticker_set(self, tickers: List[str]) -> Tuple[str]:

        return tuple([self.adjust_yfin_ticker_by_market(i) for i in tickers])
