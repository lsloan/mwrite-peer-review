import re
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
        url_match = re.search('^/course/(?P<course_id>[0-9]+)/launch$', request.path)
        browser_is_safari = request.user_agent.browser.family == 'Safari'
        safari_cookie_exists = settings.SAFARI_LAUNCH_COOKIE not in request.COOKIES

        if url_match and browser_is_safari and safari_cookie_exists:
            logger.debug('Unauthenticated Safari user detected, serving Safari landing page')
            context = {
                'referer': request.META['HTTP_REFERER'],
                'course_id': url_match.group('course_id')
            }
            return render_to_response('safari_launch_iframe.html', context=context)
        else:
            response = get_response(request)
        return response

    return middleware
