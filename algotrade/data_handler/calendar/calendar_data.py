from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional, TypedDict

from algotrade.data_handler.calendar.constants import DATE_FMT, TODAY, WEEKDAY_TO_ISO


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
        self.day = (
            DayOfWeek(self.week_day)
            if self.week_day in (None, str())
            else DayOfWeek(self.trade_date.as_weekday)
        )
        self.working = True if "*" in self.description else False


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

    def _create_holiday_entry(
        self, holiday_str: MarketHolidayEntry
    ) -> MarketHolidayEntry:

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
