import json
import logging
from functools import partial
from collections import Iterable

from django.http import HttpResponse
from django.core.exceptions import PermissionDenied

from rolepermissions.roles import get_user_roles
from toolz.dicttoolz import keymap
from toolz.functoolz import thread_first, compose

from peer_review.util import to_camel_case

logger = logging.getLogger(__name__)


def login_required_or_raise(view):
    def wrapper(*args, **kwargs):
        request = args[0]
        if not request.user.is_authenticated:
            raise PermissionDenied
        else:
            return view(*args, **kwargs)
    return wrapper


# necessary because rolepermissions.decorators.has_role_decorator only supports single role
def has_one_of_roles(**kwargs):
    valid_roles = kwargs['roles']

    def decorator(view):
        def wrapper(*args, **kwargs):
            request = args[0]
            user_roles = [r.get_name() for r in get_user_roles(request.user)]
            if any(r in valid_roles for r in user_roles):
                return view(*args, **kwargs)
            else:
                raise PermissionDenied
        return wrapper
    return decorator


# TODO think about pagination for large collections
def json_response(view):
    camel_caser = partial(keymap, to_camel_case)

    def wrapper(*args, **kwargs):
        data = view(*args, **kwargs)
        is_iterable = isinstance(data, Iterable)
        is_dict = isinstance(data, dict)

        if is_iterable and not is_dict:
            content = list(map(camel_caser, data))
        else:
            content = camel_caser(data)

        return HttpResponse(content=json.dumps(content),
                            content_type='application/json')
    return wrapper


authenticated_json_endpoint = compose(login_required_or_raise, json_response)


def authorized_json_endpoint(**kwargs):
    valid_roles = kwargs['roles']

    def decorator(view):
        has_roles_decorator = has_one_of_roles(roles=valid_roles)
        decorators = thread_first(view,
                                  json_response,
                                  has_roles_decorator,
                                  login_required_or_raise)

        def wrapper(request, *args, **kwargs):
            return decorators(request, *args, **kwargs)
        return wrapper
    return decorator
