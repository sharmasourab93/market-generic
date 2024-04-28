import pytest
from datetime import datetime
import os

print(os.getcwd())
print(sys.path)

from algotrade.data_handler.calendar.constants import TODAY, DATE_FMT, WEEKDAY_TO_ISO
from algotrade.data_handler.calendar.calendar_data import DateObj, DayOfWeek, MarketHolidayEntry, MarketHolidays, MarketHolidayType


FROZEN_DATE = '2024-04-24'


@pytest.mark.parametrize("given_date", ["28-Apr-2024", "01-Jan-2024"])
def test_date_obj_as_datetime(given_date):
    date_obj = DateObj(given_date)
    assert date_obj.as_datetime == datetime.strptime(given_date, DATE_FMT).date()


@pytest.mark.parametrize("given_date", ["28-Apr-2024", "01-Jan-2024"])
def test_date_obj_as_str(given_date):
    date_obj = DateObj(given_date)
    assert date_obj.as_str == given_date


@pytest.mark.parametrize("given_date", ["28-Apr-2024", "01-Jan-2024"])
def test_date_obj_as_weekday(given_date):
    date_obj = DateObj(given_date)
    assert date_obj.as_weekday == datetime.strptime(given_date, DATE_FMT).strftime("%A")


@pytest.mark.parametrize("given_date", ["28-Apr-2024", "01-Jan-2024"])
def test_date_obj_str(given_date):
    date_obj = DateObj(given_date)
    assert str(date_obj) == given_date


# Test the DayOfWeek class
@pytest.mark.parametrize("weekday, week_iso", [(k, v) for k, v in WEEKDAY_TO_ISO.items()])
def test_day_of_week_iso(weekday, week_iso):
    day_of_week = DayOfWeek(weekday)
    assert day_of_week.iso == week_iso


@pytest.mark.freeze_time(FROZEN_DATE)
@pytest.mark.parametrize("entry", [
    {'trade_day': '22-Jan-2024', 'week_day': 'Monday', 'description': 'Special Holiday\r'},
    {'trade_day': '26-Jan-2024', 'week_day': 'Friday', 'description': 'Republic Day\r'},
    {'trade_day': '01-Nov-2024', 'week_day': 'Friday', 'description': 'Diwali Laxmi Pujan*\r'}
])
def test_market_holiday_entry_creation(entry: MarketHolidayType):
    holiday_entry = MarketHolidayEntry(**entry)
    assert holiday_entry.trade_date.as_str == entry["trade_day"]
    assert str(holiday_entry.trade_date) == entry["trade_day"]
    assert holiday_entry.day.iso == WEEKDAY_TO_ISO[datetime.strptime(entry["trade_day"], DATE_FMT).strftime("%A")]

    if '*' in holiday_entry.description:
        assert holiday_entry.working is True

    else:
        assert holiday_entry.working is False


@pytest.mark.freeze_time(FROZEN_DATE)
def test_market_holidays_creation():
    holidays_dict = [{'trade_day': '22-Jan-2024', 'week_day': 'Monday', 'description': 'Special Holiday\r'},
    {'trade_day': '01-May-2024', 'week_day': 'Wednesday', 'description': 'Maharashtra Day\r'},
    {'trade_day': '01-Nov-2024', 'week_day': 'Friday', 'description': 'Diwali Laxmi Pujan*\r'}]
    market_holidays = MarketHolidays(holidays_dict=holidays_dict)
    assert len(market_holidays.holidays) == len(holidays_dict)
    assert market_holidays.next_working.trade_date.as_str == holidays_dict[-1]['trade_day']


@pytest.mark.freeze_time(FROZEN_DATE)
def test_market_holidays_update_next_holiday():
    holidays_dict = [{'trade_day': '22-Jan-2024', 'week_day': 'Monday', 'description': 'Special Holiday\r'},
    {'trade_day': '01-May-2024', 'week_day': 'Wednesday', 'description': 'Maharashtra Day\r'},
    {'trade_day': '01-Nov-2024', 'week_day': 'Friday', 'description': 'Diwali Laxmi Pujan*\r'}]
    market_holidays = MarketHolidays(holidays_dict=holidays_dict)
    market_holidays.update_next_holiday()
    assert market_holidays.next_working.trade_date.as_str == holidays_dict[-1]["trade_day"]
    assert market_holidays.next_holiday.trade_date.as_str == holidays_dict[1]["trade_day"]


@pytest.mark.freeze_time(FROZEN_DATE)
def test_market_holidays_update_next_holiday():
    holidays_dict = []
    with pytest.raises(StopIteration):
        market_holidays = MarketHolidays(holidays_dict=holidays_dict)
        market_holidays.update_next_holiday()

