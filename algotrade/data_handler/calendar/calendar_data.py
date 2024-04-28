from dataclasses import dataclass, field
from datetime import date, datetime, time, timedelta
from typing import List, Optional, TypedDict, Union
from zoneinfo import ZoneInfo

from pandas.tseries.offsets import BDay

from algotrade.data_handler.calendar.constants import (DATE_FMT, HOLIDAY_EXHAUSTED,
                                                       ISO_WEEK_RANGE,
                                                       MARKET_CLOSE_TIME,
                                                       MARKET_START_TIME, TIME_CUTOFF,
                                                       TIME_ZONE, TODAY, WEEKDAY_TO_ISO)


@dataclass
class MarketTimings:
    start_time: time = MARKET_START_TIME
    close_time: time = MARKET_CLOSE_TIME
    time_zone: ZoneInfo = TIME_ZONE
    time_cutoff: time = TIME_CUTOFF


@dataclass
class DateObj:
    raw_date: str
    _formatted_date: datetime = field(init=False)

    @property
    def as_date(self) -> datetime:
        self._formatted_date = datetime.strptime(self.raw_date, DATE_FMT).date()

        return self._formatted_date

    @property
    def as_str(self) -> str:
        return self.as_date.strftime(DATE_FMT)

    @property
    def as_weekday(self):
        return self.as_date.strftime("%A")

    @property
    def as_weekday_iso(self) -> int:
        return WEEKDAY_TO_ISO[self.as_weekday]

    def __str__(self):
        return self.as_str

    def __add__(self, date_diff: Union[timedelta, BDay]) -> 'DateObj':
        new_date = self.as_date + date_diff
        return DateObj(new_date.strftime(DATE_FMT))

    def __sub__(self, date_diff: Union[timedelta, BDay]) -> 'DateObj':
        new_date = self.as_date - date_diff
        return DateObj(new_date.strftime(DATE_FMT))

    def __eq__(self, another_date: Union['DateObj', date, datetime]):

        if isinstance(another_date, date) or isinstance(another_date, datetime):
            another_date = DateObj(another_date.strftime(DATE_FMT))

        if isinstance(another_date, str):
            another_date = DateObj(another_date)

        if self.as_date == another_date.as_date:
            return True

        return False

    def __gt__(self, other_date: Union['DateObj', date, datetime]):

        if isinstance(other_date, date) or isinstance(other_date, datetime):
            another_date = DateObj(other_date.strftime(DATE_FMT))

        if isinstance(other_date, str):
            other_date = DateObj(other_date)

        if self.as_date > other_date:
            return True

        return False

    def __lt__(self, other_date: Union['DateObj', date, datetime]):

        if isinstance(other_date, date) or isinstance(other_date, datetime):
            other_date = DateObj(other_date.strftime(DATE_FMT))

        if isinstance(other_date, str):
            other_date = DateObj(other_date)

        if self.as_date < other_date:
            return True

        return False


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
    next_holiday: Optional[DateObj] = None
    next_working: Optional[DateObj] = None

    def __len__(self) -> int:
        return len(self.holidays)

    def __post_init__(self):
        self.holidays = [self._create_holiday_entry(h) for h in self.holidays_dict]
        self.update_next_holiday()

    def _create_holiday_entry(
        self, holiday_str: MarketHolidayEntry
    ) -> MarketHolidayEntry:

        return MarketHolidayEntry(**holiday_str)

    def update_next_holiday(self) -> None:
        today = TODAY

        for i, holiday in enumerate(self.holidays):
            if holiday.trade_date.as_date >= today:
                if holiday.working and self.next_working is None:
                    self.next_working = DateObj(holiday.trade_date.as_str)

                if not holiday.working and self.next_holiday is None:
                    self.next_holiday = DateObj(holiday.trade_date.as_str)

                if self.next_holiday is not None and self.next_working is not None:
                    break
        else:
            raise StopIteration(HOLIDAY_EXHAUSTED)

    @property
    def prev_holiday(self) -> DateObj:
        today = TODAY

        for holiday in reversed(self.holidays):
            if holiday.trade_date < today and not holiday.working:
                return DateObj(holiday.trade_date.as_str)

        return None

    @property
    def prev_working(self) -> DateObj:
        today = TODAY

        for holiday in reversed(self.holidays):
            if holiday.trade_date < today and holiday.working:
                return DateObj(holiday.trade_date.as_str)

        return None


@dataclass
class WorkingDayDate:
    given_date: str
    market_holidays: List[MarketHolidayType]
    working_day: DateObj = field(init=False)

    @property
    def day(self):
        return self.working_day

    def compare_time_cutoff(self) -> DateObj:
        date_ = DateObj(self.given_date)
        tomorrow: DateObj = date_ + BDay()
        yesterday: DateObj = date_ - BDay()
        cut_off = TIME_CUTOFF
        now = datetime.now().time()

        if date_ > tomorrow and date_ > yesterday:
            return date_

        if date_ < tomorrow and date_ < yesterday:
            return date_

        if cut_off > now:
            if date_ == TODAY:
                if date_.as_weekday_iso in ISO_WEEK_RANGE:
                    return date_ - BDay()
                return yesterday

            if date_ == yesterday:
                if date_.as_weekday_iso in ISO_WEEK_RANGE:
                    return date_ + BDay()
                return date_

            if date_ == tomorrow:
                if date_.as_weekday_iso in ISO_WEEK_RANGE:
                    return date_ + BDay()
                return tomorrow

            if tomorrow < date_ and date_ > yesterday:
                return date_ - BDay()

        return date_

    def __post_init__(self):
        if DateObj(self.given_date) == TODAY and MARKET_START_TIME <= datetime.now().time() <= TIME_CUTOFF:
            self.working_day = self.compare_time_cutoff()
        else:
            self.working_day = DateObj(self.given_date)

        self.market_holidays = MarketHolidays(self.market_holidays)

    @property
    def next_business_day(self) -> None:

        today = self.day
        tomorrow = today + BDay()

        if tomorrow == self.market_holidays.next_holiday:
            tomorrow = tomorrow + BDay()

        if self.market_holidays.next_working > today:
            if self.market_holidays.next_working < tomorrow:
                tomorrow = self.market_holidays.next_holiday

        return tomorrow

    @property
    def previous_business_day(self) -> None:

        today = self.day
        yesterday = today - BDay()

        if yesterday == self.market_holidays.next_holiday:
            yesterday = yesterday - BDay()

        if self.market_holidays.prev_working is not None:
            if self.market_holidays.prev_working < today and \
                    self.market_holidays.prev_working > yesterday:
                yesterday = self.market_holidays.prev_working

        return yesterday
