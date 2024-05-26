from unittest.mock import MagicMock

import pandas as pd
import pytest

from trade.nse.nse_stock import NSEStock


@pytest.fixture
def nse_stock():
    return NSEStock(dated="17-May-2024", symbol="RELIANCE")


def test_nse_stock_init(nse_stock):
    assert nse_stock.dated == "17-May-2024"
    assert nse_stock.symbol == "RELIANCE"
    assert nse_stock.tf == "1d"


def test_nse_stock_str(nse_stock):
    assert str(nse_stock) == "RELIANCE"


def test_nse_stock_get_meta_data(nse_stock):
    nse_stock._nse_config.get_equity_meta = MagicMock(
        return_value={"name": "Apple Inc."}
    )
    assert nse_stock.get_meta_data == {"name": "Apple Inc."}


def test_nse_stock_get_ticker(nse_stock):
    nse_stock._nse_config.yf.Ticker = MagicMock()
    assert nse_stock.ticker
