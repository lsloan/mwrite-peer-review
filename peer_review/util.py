import re
import json
import pytz
from collections import Iterable

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


def transform_data_structure(data, dict_transform=lambda x: x):
    is_dict = isinstance(data, dict)
    is_string = isinstance(data, str)
    is_collection = isinstance(data, Iterable) and not is_dict and not is_string

    if is_collection:
        content = [
            transform_data_structure(item, dict_transform=dict_transform)
            for item in data
        ]
    elif is_dict:
        # TODO doesn't preserve order for OrderedDict, defaultdict factory, etc.
        content = dict_transform({
            k: transform_data_structure(v, dict_transform=dict_transform)
            for k, v in data.items()
        })
    else:
        content = data

    return content


def some(predicate, collection):
    return any(map(predicate, collection))


def keymap_all(fn, collection):
    return (keymap(fn, d) for d in collection)


def fetchall_dicts(cursor):
    columns = [col[0] for col in cursor.description]
    return [
        dict(zip(columns, row))
        for row in cursor.fetchall()
    ]
