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
        url_match = re.search('^/launch$', request.path)
        browser_is_safari = request.user_agent.browser.family == 'Safari'
        safari_cookie_missing = settings.SAFARI_LAUNCH_COOKIE not in request.COOKIES
        have_launch_params = 'lti_launch_params' in request.session

        if url_match and browser_is_safari and safari_cookie_missing  and have_launch_params:
            LOGGER.debug('Unauthenticated Safari user detected, serving Safari landing page')
            context = {
                'referer': request.META['HTTP_REFERER'],
                'course_id': request.session['lti_launch_params']['context_id']
            }
            return render_to_response('safari_launch_iframe.html', context=context)
        else:
            response = get_response(request)
        return response

    return middleware
