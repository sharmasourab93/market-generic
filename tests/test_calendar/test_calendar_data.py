from datetime import datetime, timedelta

import pytest

from trade.calendar.calendar_data import (
    WEEKDAY_TO_ISO,
    DateObj,
    DayOfWeek,
    MarketHolidayEntry,
    MarketHolidays,
    MarketHolidayType,
    WorkingDayDate,
)

MARKET_TIMINGS = {
    "start_time": "0915",
    "close_time": "1530",
    "time_zone": "Asia/Kolkata",
    "time_cutoff": "1600",
}

DATE_FMT = "%d-%b-%Y"
FROZEN_DATE = "2024-04-24"
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


@pytest.mark.parametrize("given_date", ["28-Apr-2024", "01-Jan-2024"])
def test_date_obj_as_datetime(given_date):
    date_obj = DateObj(given_date, date_fmt=DATE_FMT)
    assert date_obj.as_date == datetime.strptime(given_date, DATE_FMT).date()


@pytest.mark.parametrize("given_date", ["28-Apr-2024", "01-Jan-2024"])
def test_date_obj_as_str(given_date):
    date_obj = DateObj(given_date, date_fmt=DATE_FMT)
    assert date_obj.as_str == given_date


@pytest.mark.parametrize("given_date", ["28-Apr-2024", "01-Jan-2024"])
def test_date_obj_as_weekday(given_date):
    date_obj = DateObj(given_date, date_fmt=DATE_FMT)
    assert date_obj.as_weekday == datetime.strptime(given_date, DATE_FMT).strftime("%A")


@pytest.mark.parametrize("given_date", ["28-Apr-2024", "01-Jan-2024"])
def test_date_obj_str(given_date):
    date_obj = DateObj(given_date, date_fmt=DATE_FMT)
    assert str(date_obj) == given_date


@pytest.mark.parametrize("given_date", ["28-Apr-2024", "01-Jan-2024"])
def test_date_obj_eq(given_date):
    date_obj = DateObj(given_date, date_fmt=DATE_FMT)
    assert date_obj == given_date


@pytest.mark.parametrize("given_date", ["28-Apr-2024", "01-Jan-2024"])
def test_date_obj_add(given_date):
    date_obj = DateObj(given_date, date_fmt=DATE_FMT)
    delta_days = timedelta(days=10)
    next_day = (datetime.strptime(given_date, DATE_FMT) + delta_days).date()
    assert date_obj + delta_days == next_day


@pytest.mark.parametrize("given_date", ["28-Apr-2024", "01-Jan-2024"])
def test_date_obj_sub(given_date):
    date_obj = DateObj(given_date, date_fmt=DATE_FMT)
    delta_days = timedelta(days=10)
    next_day = (datetime.strptime(given_date, DATE_FMT) - delta_days).date()
    assert date_obj - delta_days == next_day


@pytest.mark.parametrize("given_date", ["28-Apr-2024", "01-Jan-2024"])
def test_date_obj_gt(given_date):
    date_obj = DateObj(given_date, date_fmt=DATE_FMT)
    delta_days = timedelta(days=10)
    next_day = (datetime.strptime(given_date, DATE_FMT) - delta_days).date()
    assert date_obj > next_day


@pytest.mark.parametrize("given_date", ["28-Apr-2024", "01-Jan-2024"])
def test_date_obj_lt(given_date):
    date_obj = DateObj(given_date, date_fmt=DATE_FMT)
    delta_days = timedelta(days=10)
    next_day = (datetime.strptime(given_date, DATE_FMT) + delta_days).date()
    assert date_obj < next_day


# Test the DayOfWeek class
@pytest.mark.parametrize(
    "weekday, week_iso", [(k, v) for k, v in WEEKDAY_TO_ISO.items()]
)
def test_day_of_week_iso(weekday, week_iso):
    day_of_week = DayOfWeek(weekday)
    assert day_of_week.iso == week_iso


@pytest.mark.freeze_time(FROZEN_DATE)
@pytest.mark.parametrize("entry", HOLIDAYS_DICT)
def test_market_holiday_entry_creation(entry: MarketHolidayType):
    holiday_entry = MarketHolidayEntry(**entry, date_fmt=DATE_FMT)
    assert holiday_entry.trade_date.as_str == entry["trade_day"]
    assert str(holiday_entry.trade_date) == entry["trade_day"]
    assert (
        holiday_entry.day.iso
        == WEEKDAY_TO_ISO[
            datetime.strptime(entry["trade_day"], DATE_FMT).strftime("%A")
        ]
    )

    if "*" in holiday_entry.description:
        assert holiday_entry.working is True

    else:
        assert holiday_entry.working is False


@pytest.mark.freeze_time(FROZEN_DATE)
def test_market_holidays_creation():
    holidays_dict = HOLIDAYS_DICT
    market_holidays = MarketHolidays(holidays_dict=holidays_dict, date_fmt=DATE_FMT)
    assert len(market_holidays) == len(holidays_dict)
    assert market_holidays.next_working == holidays_dict[-1]["trade_day"]
    assert market_holidays.next_holiday == holidays_dict[1]["trade_day"]
    assert market_holidays.prev_holiday == holidays_dict[0]["trade_day"]
    assert market_holidays.prev_working is None


@pytest.mark.freeze_time(FROZEN_DATE)
def test_market_holidays_update_next_holiday():
    holidays_dict = HOLIDAYS_DICT
    market_holidays = MarketHolidays(holidays_dict=holidays_dict, date_fmt=DATE_FMT)
    market_holidays.update_next_holiday()
    assert (
        market_holidays.next_working.trade_date.as_str == holidays_dict[-1]["trade_day"]
    )
    assert (
        market_holidays.next_holiday.trade_date.as_str == holidays_dict[1]["trade_day"]
    )


@pytest.mark.freeze_time(FROZEN_DATE)
def test_market_holidays_update_next_holiday():
    holidays_dict = []
    with pytest.raises(StopIteration):
        market_holidays = MarketHolidays(holidays_dict=holidays_dict, date_fmt=DATE_FMT)
        market_holidays.update_next_holiday()


@pytest.mark.freeze_time(FROZEN_DATE)
@pytest.mark.parametrize(
    "given_date, next_date, prev_date",
    [
        ("24-Apr-2024", "25-Apr-2024", "23-Apr-2024"),
        ("26-Apr-2024", "29-Apr-2024", "25-Apr-2024"),
        ("30-Apr-2024", "2-May-2024", "29-Apr-2024"),
        ("31-Oct-2024", "1-Nov-2024", "30-Oct-2024"),
        (
            "1-Nov-2024",
            "4-Nov-2024",
            "31-Oct-2024",
        ),
    ],
)
def test_working_day_date(given_date, next_date, prev_date):
    holidays_dict = HOLIDAYS_DICT
    working_date_obj = WorkingDayDate(
        given_date, holidays_dict, market_timings=MARKET_TIMINGS, date_fmt=DATE_FMT
    )
    previous_day = working_date_obj.previous_business_day
    next_day = working_date_obj.next_business_day
    assert next_day == next_date
    assert previous_day == prev_date


@pytest.mark.freeze_time("2024-04-29 5:10")
@pytest.mark.parametrize(
    "given_date, next_date, prev_date",
    [
        ("29-Apr-2024", "29-Apr-2024", "26-Apr-2024"),
    ],
)
def test_working_day_today_1(given_date, next_date, prev_date):
    holiday_dict = HOLIDAYS_DICT
    working_date_obj = WorkingDayDate(
        given_date, holiday_dict, market_timings=MARKET_TIMINGS, date_fmt=DATE_FMT
    )

    next_day = working_date_obj.next_business_day
    prev_day = working_date_obj.previous_business_day

    assert next_day == next_date
    assert prev_day == prev_date


@pytest.mark.freeze_time("2024-04-29 10:40")
@pytest.mark.parametrize(
    "given_date, next_date, prev_date",
    [
        ("29-Apr-2024", "30-Apr-2024", "26-Apr-2024"),
    ],
)
def test_working_day_today_2(given_date, next_date, prev_date):
    holiday_dict = HOLIDAYS_DICT
    working_date_obj = WorkingDayDate(
        given_date, holiday_dict, market_timings=MARKET_TIMINGS, date_fmt=DATE_FMT
    )

    next_day = working_date_obj.next_business_day
    prev_day = working_date_obj.previous_business_day

    assert next_day == next_date
    assert prev_day == prev_date
