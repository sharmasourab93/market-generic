from datetime import date, datetime
from pathlib import Path

import pytest
from freezegun import freeze_time
from pandas import DataFrame

from trade.calendar import MarketCalendar, MarketHolidayType
from trade.ticker import Exchange
from trade.utils import LoggingType

FROZEN_DATE = "2024-04-29 05:10"
CONFIG_FILE = Path(__file__).parent.parent.parent / Path("configs/nse.json")
DATE_FMT = "%d-%b-%Y"
MARKET, COUNTRY = "NSE", "INDIA"

MARKET_TIMINGS = dict(
    [
        ("start_time", "0915"),
        ("close_time", "1530"),
        ("time_zone", "Asia/Kolkata"),
        ("time_cutoff", "1600"),
    ]
)

HOLIDAYS_DICT = [
    {
        "trade_day": "22-Jan-2024",
        "week_day": "Monday",
        "description": "Special Holiday\r",
    },
    {
        "trade_day": "01-May-2024",
        "week_day": "Wednesday",
        "description": "Maharashtra Day\r",
    },
    {
        "trade_day": "01-Nov-2024",
        "week_day": "Friday",
        "description": "Diwali Laxmi Pujan*\r",
    },
]


@pytest.fixture(scope="module")
def prepared_args():
    return


@pytest.mark.freeze_time(FROZEN_DATE)
def test_exchange_data():
    TODAY = datetime.strftime(datetime.today().date(), DATE_FMT)
    prepared_args = (
        TODAY,
        DATE_FMT,
        CONFIG_FILE,
        MARKET,
        COUNTRY,
        HOLIDAYS_DICT,
        MARKET_TIMINGS,
        None,
    )
    obj = Exchange(*prepared_args)
    check_attrs = (
        "get_period_data",
        "industry",
        "market",
        "nse",
        "api",
        "block_deal",
        "fii_dii_report",
        "get_cookies",
        "yf",
    )
    assert all([hasattr(obj, i) for i in check_attrs])


@pytest.mark.freeze_time(FROZEN_DATE)
@pytest.mark.parametrize("ticker", ["RELIANCE", "SBIN"])
def test_get_period_data(ticker):
    TODAY = datetime.strftime(datetime.today().date(), DATE_FMT)
    prepared_args = (
        TODAY,
        DATE_FMT,
        CONFIG_FILE,
        MARKET,
        COUNTRY,
        HOLIDAYS_DICT,
        MARKET_TIMINGS,
        None,
    )
    obj = Exchange(*prepared_args)

    response = obj.get_period_data(ticker)

    assert isinstance(response, DataFrame)
    assert not response.empty


@pytest.mark.freeze_time(FROZEN_DATE)
def test_check_dates_with_markettime():
    TODAY = datetime.strftime(datetime.today().date(), DATE_FMT)
    prepared_args = (
        TODAY,
        DATE_FMT,
        CONFIG_FILE,
        MARKET,
        COUNTRY,
        HOLIDAYS_DICT,
        MARKET_TIMINGS,
        None,
    )
    obj = Exchange(*prepared_args)
    assert obj.today == "29-Apr-2024"
    assert obj.prev_day == "26-Apr-2024"
    assert obj.next_day == "29-Apr-2024"


@pytest.mark.freeze_time("2024-04-29 16:10")
def test_check_dates_wo_markettime():
    TODAY = datetime.strftime(datetime.today().date(), DATE_FMT)
    prepared_args = (
        TODAY,
        DATE_FMT,
        CONFIG_FILE,
        MARKET,
        COUNTRY,
        HOLIDAYS_DICT,
        MARKET_TIMINGS,
        None,
    )
    obj = Exchange(*prepared_args)
    assert obj.today == "29-Apr-2024"
    assert obj.prev_day == "26-Apr-2024"
    assert obj.next_day == "30-Apr-2024"
