import logging

from django.http import HttpResponse, HttpResponseBadRequest
from django.core.exceptions import PermissionDenied

from django.shortcuts import redirect
from django.views.generic import TemplateView, View
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.clickjacking import xframe_options_exempt
from django.contrib import auth
from django.contrib import messages
from django.conf import settings
from django.urls import reverse
from django.shortcuts import render
from django.utils.decorators import method_decorator

from lti import ToolConfig
from lti.contrib.django import DjangoToolProvider

logger = logging.getLogger(__name__)


@method_decorator(xframe_options_exempt, name='dispatch')
class IndexView(TemplateView):
    template_name = 'djangolti/index.html'
    http_method_names = ('get',)


@method_decorator(xframe_options_exempt, name='dispatch')
class ConfigView(View):
    http_method_names = ('get',)

    def get(self, request):
        launch_url = request.build_absolute_uri(reverse('lti:launch'))

        lti_tool_config = ToolConfig(
            title='(django)',
            description='foo',
            launch_url=launch_url,
            secure_launch_url=launch_url,
        )

        return HttpResponse(lti_tool_config.to_xml(), content_type='text/xml')


@method_decorator(xframe_options_exempt, name='dispatch')
@method_decorator(csrf_exempt, name='dispatch')
class LaunchView(View):
    http_method_names = ('get', 'post',)

    def get(self, request):
        messages.error(request,
                       'Must login by connecting from course site')
        return render(request, 'djangolti/index.html', status=400)

    def post(self, request):
        if request.user.is_authenticated:
            # end any existing session
            auth.logout(request)

        launch_request = DjangoToolProvider.from_django_request(
            request=request)

        user = auth.authenticate(request=request,
                                 lti_launch_request=launch_request)

        if hasattr(settings, 'LTI_APP_REDIRECT'):
            app_redirect = settings.LTI_APP_REDIRECT
        else:
            app_redirect = '/'

        if user and user.is_anonymous:
            request.user = user
            logger.debug('LTI using AnonymousUser')
        elif user:
            request.user = user
            auth.login(request, user)

            logger.debug('LTI user logged in (%s)' % user.username)

            # stash the launch params into the session for later use
            request.session['lti_launch_params'] = dict(
                launch_request.launch_params)
        else:
            raise PermissionDenied

        if request.GET.get('debug') in ('1', 'on', 'true'):
            context = {
                'redirect': app_redirect,
                'launch_params': sorted(launch_request.to_params().items()),
                'post': request.POST,
            }
            return render(request, 'djangolti/debug.html', context)

        return redirect(app_redirect)


@method_decorator(xframe_options_exempt, name='dispatch')
class ReturnView(View):
    http_method_names = ('get')

    def get(self, request):
        try:
            launch_params = request.session['lti_launch_params']
            return_url = launch_params['launch_presentation_return_url']
        except KeyError:
            return_url = None

        if return_url:
            return redirect(return_url)
        else:
            messages.warning(request, 'Return URL not found')
            return render(request, 'djangolti/index.html')
