from datetime import date, datetime, time, timezone


def str_to_datetime(date_str: str, date_format: str = '%Y-%m-%dT%H:%M:%S.%fZ') -> datetime | None:
    try:
        return datetime.strptime(date_str, date_format)
    except ValueError:
        return None


def iso_str_to_datetime(date_str: str) -> datetime | None:
    if data := str_to_datetime(date_str, '%Y-%m-%dT%H:%M:%S.%fZ'):
        return data
    return None


def str_to_date(date_str: str, date_format: str = '%Y-%m-%d') -> date | None:
    if data := str_to_datetime(date_str, date_format):
        return data.date()
    return None


def iso_str_to_date(date_str: str,) -> date | None:
    if data := str_to_date(date_str):
        return data
    return None


def datetime_to_iso_str(date: datetime | None) -> str | None:
    if date is None:
        return None
    return date.astimezone(timezone.utc).strftime('%Y-%m-%dT%H:%M:%S.%fZ')


def date_to_iso_str(date_val: date | None) -> str | None:
    if date_val is None:
        return None

    return date_val.strftime('%Y-%m-%d')


def time_to_str(time_val: time | None) -> str | None:
    if time_val is None:
        return None
    return time_val.strftime('%H:%M:%S')
