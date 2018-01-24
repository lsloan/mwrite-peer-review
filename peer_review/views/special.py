import logging

from django import forms, http
from django.conf import settings
from django.utils.encoding import force_text
from django.views.generic import TemplateView, FormView
from django.template import loader, TemplateDoesNotExist
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.defaults import ERROR_403_TEMPLATE_NAME
from django.views.decorators.csrf import requires_csrf_token

from toolz.functoolz import thread_last

logger = logging.getLogger(__name__)


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


class SafariLaunchPopup(TemplateView):
    template_name = 'safari_launch_popup.html'

    def get(self, request, *args, **kwargs):
        response = super(SafariLaunchPopup, self).get(request, *args, **kwargs)
        response.set_cookie(settings.SAFARI_LAUNCH_COOKIE, True, httponly=True, secure=True)
        return response


# adapted from django.views.defaults.permission_denied
@requires_csrf_token
def permission_denied(request, exception, template_name=ERROR_403_TEMPLATE_NAME):
    """
    Permission denied (403) handler.

    Templates: :template:`403.html`
    Context: None

    If the template does not exist, an Http403 response containing the text
    "403 Forbidden" (as per RFC 7231) will be returned.
    """

    # M-Write Peer Review customization starts here
    if request.user.is_authenticated:
        username = 'user %s' % request.user.username

    else:
        username = 'unauthenticated user'
    lti_launch_params = request.session.get('lti_launch_params')
    if lti_launch_params:
        params_desc = lti_launch_params
    else:
        params_desc = 'nonexistent'
    logger.warning('Permission denied for %s to %s with LTI launch parameters %s'
                   % (username, request.get_full_path(), params_desc))
    # M-Write Peer Review customization ends here

    try:
        template = loader.get_template(template_name)
    except TemplateDoesNotExist:
        if template_name != ERROR_403_TEMPLATE_NAME:
            # Reraise if it's a missing custom template.
            raise
        return http.HttpResponseForbidden('<h1>403 Forbidden</h1>', content_type='text/html')
    return http.HttpResponseForbidden(
        template.render(request=request, context={'exception': force_text(exception)})
    )
