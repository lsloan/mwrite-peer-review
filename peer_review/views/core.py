import json
import logging
from itertools import chain
from django.db.models import Q
from django.template.loader import render_to_string
from django.views.generic import TemplateView
from toolz.functoolz import thread_last
from toolz.itertoolz import unique
from peer_review.views.special import LtiView
from peer_review.etl import persist_assignments, AssignmentValidation
from peer_review.models import Rubric, Criterion, CanvasAssignment, PeerReviewDistribution

logger = logging.getLogger(__name__)


class UnauthorizedView(TemplateView):
    template_name = '403.html'


# TODO test for existing rubrics
class RubricCreationFormView(LtiView, TemplateView):
    template_name = 'rubric_creation_form.html'

    @staticmethod
    def _get_unclaimed_assignments(course_id):
        query = Q(reviewed_assignment__course_id=course_id) | Q(revision_assignment__course_id=course_id)
        rubrics = Rubric.objects.filter(query)
        claimed_assignments = thread_last(rubrics,
                                          (map, lambda r: (r.reviewed_assignment_id, r.revision_assignment_id)),
                                          chain.from_iterable,
                                          unique,
                                          (filter, lambda i: i is not None))
        return CanvasAssignment.objects.filter(course_id=course_id, is_peer_review_assignment=False) \
                                       .exclude(id__in=claimed_assignments)

    def get_context_data(self, **kwargs):
        course_id = int(kwargs['course_id'])
        passback_assignment_id = int(kwargs['assignment_id'])
        try:
            existing_rubric = Rubric.objects.get(passback_assignment_id=passback_assignment_id)
        except Rubric.DoesNotExist:
            existing_rubric = None
        if existing_rubric:
            review_is_in_progress = PeerReviewDistribution.objects.get(rubric=existing_rubric).is_distribution_complete
        else:
            review_is_in_progress = False
        existing_criteria = Criterion.objects.filter(rubric=existing_rubric) if existing_rubric else None
        existing_prompt = existing_rubric.reviewed_assignment if existing_rubric else None
        existing_revision = existing_rubric.revision_assignment if existing_rubric else None
        fetched_assignments = persist_assignments(course_id)
        unclaimed_assignments = self._get_unclaimed_assignments(course_id)
        if review_is_in_progress:
            mode = 'view'
        elif existing_rubric:
            mode = 'edit'
        else:
            mode = 'create'
        criterion_card_html = render_to_string('criterion.html', {'description': '', 'read_only': False, 'counter': 1})
        return {
            'course_id': course_id,
            'passback_assignment_id': passback_assignment_id,
            'potential_prompts_and_rubrics': json.dumps({a.id: a.title for a in unclaimed_assignments}),
            'validations': json.dumps({assignment.id: assignment.validation for assignment in fetched_assignments},
                                      default=AssignmentValidation.json_default),
            'should_show_revision_info': not (review_is_in_progress and not existing_revision),
            'mode': mode,
            'existing_prompt': existing_prompt,
            'existing_revision': existing_revision,
            'existing_rubric': existing_rubric,
            'existing_criteria': existing_criteria,
            'review_is_in_progress': review_is_in_progress,
            'criterion_card_html': criterion_card_html.replace('\n', '')
        }
