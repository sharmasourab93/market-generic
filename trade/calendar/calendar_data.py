from dataclasses import dataclass, field
from datetime import date, datetime, timedelta
from typing import List, Optional, TypedDict, Union

from pandas.tseries.offsets import BDay
from pytz import timezone

WEEKDAY_TO_ISO = {
    "Monday": 1,
    "Tuesday": 2,
    "Wednesday": 3,
    "Thursday": 4,
    "Friday": 5,
    "Saturday": 6,
    "Sunday": 7,
}


class MarketTimingType(TypedDict):
    start_time: str
    close_time: str
    time_zone: str
    time_cutoff: str


TIME_STRF = "%H%M"
HOLIDAY_EXHAUSTED = "Holiday List exhausted. Update Holiday List"
ISO_WEEK_RANGE = (0, 6)


@dataclass
class MarketTimings:
    start_time: str
    close_time: str
    time_zone: str
    time_cutoff: str

    def __post_init__(self):
        self.tz = timezone(self.time_zone)
        self.start_time = datetime.strptime(self.start_time, TIME_STRF).time()
        self.close_time = datetime.strptime(self.close_time, TIME_STRF).time()
        self.time_cutoff = datetime.strptime(self.time_cutoff, TIME_STRF).time()


@dataclass
class DateObj:
    raw_date: str
    date_fmt: str
    _formatted_date: datetime = None

    def __post_init__(self):
        self._formatted_date = datetime.strptime(self.raw_date, self.date_fmt).date()

    @property
    def as_date(self) -> datetime:
        return self._formatted_date

    @property
    def as_str(self) -> str:
        return self.as_date.strftime(self.date_fmt)

    @property
    def as_weekday(self):
        return self.as_date.strftime("%A")

    @property
    def as_weekday_iso(self) -> int:
        return WEEKDAY_TO_ISO[self.as_weekday]

    def __str__(self):
        return self.as_str

    def __add__(self, date_diff: Union[timedelta, BDay]) -> "DateObj":
        new_date = self.as_date + date_diff
        return DateObj(new_date.strftime(self.date_fmt), date_fmt=self.date_fmt)

    def __sub__(self, date_diff: Union[timedelta, BDay]) -> "DateObj":
        new_date = self.as_date - date_diff
        return DateObj(new_date.strftime(self.date_fmt), date_fmt=self.date_fmt)

    def __eq__(self, another_date: Union["DateObj", date, datetime]):

        if isinstance(another_date, date) or isinstance(another_date, datetime):
            another_date = DateObj(
                another_date.strftime(self.date_fmt), date_fmt=self.date_fmt
            )

        if isinstance(another_date, str):
            another_date = DateObj(another_date, date_fmt=self.date_fmt)

        if self.as_date == another_date.as_date:
            return True

        return False

    def __gt__(self, other_date: Union["DateObj", date, datetime]):

        if isinstance(other_date, date) or isinstance(other_date, datetime):
            another_date = DateObj(
                other_date.strftime(self.date_fmt), date_fmt=self.date_fmt
            )

        if isinstance(other_date, str):
            other_date = DateObj(other_date, date_fmt=self.date_fmt)

        if self.as_date > other_date:
            return True

        return False

    def __lt__(self, other_date: Union["DateObj", date, datetime]):

        if isinstance(other_date, date) or isinstance(other_date, datetime):
            other_date = DateObj(
                other_date.strftime(self.date_fmt), date_fmt=self.date_fmt
            )

        if isinstance(other_date, str):
            other_date = DateObj(other_date, date_fmt=self.date_fmt)

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
    date_fmt: str

    def __post_init__(self):
        self.trade_date = DateObj(self.trade_day, self.date_fmt)
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
    date_fmt: str
    holidays: List[MarketHolidayEntry] = field(init=False, default_factory=list)
    next_holiday: Optional[DateObj] = None
    next_working: Optional[DateObj] = None
    today: Optional[date] = None

    def __len__(self) -> int:
        return len(self.holidays)

    def __contains__(self, item):
        return item in [i.trade_date for i in self.holidays]

    def __post_init__(self):
        if self.today is None:
            self.today = datetime.today().date()

        self.holidays = [self._create_holiday_entry(h) for h in self.holidays_dict]
        self.update_next_holiday()

    def _create_holiday_entry(
        self, holiday_str: MarketHolidayEntry
    ) -> MarketHolidayEntry:

        return MarketHolidayEntry(**holiday_str, date_fmt=self.date_fmt)

    def update_next_holiday(self) -> None:

        for i, holiday in enumerate(self.holidays):
            if holiday.trade_date.as_date >= self.today:
                if holiday.working and self.next_working is None:
                    self.next_working = DateObj(
                        holiday.trade_date.as_str, date_fmt=self.date_fmt
                    )

                if not holiday.working and self.next_holiday is None:
                    self.next_holiday = DateObj(
                        holiday.trade_date.as_str, date_fmt=self.date_fmt
                    )

                if self.next_holiday is not None and self.next_working is not None:
                    break
        else:
            raise StopIteration(HOLIDAY_EXHAUSTED)

    @property
    def prev_holiday(self) -> DateObj:
        for holiday in reversed(self.holidays):
            if holiday.trade_date < self.today and not holiday.working:
                return DateObj(holiday.trade_date.as_str, date_fmt=self.date_fmt)

        return None

    @property
    def prev_working(self) -> DateObj:

        for holiday in reversed(self.holidays):
            if holiday.trade_date < self.today and holiday.working:
                return DateObj(holiday.trade_date.as_str, date_fmt=self.date_fmt)

        return None


@dataclass
class WorkingDayDate:
    given_date: str
    market_holidays: Union[List[MarketHolidayType], MarketHolidays]
    working_day: DateObj = field(init=False)
    market_timings: MarketTimingType
    date_fmt: str
    today: Optional[date] = None

    @property
    def day(self):
        return self.working_day

    def compare_time_cutoff(self) -> DateObj:
        date_ = DateObj(self.given_date, date_fmt=self.date_fmt)
        tomorrow: DateObj = date_ + BDay()
        yesterday: DateObj = date_ - BDay()
        cut_off = self.market_timings.time_cutoff
        now = datetime.now(tz=self.market_timings.tz).time()

        if date_ > tomorrow and date_ > yesterday:
            return date_

        if date_ < tomorrow and date_ < yesterday:
            return date_

        if cut_off > now:
            if date_ == self.today:
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
        self.market_timings = MarketTimings(**self.market_timings)

        if self.today is None:
            self.today = datetime.now(tz=self.market_timings.tz).today().date()

        now = datetime.now(tz=self.market_timings.tz).time()

        if (
            DateObj(self.given_date, self.date_fmt) == self.today
            and self.market_timings.start_time <= now <= self.market_timings.time_cutoff
        ):
            self.working_day = self.compare_time_cutoff()
        else:
            self.working_day = DateObj(self.given_date, self.date_fmt)

        if not isinstance(self.market_holidays, MarketHolidays):
            self.market_holidays = MarketHolidays(
                self.market_holidays, date_fmt=self.date_fmt
            )

    @property
    def next_business_day(self) -> DateObj:

        today = self.day
        tomorrow = today + BDay()

        if tomorrow == self.market_holidays.next_holiday:
            tomorrow = tomorrow + BDay()

        if self.market_holidays.next_working > today:
            if self.market_holidays.next_working < tomorrow:
                tomorrow = self.market_holidays.next_holiday

        return tomorrow

    @property
    def previous_business_day(self) -> DateObj:

        today = self.day
        yesterday = today - BDay()

        if (
            today not in self.market_holidays
            and today < datetime.now(tz=self.market_timings.tz).today()
        ):
            return today

        if yesterday == self.market_holidays.next_holiday:
            yesterday = yesterday - BDay()

        if self.market_holidays.prev_working is not None:
            if (
                self.market_holidays.prev_working < today
                and self.market_holidays.prev_working > yesterday
            ):
                yesterday = self.market_holidays.prev_working

        return yesterday

    def __add__(self, days: int) -> "WorkObj":
        count_days = 0
        iter_work_day = self.day
        while count_days < days:
            iter_work_day = WorkingDayDate(
                iter_work_day.as_str, self.market_holidays
            ).next_business_day
            count_days += 1

        return WorkingDayDate(
            iter_work_day.as_str, self.market_holidays, date_fmt=self.date_fmt
        )

    def __sub__(self, days: int) -> "WorkObj":
        count_days = days
        iter_work_day = self.day
        while count_days > 0:
            iter_work_day = WorkingDayDate(
                iter_work_day.as_str, self.market_holidays, date_fmt=self.date_fmt
            ).previous_business_day
            count_days -= 1

        return WorkingDayDate(
            iter_work_day.as_str, self.market_holidays, date_fmt=self.date_fmt
        )
