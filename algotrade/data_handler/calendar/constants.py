from datetime import date, datetime
from zoneinfo import ZoneInfo

from pytz import timezone


ADHOC_MARKET_TIME_OFF = ["22-Jan-2024"]
ADHOC_MARKET_TIME_ON = ["20-Jan-2024", "2-Mar-2024"]

WEEKDAY_TO_ISO = {
    "Monday": 1,
    "Tuesday": 2,
    "Wednesday": 3,
    "Thursday": 4,
    "Friday": 5,
    "Saturday": 6,
    "Sunday": 7,
}
HOLIDAY_EXHAUSTED = "Holiday List exhausted. Update Holiday List"


# Time related Constants used along with Market Calendar Module.
TIME_ZONE = ZoneInfo("Asia/Kolkata")
TZ = timezone("Asia/Kolkata")
DATE = date.today()
TODAY = datetime.now(tz=TIME_ZONE).date()
TIME_OFFSET = "1600"
TIME_OFFSET_FMT = "%H%M"
TIME_CUTOFF = datetime.strptime(TIME_OFFSET, TIME_OFFSET_FMT).time()
DATE_FMT = "%d-%b-%Y"
ISO_WEEK_RANGE = (0, 6)

# Fixed Market Start Time and End time for any market day.
MARKET_START = "0915"
MARKET_CLOSE = "1530"
MARKET_AMO = ("1540", "1600")
TIME_STRF = "%H%M"

# Market Start Time and Close Time.
MARKET_START_TIME = datetime.strptime(MARKET_START, TIME_STRF).time()
MARKET_CLOSE_TIME = datetime.strptime(MARKET_CLOSE, TIME_STRF).time()
MARKET_AMO_TIME = tuple(
    list(datetime.strptime(i, TIME_STRF).time() for i in MARKET_AMO)
)
