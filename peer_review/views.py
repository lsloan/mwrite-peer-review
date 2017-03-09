import logging
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from httpproxy.views import HttpProxy

# TODO remove when django-http-proxy fixes https://github.com/yvandermeer/django-http-proxy/issues/25
from django.http import HttpResponse
from django.utils.six.moves import urllib


logger = logging.getLogger(__name__)


# TODO remove when django-http-proxy fixes https://github.com/yvandermeer/django-http-proxy/issues/25
class FixedHttpProxy(HttpProxy):
    def get_response(self, body=None, headers=None):
        request_url = self.get_full_url(self.url)
        request = self.create_request(request_url, body=body, headers={} if not headers else headers)
        try:
            response = urllib.request.urlopen(request)
            response_body = response.read()
            status = response.getcode()
            content_type = response.headers['content-type']
        except urllib.error.HTTPError as e:
            response_body = e.read()
            status = e.code
            content_type = e.hdrs['content-type']
        logger.debug(self._msg % response_body)
        return HttpResponse(response_body, status=status, content_type=content_type)


class LtiView(LoginRequiredMixin):
    login_url = '/unauthorized'
    redirect_field_name = ''


class LtiProxyView(FixedHttpProxy, LtiView):
    pass


class IndexView(LtiView, TemplateView):
    template_name = 'index.html'

    def get_context_data(self, **kwargs):
        context = super(IndexView, self).get_context_data(**kwargs)
        context['launch_params'] = self.request.session['lti_launch_params']
        return context


class UnauthorizedView(TemplateView):
    template_name = '403.html'
