import re
import pytz


def utc_to_timezone(datetime_utc, timezone_name):
    timezone = pytz.timezone(timezone_name)
    datetime = datetime_utc.replace(tzinfo=pytz.utc).astimezone(timezone)
    return timezone.normalize(datetime)


def to_camel_case(s):
    parts = s.split('_')
    return parts[0] + ''.join(p.title() for p in parts[1:])


def to_snake_case(s):
    inter = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', s)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', inter).lower()
