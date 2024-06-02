from datetime import date, datetime
from pathlib import Path

import pytest
import requests
from pandas import DataFrame

from trade.nse.nse_config import DATE_FMT, NSEConfig

MARKET, COUNTRY = "NSE", "INDIA"
DATED = datetime.today().strftime(DATE_FMT)


@pytest.fixture
def nse_config():
    return NSEConfig(DATED, market=MARKET, country=COUNTRY)


@pytest.fixture
def nse_config_with_log_config():
    log_path = Path(__file__).parent.parent.parent
    log_config = dict(date_fmt=DATE_FMT, log_path=log_path, level=10)
    return NSEConfig(DATED, market=MARKET, country=COUNTRY, log_config=log_config)


def test_advanced_header(nse_config):
    assert isinstance(nse_config.advanced_header, dict)


def test_holiday_url(nse_config):
    assert nse_config.holiday_url.startswith("https://")


def test_get_market_holidays(nse_config):
    holidays = nse_config.get_market_holidays()
    assert isinstance(holidays, list)


def test_get_equity_meta(nse_config):
    meta = nse_config.get_equity_meta("RELIANCE")
    assert isinstance(meta, dict)


def test_get_equity_quote(nse_config):
    quote = nse_config.get_equity_quote("RELIANCE")
    assert isinstance(quote, dict)


@pytest.mark.freeze_time("2024-05-17 15:20")
def test_get_eq_bhavcopy():
    dated = datetime.today().date().strftime(DATE_FMT)
    nse_config = NSEConfig(dated, market=MARKET, country=COUNTRY)
    bhavcopy = nse_config.get_eq_bhavcopy()
    assert isinstance(bhavcopy, DataFrame)


def test_init(nse_config):
    assert nse_config.today == DATED
    assert nse_config.market == MARKET
    assert nse_config.country == COUNTRY


def test_get_market_holidays_key_error(nse_config):
    with pytest.raises(KeyError):
        nse_config.get_market_holidays(holiday_key="InvalidKey")


def test_get_equity_meta_symbol_none(nse_config):
    with pytest.raises(AttributeError):
        nse_config.get_equity_meta(None)


def test_get_equity_quote_symbol_none(nse_config):
    with pytest.raises(AttributeError):
        nse_config.get_equity_quote(None)


def test_get_eq_bhavcopy_url_error(nse_config, monkeypatch):
    def mock_download_data(url, headers):
        raise requests.exceptions.RequestException

    monkeypatch.setattr(nse_config, "download_data", mock_download_data)

    with pytest.raises(requests.exceptions.RequestException):
        nse_config.get_eq_bhavcopy()


def test_if_logger_exists(nse_config):
    does_logger_exists = hasattr(nse_config, "logger")
    assert not does_logger_exists


def test_if_logger_exists_after_config(nse_config_with_log_config):
    does_logger_exists = hasattr(nse_config_with_log_config, "logger")
    log_file_path = Path(__file__).parent.parent.parent / Path("log")
    assert does_logger_exists
    assert log_file_path.exists()


def test_get_all_etfs(nse_config):

    response = nse_config.get_all_etfs()

    assert isinstance(response, dict)
    assert isinstance(response["data"], list)
    assert all(isinstance(i, dict) for i in response["data"])
    assert len(response["data"]) > 100


@pytest.mark.parametrize(
    "symbol", ["NIFTY", "NIFTYNXT50", "BANKNIFTY", "RELIANCE", "SBIN"]
)
def test_get_option_chain(nse_config, symbol):
    response = nse_config.get_option_chain_data(symbol)
    assert isinstance(response, dict)
    assert all(i in response.keys() for i in ("records", "filtered"))
