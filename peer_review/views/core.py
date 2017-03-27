import logging
from django.views.generic import TemplateView

logger = logging.getLogger(__name__)


class UnauthorizedView(TemplateView):
    template_name = '403.html'
