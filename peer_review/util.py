import re
import json
import pytz
from toolz.dicttoolz import keymap


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


# TODO what i really want here is something to recursively descend through the datastructure, snake-casing dict keys
# TODO right now this only works for dicts or lists of dicts
def parse_json_body(b):
    b_obj = json.loads(b.decode('utf-8'))
    if isinstance(b_obj, dict):
        return keymap(to_snake_case, b_obj)
    elif isinstance(b_obj, list):
        return list(map(lambda d: keymap(to_snake_case, d), b_obj))


def some(predicate, collection):
    return any(map(predicate, collection))


def fetchall_dicts(cursor):
    columns = [col[0] for col in cursor.description]
    return [
        dict(zip(columns, row))
        for row in cursor.fetchall()
    ]
