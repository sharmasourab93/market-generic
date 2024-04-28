from datetime import date, datetime
from typing import Optional, TypedDict, List
from dataclasses import dataclass, field


from algotrade.data_handler.calendar.constants import (
    ADHOC_MARKET_TIME_OFF,
    ADHOC_MARKET_TIME_ON,
    DATE_FMT,
    MARKET_CLOSE_TIME,
    MARKET_START_TIME,
    TIME_CUTOFF,
    TIME_ZONE,
    TODAY,
    WEEKDAY_TO_ISO
)


@dataclass
class DateObj:
    raw_date: str
    _formatted_date: datetime = field(init=False)

    @property
    def as_datetime(self) -> datetime:
        self._formatted_date = datetime.strptime(self.raw_date, DATE_FMT).date()

        return self._formatted_date

    @property
    def as_str(self) -> str:
        return self.as_datetime.strftime(DATE_FMT)

    @property
    def as_weekday(self):
        return self.as_datetime.strftime("%A")

    def __str__(self):
        return self.as_str


@dataclass
class DayOfWeek:
    day: str
    _iso_day: int = field(init=False)

    def __post_init__(self):
        self._iso_day = WEEKDAY_TO_ISO.get(self.day.strip().capitalize())

    @property
    def iso(self):
        return self._iso_day


@dataclass
class MarketHolidayEntry:
    trade_day: str
    trade_date: DateObj = field(init=False)
    week_day: str
    day: Optional[str] = field(init=False, default=None)
    description: str
    working: bool = field(init=False)

    def __post_init__(self):
        self.trade_date = DateObj(self.trade_day)
        self.day = DayOfWeek(self.week_day) if self.week_day in (None, str()) else DayOfWeek(self.trade_date.as_weekday)
        self.working = True if '*' in self.description else False


class MarketHolidayType(TypedDict):
    trade_day: str
    week_day: Optional[str]
    description: str


@dataclass
class MarketHolidays:
    holidays_dict: List[MarketHolidayType]
    holidays: List[MarketHolidayEntry] = field(init=False, default_factory=list)
    next_holiday: Optional[MarketHolidayEntry] = None
    next_working: Optional[MarketHolidayEntry] = None

    def __post_init__(self):
        self.holidays = [self._create_holiday_entry(h) for h in self.holidays_dict]
        self.update_next_holiday()

    def _create_holiday_entry(self, holiday_str: MarketHolidayEntry)-> MarketHolidayEntry:

        return MarketHolidayEntry(**holiday_str)

    def update_next_holiday(self) -> None:
        today = TODAY

        for holiday in self.holidays:
            if holiday.trade_date.as_datetime >= today:
                if holiday.working and self.next_working is None:
                    self.next_working = holiday

                elif not holiday.working and self.next_holiday is None:
                    self.next_holiday = holiday

                if self.next_holiday is not None and self.next_working is not None:
                    break
        else:
            raise StopIteration("Holiday List exhausted. Update Holiday List")


if __name__ == '__main__':
    hols = [{'trade_day': '22-Jan-2024', 'week_day': 'Monday', 'description': 'Special Holiday\r'}, {'trade_day': '26-Jan-2024', 'week_day': 'Friday', 'description': 'Republic Day\r'}, {'trade_day': '08-Mar-2024', 'week_day': 'Friday', 'description': 'Mahashivratri\r'}, {'trade_day': '25-Mar-2024', 'week_day': 'Monday', 'description': 'Holi\r'}, {'trade_day': '29-Mar-2024', 'week_day': 'Friday', 'description': 'Good Friday\r'}, {'trade_day': '11-Apr-2024', 'week_day': 'Thursday', 'description': 'Id-Ul-Fitr (Ramadan Eid)\r'}, {'trade_day': '14-Apr-2024', 'week_day': 'Sunday', 'description': 'Dr. Baba Saheb Ambedkar Jayanti\r'}, {'trade_day': '17-Apr-2024', 'week_day': 'Wednesday', 'description': 'Shri Ram Navmi\r'}, {'trade_day': '21-Apr-2024', 'week_day': 'Sunday', 'description': 'Shri Mahavir Jayanti\r'}, {'trade_day': '01-May-2024', 'week_day': 'Wednesday', 'description': 'Maharashtra Day\r'}, {'trade_day': '17-Jun-2024', 'week_day': 'Monday', 'description': 'Bakri Id\r'}, {'trade_day': '17-Jul-2024', 'week_day': 'Wednesday', 'description': 'Moharram\r'}, {'trade_day': '15-Aug-2024', 'week_day': 'Thursday', 'description': 'Independence Day\r'}, {'trade_day': '07-Sep-2024', 'week_day': 'Saturday', 'description': 'Ganesh Chaturthi\r'}, {'trade_day': '02-Oct-2024', 'week_day': 'Wednesday', 'description': 'Mahatma Gandhi Jayanti\r'}, {'trade_day': '12-Oct-2024', 'week_day': 'Saturday', 'description': 'Dussehra\r'}, {'trade_day': '01-Nov-2024', 'week_day': 'Friday', 'description': 'Diwali Laxmi Pujan*\r'}, {'trade_day': '02-Nov-2024', 'week_day': 'Saturday', 'description': 'Diwali-Balipratipada\r'}, {'trade_day': '15-Nov-2024', 'week_day': 'Friday', 'description': 'Gurunanak Jayanti\r'}, {'trade_day': '25-Dec-2024', 'week_day': 'Wednesday', 'description': 'Christmas\r'}]
    market_holidays = MarketHolidays(hols)
    print(market_holidays)