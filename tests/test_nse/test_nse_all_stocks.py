import pytest
from unittest.mock import MagicMock
from trade.nse.nse_stock import AllNSEStocks, NSEStock


def test_all_nse_stocks_post_init_with_symbols():
    all_nse_stocks = AllNSEStocks("17-May-2024", ["RELIANCE", "SBIN"])
    assert all_nse_stocks.symbols[0] == "RELIANCE"
    assert all_nse_stocks.symbols[1] == "SBIN"
    attrs = ("open", "low", "close","high", "prev_close", "prev_volume", "volume_diff")
    assert all(hasattr(all_nse_stocks.symbols[1], i) for i in attrs)
