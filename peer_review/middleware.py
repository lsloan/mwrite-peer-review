from django.conf import settings
from django.utils.deprecation import MiddlewareMixin
from django_user_agents.middleware import UserAgentMiddleware


# TODO remove when django-user-agents fixes https://github.com/selwin/django-user_agents/issues/13
class FixedUserAgentMiddleware(MiddlewareMixin, UserAgentMiddleware):
    pass


def safari_iframe_launch_middleware(get_response):
    def middleware(request):

        safari_first_launch = request.path == '/' and \
                              request.user_agent.browser.family == 'Safari' and \
                              settings.SESSION_COOKIE_NAME not in request.COOKIES

        if safari_first_launch:
            print('safari first launch')

        return get_response(request)
    return middleware
