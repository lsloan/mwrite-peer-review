import logging
from toolz.dicttoolz import merge, valmap
from toolz.functoolz import thread_last
from httpproxy.views import HttpProxy
from django import forms

from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import TemplateView, FormView
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
            content_type = response.headers['Content-Type']
            content_disposition = response.headers.get('Content-Disposition')
        except urllib.error.HTTPError as e:
            response_body = e.read()
            status = e.code
            content_type = e.hdrs['content-type']
            content_disposition = None
        logger.debug(self._msg % response_body)
        proxy_response = HttpResponse(response_body, status=status, content_type=content_type)
        if content_disposition:
            proxy_response['Content-Disposition'] = content_disposition
        return proxy_response


class LoginRequiredNoRedirectMixin(LoginRequiredMixin):
    raise_exception = True


# TODO need to rearrange required/optional LTI headers; not quite right (but good enough for now)
@method_decorator(csrf_exempt, name='dispatch')
class LtiProxyView(LoginRequiredNoRedirectMixin, FixedHttpProxy):

    @staticmethod
    def _get_required_headers(lti_launch_params):
        try:
            headers = {'roles':                            ','.join(lti_launch_params['roles']),
                       'custom_canvas_user_id':            lti_launch_params['custom_canvas_user_id'],
                       'lis_person_contact_email_primary': lti_launch_params['lis_person_contact_email_primary'],
                       'context_title':                    lti_launch_params['context_title']}
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
        logger.debug('lti launch params = %s' % str(lti_launch_params))
        headers = merge(self._get_required_headers(lti_launch_params), self._get_optional_headers(lti_launch_params))
        return valmap(str, headers)

    def get_response(self, body=None, headers=None):
        headers = merge(headers if headers else {}, self.get_proxy_headers())
        return super(LtiProxyView, self).get_response(body, headers)


# noinspection PyClassHasNoInit
class LtiParamsForm(forms.Form):
    custom_canvas_course_id = forms.CharField(label='Course ID')
    custom_canvas_user_id = forms.CharField(label='User ID')
    roles = forms.CharField(label='Roles')
    lis_person_contact_email_primary = forms.EmailField(label='Email')
    context_title = forms.CharField(label='Course Name')


class DebugLtiParamsView(LoginRequiredMixin, FormView):
    template_name = 'debug_lti.html'
    success_url = '/'
    form_class = LtiParamsForm

    def get_form(self, form_class=None):
        lti_launch_params = dict(self.request.session.get('lti_launch_params') or {})
        if 'roles' in lti_launch_params:
            lti_launch_params['roles'] = ','.join(lti_launch_params['roles'])
        return LtiParamsForm(initial=lti_launch_params, data=self.request.POST or None)

    def form_valid(self, form):
        lti_launch_params = self.request.session.get('lti_launch_params') or {}
        roles = thread_last(form.cleaned_data['roles'], lambda rs: rs.split(','), (map, lambda s: s.strip()), list)
        form.cleaned_data['roles'] = roles
        self.request.session['lti_launch_params'] = {**form.cleaned_data, **lti_launch_params}
        return super(DebugLtiParamsView, self).form_valid(form)
