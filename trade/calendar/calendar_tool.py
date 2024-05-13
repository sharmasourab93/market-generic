from typing import List, NewType

from trade.calendar.calendar_data import (
    DateObj,
    MarketHolidayType,
    MarketTimingType,
    WorkingDayDate,
)


class MarketCalendar:
    # Provide the following arguments
    # 1. Today's Date in str format in DATE_FMT
    # 2. List of Market Holidays
    # 3. Market Timings (Which can be used as a default value).

    def __init__(
        self,
        today: NewType("DateFormat", str),
        date_fmt: str,
        market_holidays: List[MarketHolidayType],
        market_timings: MarketTimingType,
    ):
        self.today = today
        self.working_day = WorkingDayDate(
            self.today,
            market_holidays,
            market_timings=market_timings,
            date_fmt=date_fmt,
        )

    @property
    def prev_day(self) -> DateObj:
        return self.working_day.previous_business_day

    @property
    def next_day(self) -> DateObj:
        return self.working_day.next_business_day

    @property
    def curr_day(self):
        return self.working_day.working_day
