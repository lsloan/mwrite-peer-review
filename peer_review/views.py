import logging
from toolz.dicttoolz import merge, valmap
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
    def _get_required_headers(lti_launch_params):
        try:
            headers = {'roles':                            lti_launch_params['roles'],
                       'custom_canvas_user_id':            lti_launch_params['custom_canvas_user_id'],
                       'lis_person_contact_email_primary': lti_launch_params['lis_person_contact_email_primary']}
        except KeyError as e:
            key = e.args[0]
            raise RuntimeError('LTI launch parameter \'%s\' not found' % key) from e
        return headers

    @staticmethod
    def _get_optional_headers(lti_launch_params):
        headers = {}
        if 'custom_canvas_course_id' in lti_launch_params or 'custom_canvas_assignment_id' in lti_launch_params:
            if 'custom_canvas_course_id' in lti_launch_params:
                headers['custom_canvas_course_id'] = lti_launch_params['custom_canvas_course_id']
            if 'custom_canvas_assignment_id' in lti_launch_params:
                headers['custom_canvas_assignment_id'] = lti_launch_params['custom_canvas_assignment_id']
        else:
            raise RuntimeError('LTI launch parameters must contain \'%s\' or \'%s\'' %
                               ('custom_canvas_course_id', 'custom_canvas_assignment_id'))
        return headers

    def get_proxy_headers(self):
        lti_launch_params = self.request.session['lti_launch_params']
        headers = merge(self._get_required_headers(lti_launch_params), self._get_optional_headers(lti_launch_params))
        return valmap(str, headers)

    def get_response(self, body=None, headers=None):
        headers = merge(headers if headers else {}, self.get_proxy_headers())
        return super(LtiProxyView, self).get_response(body, headers)


class IndexView(LtiView, TemplateView):
    template_name = 'index.html'

    def get_context_data(self, **kwargs):
        context = super(IndexView, self).get_context_data(**kwargs)
        context['launch_params'] = self.request.session['lti_launch_params']
        return context


class UnauthorizedView(TemplateView):
    template_name = '403.html'
