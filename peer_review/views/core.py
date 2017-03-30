import json
import logging
from itertools import chain
from django.db.models import Q
from django.db import transaction
from django.http import HttpResponse, Http404
from django.template.loader import render_to_string
from django.views.generic import TemplateView
from toolz.itertoolz import unique
from toolz.dicttoolz import keymap
from toolz.functoolz import thread_last
from peer_review.util import to_snake_case
from peer_review.views.special import LtiView
from peer_review.etl import persist_assignments, AssignmentValidation
from peer_review.models import Rubric, Criterion, CanvasAssignment, PeerReviewDistribution, CanvasSubmission

logger = logging.getLogger(__name__)


class UnauthorizedView(TemplateView):
    template_name = '403.html'


# TODO need authz -- only teachers can access
class RubricCreationFormView(LtiView, TemplateView):
    template_name = 'rubric_creation_form.html'

    class ReviewsInProgressException(Exception):
        pass

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
            try:
                review_is_in_progress = PeerReviewDistribution.objects.get(rubric=existing_rubric) \
                                                              .is_distribution_complete
            except PeerReviewDistribution.DoesNotExist:
                review_is_in_progress = False
        else:
            review_is_in_progress = False
        existing_criteria = Criterion.objects.filter(rubric=existing_rubric) if existing_rubric else None
        existing_prompt = existing_rubric.reviewed_assignment if existing_rubric else None
        existing_revision = existing_rubric.revision_assignment if existing_rubric else None
        fetched_assignments = persist_assignments(course_id)
        assignments = list(self._get_unclaimed_assignments(course_id))
        if existing_prompt:
            assignments.insert(0, existing_prompt)
        if existing_revision:
            assignments.insert(0, existing_revision)
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
            'potential_prompts_and_rubrics': json.dumps({a.id: a.title for a in assignments}),
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

    # noinspection PyMethodMayBeStatic
    def post(self, request, *args, **kwargs):
        params = keymap(to_snake_case, json.loads(request.body.decode('utf-8')))
        passback_assignment_id = int(kwargs['assignment_id'])
        if 'criteria' not in params or len(params['criteria']) < 1:
            return HttpResponse('Missing criteria.', status=400)
        try:
            prompt_assignment_id = int(params['prompt_assignment'])
        except ValueError:
            return HttpResponse('Prompt assignment was not an integer.', status=400)
        if 'prompt_assignment' not in params or not params['prompt_assignment'].strip():
            return HttpResponse('Missing prompt assignment.', status=400)
        if 'rubric_description' not in params or not params['rubric_description'].strip():
            return HttpResponse('Missing rubric description.', status=400)
        if 'revision_assignment' in params and params['revision_assignment'].strip():
            revision_assignment_id = int(params['revision_assignment'])
        else:
            revision_assignment_id = None
        rubric_description = params['rubric_description'].strip()
        criteria = [Criterion(description=c['description']) for c in params['criteria']]
        try:
            with transaction.atomic():
                prompt_assignment = CanvasAssignment.objects.get(id=prompt_assignment_id)
                passback_assignment = CanvasAssignment.objects.get(id=passback_assignment_id)
                revision_assignment = CanvasAssignment.objects.get(id=revision_assignment_id)
                rubric, created = Rubric.objects.update_or_create(reviewed_assignment=prompt_assignment_id,
                                                                  defaults={'description': rubric_description,
                                                                            'reviewed_assignment': prompt_assignment,
                                                                            'passback_assignment': passback_assignment,
                                                                            'revision_assignment': revision_assignment})
                if not created:
                    try:
                        if PeerReviewDistribution.objects.get(rubric_id=rubric.id).is_distribution_complete:
                            raise RubricCreationFormView.ReviewsInProgressException
                    except PeerReviewDistribution.DoesNotExist:
                        pass
                    Criterion.objects.filter(rubric_id=rubric.id).delete()
                rubric.save()
                for c in criteria:
                    c.rubric_id = rubric.id
                    c.save()
            return HttpResponse(status=201)
        except RubricCreationFormView.ReviewsInProgressException:
            return HttpResponse('Rubric is read-only because reviews are in progress.', status=403)


# TODO need authz -- only students can access. refrained some implemented permissions check part until I research
# TODO Django's authz system
class PeerReviewView(LtiView, TemplateView):

    def get_context_data(self, **kwargs):
        try:
            submission = CanvasSubmission.objects.get(id=kwargs['submission_id'])
        except CanvasSubmission.DoesNotExist:
            raise Http404
        rubric = Rubric.objects.get(reviewed_assignment=submission.assignment)
        criteria = Criterion.objects.filter(rubric=rubric)
        return {
            'submission': submission,
            'rubric': rubric,
            'criteria': criteria
        }
