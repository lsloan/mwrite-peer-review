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
        logger.debug('(safari iframe) request.path = %s' % request.path)
        logger.debug('(safari iframe) request.user_agent.browser.family = %s' % request.user_agent.browser.family)
        logger.debug('(safari iframe) request.COOKIES = %s' % request.COOKIES)
        logger.debug('(safari iframe) request.META = %s' % request.META)
        logger.debug('(safari iframe) request.META[\'HTTP_REFERER\'] header = %s' % request.META['HTTP_REFERER'])

        if request.path == '/launch' and \
           request.user_agent.browser.family == 'Safari' and \
           settings.SESSION_COOKIE_NAME not in request.COOKIES:
            logger.debug('safari first launch')
            return render_to_response('safari_launch_iframe.html', {'referer': request.META['HTTP_REFERER']})
        else:
            response = get_response(request)
        return response

    return middleware
