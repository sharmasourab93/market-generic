from datetime import datetime
from pathlib import Path

import pandas as pd
import pytest

from trade.nse.nse_configs.nse_config import DATE_FMT
from trade.nse.nse_configs.nse_indices_config import INDICES, NSEIndexConfig

MARKET, COUNTRY = "NSE", "INDIA"
DATED = datetime.today().strftime(DATE_FMT)


@pytest.fixture(scope="function")
def index_config():
    return NSEIndexConfig(DATED, market=MARKET, country=COUNTRY)


def test_get_fii_dii(index_config):
    fii_dii = index_config.get_fii_dii_report()
    assert isinstance(fii_dii, list)
    assert len(fii_dii) > 0
    assert all(isinstance(item, dict) for item in fii_dii)


def test_get_all_indices(index_config):
    indices = index_config.get_all_indices()
    assert isinstance(indices, dict)
    assert len(indices) > 0
    assert all(
        isinstance(key, str) and isinstance(value, pd.DataFrame)
        for key, value in indices.items()
    )


def test_get_quote_index(index_config):
    for index in INDICES:
        quote = index_config.get_quote_index(index)
        assert isinstance(quote, dict)
        cols = ("adv-dec", "symbol", "ohlc", "dated", "status")
        assert all(i in cols for i in quote.keys())
        assert quote["symbol"] == index


def test_get_quote_index_invalid_input(index_config):
    with pytest.raises(AttributeError):
        index_config.get_quote_index(None)


def test_get_index_metrics(index_config):

    response = index_config.get_index_metrics()

    assert isinstance(response, dict)
    assert all(i in INDICES for i in response.keys())


def test_get_vix_history(index_config):
    start, end = "01-05-2024", "01-06-2024"
    response = index_config.get_vix_history(start, end)

    assert isinstance(response, dict)
