import pytz


def utc_to_timezone(datetime_utc, timezone_name):
    timezone = pytz.timezone(timezone_name)
    datetime = datetime_utc.replace(tzinfo=pytz.utc).astimezone(timezone)
    return timezone.normalize(datetime)


def to_camel_case(s):
    parts = s.split('_')
    return parts[0] + ''.join(p.title() for p in parts[1:])
