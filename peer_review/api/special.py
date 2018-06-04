import logging

from django.conf import settings
from django.http import JsonResponse
from django.views.generic import TemplateView
from django.views.decorators.csrf import requires_csrf_token

LOGGER = logging.getLogger(__name__)

@requires_csrf_token
def permission_denied(request, exception, template_name=''):
    if request.user.is_authenticated:
        username = 'user %s' % request.user.username

    else:
        username = 'unauthenticated user'
    lti_launch_params = request.session.get('lti_launch_params')
    if lti_launch_params:
        params_desc = lti_launch_params
    else:
        params_desc = 'nonexistent'
    LOGGER.warning(
        'Permission denied for %s to %s with LTI launch parameters %s',
        username, request.get_full_path(), params_desc
    )

    return JsonResponse(
        {'error': 'You do not have access to the specified resource.'},
        status_code=403
    )


def not_found(request, exception, template_name=''):
    return JsonResponse(
        {'error': 'The specified resource was not found.'},
        status_code=404
    )


def server_error(request, template_name=''):
    return JsonResponse(
        {'error': 'An internal server error occurred.'},
        status_code=500
    )


class SafariLaunchPopup(TemplateView):
    template_name = 'safari_launch_popup.html'

    def get(self, request, *args, **kwargs):
        response = super(SafariLaunchPopup, self).get(request, *args, **kwargs)
        response.set_cookie(settings.SAFARI_LAUNCH_COOKIE, True, httponly=True, secure=True)
        return response
