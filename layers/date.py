from datetime import datetime, timedelta, timezone
from dataclasses import dataclass


@dataclass()
class Date:
    date: datetime = None
    is_date: bool = isinstance(date, datetime)

    def get_date_in_iso_format(self, utc: int = -3) -> str:
        if self.is_date:
            return self.date.isoformat()
        return self.get_now(utc=utc).isoformat()

    @staticmethod
    def get_timezone(utc: int = -3) -> timezone:
        return timezone(timedelta(hours=utc))

    def get_now(self, utc: int = -3) -> datetime:
        return datetime.now(tz=self.get_timezone(utc=utc))

    def add_date(self, **kwargs) -> datetime:
        if self.is_date:
            return self.date + timedelta(**kwargs)
        return self.get_now(utc=kwargs.get("utc", -3)) + timedelta(**kwargs)
