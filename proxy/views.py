from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin


class IndexView(LoginRequiredMixin, TemplateView):
    template_name = 'index.html'
    login_url = '/unauthorized'
    redirect_field_name = ''


class UnauthorizedView(TemplateView):
    template_name = '403.html'
