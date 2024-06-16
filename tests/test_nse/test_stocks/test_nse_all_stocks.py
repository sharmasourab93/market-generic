import pytest

from trade.nse.stocks.nse_all_stocks import AllNSEStocks


@pytest.mark.skip
def test_all_nse_stocks_post_init_with_symbols():
    all_nse_stocks = AllNSEStocks("17-May-2024", ["RELIANCE", "SBIN"])
    assert all_nse_stocks.symbols["RELIANCE"] == "RELIANCE"
    assert all_nse_stocks.symbols["SBIN"] == "SBIN"
    attrs = ("open", "low", "close", "high", "prev_close", "prev_volume", "volume_diff")
    assert all(hasattr(all_nse_stocks.symbols["RELIANCE"], i) for i in attrs)


@pytest.mark.parametrize("tops", [1, 5])
def test_all_nse_stocks(tops):
    all_nse_stocks = AllNSEStocks("17-May-2024", nse_top=tops)
    assert len(all_nse_stocks) == tops
