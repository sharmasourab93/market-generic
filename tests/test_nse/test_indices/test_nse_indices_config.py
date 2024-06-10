from datetime import datetime

import pandas as pd
import pytest
from pathlib import Path
from trade.nse.nse_configs.nse_indices_config import INDICES, NSEIndexConfig
from trade.nse.nse_configs.nse_config import DATE_FMT

MARKET, COUNTRY = "NSE", "INDIA"
DATED = datetime.today().strftime(DATE_FMT)
CONFIG_FILE = Path(__file__).resolve().parents[3] / Path("configs/nse.json")


@pytest.fixture(scope="function")
def index_config():
    try:
        return NSEIndexConfig(DATED, market=MARKET, country=COUNTRY, config=CONFIG_FILE)
    except FileNotFoundError:
        config_file = Path(__file__).resolve().parents[4] / Path("configs/nse.json")
        return NSEIndexConfig(DATED, market=MARKET, country=COUNTRY, config=config_file)


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
