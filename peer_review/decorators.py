import json
import logging
from functools import partial

from django.http import HttpResponse
from django.core.exceptions import PermissionDenied

from rolepermissions.roles import get_user_roles
from toolz.dicttoolz import keymap
from toolz.functoolz import thread_first, compose

from djangolti.backends import LtiBackend
from peer_review.exceptions import APIException
from peer_review.util import camel_case_keys, snake_case_keys, \
    transform_data_structure, object_to_json

LOGGER = logging.getLogger(__name__)


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

            userRoles = [LtiBackend.determine_role(request.session['lti_launch_params']['roles'])]

            if any(r in valid_roles for r in userRoles):
                return view(*args, **kwargs)
            else:
                raise PermissionDenied
        return wrapper
    return decorator


# TODO think about pagination for large collections
def json_response(view, default_status_code=200):
    def wrapper(*args, **kwargs):
        try:
            data = view(*args, **kwargs)
            status_code = default_status_code
        except APIException as ex:
            data = ex.data
            status_code = ex.status_code
        content = transform_data_structure(data, dict_transform=camel_case_keys)
        return HttpResponse(
            status=status_code,
            content=json.dumps(content, default=object_to_json),
            content_type='application/json'
        )
    return wrapper


# this decorator ensures that a user is can only access resources under the course they launched on.
# it effectively means that a user can only be logged into one course at a time.
def launch_course_matches(view):
    def wrapper(*args, **kwargs):
        request = args[0]
        if 'course_id' in kwargs:
            launch_course_id = request.session['lti_launch_params']['custom_canvas_course_id']
            requested_course_id = kwargs['course_id']
            if requested_course_id != launch_course_id:
                LOGGER.warning('Requested course ID %s does not match LTI launch course ID %s for user %s'
                               % (requested_course_id, launch_course_id, request.user.email))
                raise PermissionDenied
        return view(*args, **kwargs)
    return wrapper

authenticated_endpoint = compose(login_required_or_raise, launch_course_matches)
authenticated_json_endpoint = compose(authenticated_endpoint, json_response)


def authorized_endpoint(**kwargs):
    valid_roles = kwargs['roles']

    def decorator(view):
        has_roles_decorator = has_one_of_roles(roles=valid_roles)
        decorators = thread_first(view,
                                  has_roles_decorator,
                                  launch_course_matches,
                                  login_required_or_raise)

        def wrapper(request, *args, **kwargs):
            return decorators(request, *args, **kwargs)
        return wrapper
    return decorator


# TODO is there a simple, pythonic way to compose with kwargs?
def authorized_json_endpoint(**kwargs):
    def decorator(view):
        authorization_decorator = authorized_endpoint(**kwargs)
        decorators = thread_first(view,
                                  json_response,
                                  authorization_decorator)
        def wrapper(request, *args, **kwargs):
            return decorators(request, *args, **kwargs)
        return wrapper
    return decorator


def json_body(view):
    def wrapper(*args, **kwargs):
        request = args[0]
        body = transform_data_structure(
            json.loads(request.body),
            dict_transform=snake_case_keys
        )
        new_args = args + (body,)
        return view(*new_args, **kwargs)
    return wrapper
