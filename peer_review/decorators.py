import json

from functools import wraps

from django.http import JsonResponse, HttpResponseForbidden
from django.core.exceptions import PermissionDenied
from django.template import loader, TemplateDoesNotExist
from django.utils.encoding import force_text
from django.views.decorators.csrf import requires_csrf_token
from django.views.defaults import ERROR_403_TEMPLATE_NAME

from rolepermissions.roles import get_user_roles
from toolz.functoolz import thread_first, compose

from peer_review.views.special import logger


def login_required_or_raise(view):
    def wrapper(request):
        if not request.user.is_authenticated:
            raise PermissionDenied
        else:
            return view(request)
    return wrapper


# necessary because rolepermissions.decorators.has_role_decorator only supports single role
def has_one_of_roles(**kwargs):
    def decorator(view):
        @wraps(view)
        def wrapper(request):
            valid_roles = kwargs['roles']
            user_roles = get_user_roles(request.user)
            if any(r in valid_roles for r in user_roles):
                return view(request)
            else:
                raise PermissionDenied




# TODO needs to support models and querysets
def json_response(view):
    def wrapper(request):
        return thread_first(request, view, JsonResponse)
    return wrapper


authenticated_json_endpoint = compose(login_required_or_raise, json_response)


# adapted from django.views.defaults.permission_denied
@requires_csrf_token
def permission_denied(request, exception, template_name=ERROR_403_TEMPLATE_NAME):
    """
    Permission denied (403) handler.

    Templates: :template:`403.html`
    Context: None

    If the template does not exist, an Http403 response containing the text
    "403 Forbidden" (as per RFC 7231) will be returned.
    """

    # M-Write Peer Review customization starts here
    if request.user.is_authenticated:
        username = 'user %s' % request.user.username

    else:
        username = 'unauthenticated user'
    lti_launch_params = request.session.get('lti_launch_params')
    if lti_launch_params:
        params_desc = lti_launch_params
    else:
        params_desc = 'nonexistent'
    logger.warning('Permission denied for %s to %s with LTI launch parameters %s'
                   % (username, request.get_full_path(), params_desc))
    # M-Write Peer Review customization ends here

    try:
        template = loader.get_template(template_name)
    except TemplateDoesNotExist:
        if template_name != ERROR_403_TEMPLATE_NAME:
            # Reraise if it's a missing custom template.
            raise
        return HttpResponseForbidden('<h1>403 Forbidden</h1>', content_type='text/html')
    return HttpResponseForbidden(
        template.render(request=request, context={'exception': force_text(exception)})
    )
