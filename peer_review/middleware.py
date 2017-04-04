import logging
from django.conf import settings
from django.shortcuts import render_to_response
from django.utils.deprecation import MiddlewareMixin
from django_user_agents.middleware import UserAgentMiddleware

logger = logging.getLogger(__name__)


# TODO remove when django-user-agents fixes https://github.com/selwin/django-user_agents/issues/13
class FixedUserAgentMiddleware(MiddlewareMixin, UserAgentMiddleware):
    pass


def safari_iframe_launch_middleware(get_response):
    def middleware(request):
        if request.path == '/launch' and \
           request.user_agent.browser.family == 'Safari' and \
           settings.SAFARI_LAUNCH_COOKIE not in request.COOKIES:
            logger.debug('Unauthenticated Safari user detected, serving Safari landing page')
            return render_to_response('safari_launch_iframe.html', {'referer': request.META['HTTP_REFERER']})
        else:
            response = get_response(request)
        return response
    return middleware
