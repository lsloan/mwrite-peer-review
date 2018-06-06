import re
import logging
from django.conf import settings
from django.shortcuts import render_to_response
from django.utils.deprecation import MiddlewareMixin
from django_user_agents.middleware import UserAgentMiddleware

LOGGER = logging.getLogger(__name__)


# TODO remove when django-user-agents fixes https://github.com/selwin/django-user_agents/issues/13
class FixedUserAgentMiddleware(MiddlewareMixin, UserAgentMiddleware):
    pass


def safari_iframe_launch_middleware(get_response):

    def middleware(request):

        browser_is_safari = request.user_agent.browser.family == 'Safari'
        safari_launch_cookie_missing = settings.SAFARI_LAUNCH_COOKIE not in request.COOKIES
        request_is_for_launch = re.search('^/launch$', request.path)

        LOGGER.debug(
            'safari launch middleware for %s info = %s, %s, %s, %s',
            request.path,
            request.method,
            browser_is_safari,
            safari_launch_cookie_missing,
            request_is_for_launch
        )

        if browser_is_safari and safari_launch_cookie_missing and request_is_for_launch and request.method == 'POST':
            LOGGER.debug('Unauthenticated Safari user detected, serving Safari landing page')
            context = {
                'tool_url': request.META['HTTP_REFERER'],
            }
            response = render_to_response('safari_launch_iframe.html', context=context)

        response = get_response(request)

        return response

    return middleware
