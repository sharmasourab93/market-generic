from unittest.mock import MagicMock

import pytest

from trade.nse import AllNSEStocks, NSEStock, NSE_TOP


def test_all_nse_stocks_post_init_with_symbols():
    all_nse_stocks = AllNSEStocks("17-May-2024", ["RELIANCE", "SBIN"])
    assert all_nse_stocks.symbols[0] == "RELIANCE"
    assert all_nse_stocks.symbols[1] == "SBIN"
    attrs = ("open", "low", "close", "high", "prev_close", "prev_volume", "volume_diff")
    assert all(hasattr(all_nse_stocks.symbols[1], i) for i in attrs)


@pytest.mark.parametrize("tops", [1, 5])
def test_all_nse_stocks(tops):
    all_nse_stocks = AllNSEStocks("17-May-2024", nse_top=tops)
    assert len(all_nse_stocks) == tops
