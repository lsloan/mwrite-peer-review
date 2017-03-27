import logging
from django.views.generic import TemplateView
from peer_review.views.special import LtiView
from peer_review.etl import persist_assignments
from peer_review.models import Rubric, Criterion

logger = logging.getLogger(__name__)


class UnauthorizedView(TemplateView):
    template_name = 'peer_review/403.html'


class RubricCreationFormView(LtiView, TemplateView):
    template_name = 'peer_review/rubric_creation_form.html'

    def get_context_data(self, **kwargs):
        rubric = Rubric.objects.get(passback_assignment_id=self.request.session['custom_canvas_assignment_id'])
        criteria = Criterion.objects.filter(rubric=rubric)
        assignments = persist_assignments(self.request.session['custom_canvas_course_id'])
        return {
            'validations': {assignment.id: assignment.validation for assignment in assignments},
            'rubric': rubric,
            'criteria': criteria
        }
