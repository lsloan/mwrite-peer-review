from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from httpproxy.views import HttpProxy


class LtiView(LoginRequiredMixin):
    login_url = '/unauthorized'
    redirect_field_name = ''


class LtiProxyView(HttpProxy, LtiView):
    pass


class IndexView(LtiView, TemplateView):
    template_name = 'index.html'


class UnauthorizedView(TemplateView):
    template_name = '403.html'


