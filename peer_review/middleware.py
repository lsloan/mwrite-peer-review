from django.utils.deprecation import MiddlewareMixin
from django_user_agents.middleware import UserAgentMiddleware


# TODO remove when django-user-agents fixes https://github.com/selwin/django-user_agents/issues/13
class FixedUserAgentMiddleware(MiddlewareMixin, UserAgentMiddleware):
    pass
