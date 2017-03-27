import pytz


def utc_to_timezone(datetime_utc, timezone_name):
    timezone = pytz.timezone(timezone_name)
    datetime = datetime_utc.replace(tzinfo=pytz.utc).astimezone(timezone)
    return timezone.normalize(datetime)
