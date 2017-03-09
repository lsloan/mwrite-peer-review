import logging
from toolz.dicttoolz import merge
from httpproxy.views import HttpProxy
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin


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

    @staticmethod
    def _launch_params_to_proxy_headers(lti_launch_params, param_keys):
        try:
            headers = {}
            for param in param_keys:
                headers[param] = lti_launch_params[param]
        except KeyError as e:
            key = e.args[0]
            raise RuntimeError('LTI launch parameters does not contain \'%s\'' % key) from e
        return headers

    def get_response(self, body=None, headers=None):
        params = ['custom_canvas_course_id', 'custom_canvas_assignment_id', 'custom_canvas_user_id',
                  'lis_person_contact_email_primary', 'roles']
        headers = merge(headers if headers else {},
                        self._launch_params_to_proxy_headers(self.request.session['lti_launch_params'], params))
        return super(LtiProxyView, self).get_response(body, headers)


class IndexView(LtiView, TemplateView):
    template_name = 'index.html'

    def get_context_data(self, **kwargs):
        context = super(IndexView, self).get_context_data(**kwargs)
        context['launch_params'] = self.request.session['lti_launch_params']
        return context


class UnauthorizedView(TemplateView):
    template_name = '403.html'
