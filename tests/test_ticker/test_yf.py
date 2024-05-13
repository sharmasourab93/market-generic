import pytest
from trade.ticker import YFinance


@pytest.fixture
def yfin_data_instance():
    return YFinance(market="NSE", country="INDIA", date_fmt="%Y-%m-%d")


@pytest.mark.parametrize("ticker", ["reliance", "sbin"])
def test_adjust_yfin_ticker_by_market(yfin_data_instance, ticker):
    assert (
        yfin_data_instance.adjust_yfin_ticker_by_market(ticker)
        == ticker.upper() + ".NS"
    )


def test_get_period_data(yfin_data_instance):
    data = yfin_data_instance.get_period_data("reliance", period="1mo", interval="1d")
    assert not data.empty
    cols = (
        "date",
        "open",
        "high",
        "low",
        "close",
        "volume",
        "prev_close",
        "pct_change",
    )
    assert all(i in data.columns for i in cols)
