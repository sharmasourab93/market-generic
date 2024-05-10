from typing import List, NewType

from algotrade.data_handler.calendar.calendar_data import (
    MarketHolidayType,
    MarketTimingType,
    WorkingDayDate,
)


class MarketCalendar:
    def __init__(
        self,
        today: NewType("DateFormat", str),
        market_name: str,
        market_holidays: List[MarketHolidayType],
        market_timings: MarketTimingType,
    ):
        self.today = today
        self.working_day = WorkingDayDate(
            self.today, market_holidays, market_timings=market_timings
        )
        self.market_name = market_name
