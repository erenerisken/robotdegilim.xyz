import datetime
from logging.handlers import TimedRotatingFileHandler
from typing import Optional
import pytz

from src.config import app_constants

# Istanbul timezone via pytz (present in requirements)
TZ_TR = pytz.timezone("Europe/Istanbul")


def time_converter_factory(tz=TZ_TR):
    """Return a time converter suitable for logging.Formatter.converter.

    Usage:
        fmt = logging.Formatter('%(asctime)s ...')
        fmt.converter = time_converter_factory(TZ_TR)
    """

    def _converter(secs: float):
        return datetime.datetime.fromtimestamp(secs, tz).timetuple()

    return _converter


class TzTimedRotatingFileHandler(TimedRotatingFileHandler):
    """TimedRotatingFileHandler that computes rollover using a timezone.

    Ensures midnight rollovers happen at local midnight of the provided tz
    (e.g., Europe/Istanbul), properly handling DST transitions.
    """

    def __init__(
        self,
        filename: str,
        when: str = "midnight",
        interval: int = 1,
        backupCount: int = 3,
        encoding: Optional[str] = app_constants.log_encoding,
        delay: bool = False,
        atTime: Optional[datetime.time] = None,
        tz=TZ_TR,
    ) -> None:
        self.tz = tz
        super().__init__(
            filename,
            when=when,
            interval=interval,
            backupCount=backupCount,
            encoding=encoding,
            delay=delay,
            utc=False,
            atTime=atTime,
        )

    def computeRollover(self, currentTime: int) -> int:
        # Align midnight rollover to timezone midnight for 'midnight'
        if isinstance(self.when, str) and self.when.upper() == "MIDNIGHT":
            ct = datetime.datetime.fromtimestamp(float(currentTime), self.tz)
            next_day = ct + datetime.timedelta(days=self.interval)
            next_midnight = next_day.replace(hour=0, minute=0, second=0, microsecond=0)
            return int(next_midnight.timestamp())
        return super().computeRollover(currentTime)
