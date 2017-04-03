from django.utils.deprecation import MiddlewareMixin
from django_user_agents.middleware import UserAgentMiddleware


# TODO remove when django-user-agents fixes https://github.com/selwin/django-user_agents/issues/13
class FixedUserAgentMiddleware(MiddlewareMixin, UserAgentMiddleware):
    pass


def safari_iframe_launch_middleware(get_response):
    def middleware(request):

        if request.path == '/' and request.user_agent.browser.family == 'Safari' and not request.user.is_authenticated:
            print('need to send the user to the safari landing page')

        return get_response(request)
    return middleware
