import json
import logging
from itertools import chain
from datetime import datetime
from django.db.models import Q
from django.db import transaction
from django.http import HttpResponse, Http404
from django.template.loader import render_to_string
from django.views.generic import TemplateView
from toolz.itertoolz import unique
from toolz.functoolz import thread_last
from peer_review.util import parse_json_body
from peer_review.views.special import LoginRequiredNoRedirectMixin
from peer_review.etl import persist_assignments, AssignmentValidation
from peer_review.models import Rubric, Criterion, CanvasAssignment, PeerReviewDistribution, CanvasSubmission, \
                               PeerReview, PeerReviewComment

logger = logging.getLogger(__name__)


class UnauthorizedView(TemplateView):
    template_name = '403.html'


# TODO need authz -- only teachers can access
class RubricCreationFormView(LoginRequiredNoRedirectMixin, TemplateView):
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
        params = parse_json_body(request.body)
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
        if 'revision_assignment' in params and params['revision_assignment'] and params['revision_assignment'].strip():
            revision_assignment_id = int(params['revision_assignment'])
        else:
            revision_assignment_id = None
        rubric_description = params['rubric_description'].strip()
        criteria = [Criterion(description=c['description']) for c in params['criteria']]
        try:
            with transaction.atomic():
                prompt_assignment = CanvasAssignment.objects.get(id=prompt_assignment_id)
                passback_assignment = CanvasAssignment.objects.get(id=passback_assignment_id)
                if revision_assignment_id:
                    revision_assignment = CanvasAssignment.objects.get(id=revision_assignment_id)
                else:
                    revision_assignment = None
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


# TODO needs validity checking and authz
class PeerReviewView(LoginRequiredNoRedirectMixin, TemplateView):
    template_name = 'review.html'

    def get_context_data(self, **kwargs):
        student_id = self.request.session['lti_launch_params']['custom_canvas_user_id']
        submission_id = kwargs['submission_id']
        try:
            PeerReview.objects.get(student_id=student_id, submission_id=submission_id)
        except PeerReview.DoesNotExist:
            return HttpResponse('You cannot review this submission because it was not assigned to you.', status=403)
        try:
            submission = CanvasSubmission.objects.get(id=submission_id)
        except CanvasSubmission.DoesNotExist:
            raise Http404
        rubric = Rubric.objects.get(reviewed_assignment=submission.assignment)
        criteria = Criterion.objects.filter(rubric=rubric)
        return {
            'submission': submission,
            'rubric': rubric,
            'criteria': criteria
        }

    # noinspection PyMethodMayBeStatic
    def post(self, request, *args, **kwargs):

        student_id = self.request.session['lti_launch_params']['custom_canvas_user_id']
        submission_id = kwargs['submission_id']
        user_comments = parse_json_body(request.body)

        try:
            submission = CanvasSubmission.objects.get(id=submission_id)
        except CanvasSubmission.DoesNotExist:
            return Http404

        try:
            peer_review = PeerReview.objects.get(student_id=student_id, submission_id=submission_id)
        except PeerReview.DoesNotExist:
            return HttpResponse('You were not assigned that submission.', status=403)

        rubric = Rubric.objects.get(reviewed_assignment=submission.assignment)
        user_comment_criteria_ids = [com['criterion_id'] for com in user_comments]
        user_comment_criteria = Criterion.objects.filter(id__in=user_comment_criteria_ids)
        if user_comment_criteria.count() != rubric.criterion_set.count():
            return HttpResponse('Criterion IDs do not match.', 400)

        rubric_criteria_ids = map(lambda cri: cri.id, rubric.criterion_set.all())
        existing_comments = PeerReviewComment.objects.filter(peer_review=peer_review,
                                                             criterion_id__in=rubric_criteria_ids)
        if rubric.criterion_set.count() == existing_comments.count():
            return HttpResponse('This review has already been completed.', 400)
        elif existing_comments.count() > 0:
            logger.warning('Somehow %d has only %d out of %d comments for %d!!!',
                           student_id, existing_comments.count(), rubric.criterion_set.count(), submission_id)

        commented_at_utc = datetime.utcnow()
        comments = [PeerReviewComment(criterion=Criterion.objects.get(id=c['criterion_id']),
                                      comment=c['comment'],
                                      commented_at_utc=commented_at_utc,
                                      peer_review=peer_review)
                    for c in user_comments]

        with transaction.atomic():
            existing_comments.delete()
            for comment in comments:
                comment.save()

        return HttpResponse(status=201)


class InstructorDashboardView(LoginRequiredNoRedirectMixin, TemplateView):
    template_name = 'instructor_dashboard.html'

    @staticmethod
    def get_rubric_for_review(assignment):
        rubric = None
        try:
            rubric = assignment.rubric_for_review
        except Rubric.DoesNotExist:
            pass
        return rubric

    def get_context_data(self, **kwargs):
        course_id = self.request.session['lti_launch_params']['custom_canvas_course_id']
        fetched_assignments = {a.id: a for a in persist_assignments(course_id)}
        peer_review_assignments = CanvasAssignment.objects.filter(id__in=fetched_assignments.keys(),
                                                                  is_peer_review_assignment=True) \
                                                          .order_by('due_date_utc')
        rubric_assignments = thread_last(peer_review_assignments,
                                         (map, InstructorDashboardView.get_rubric_for_review),
                                         (filter, lambda mr: mr is not None),
                                         (map, lambda r: (r.reviewed_assignment, r.revision_assignment)),
                                         chain.from_iterable,
                                         (filter, lambda ma: ma is not None),
                                         list)
        for assignment in rubric_assignments:
            assignment.validation = fetched_assignments[assignment.id].validation
        return {
            'title': self.request.session['lti_launch_params']['context_title'],
            'course_id': course_id,
            'assignments': peer_review_assignments,
            'validation_info': json.dumps({a.id: a.validation for a in rubric_assignments},
                                          default=AssignmentValidation.json_default)
        }


class ReviewsByStudentView(LoginRequiredNoRedirectMixin, TemplateView):
    template_name = 'reviews_by_student.html'

    def get_context_data(self, **kwargs):
        rubric = Rubric.objects.get(id=kwargs['rubric_id'])
        number_of_criteria = rubric.criteria.count()
        authors = map(lambda s: s.author,
                      rubric.reviewed_assignment.canvas_submission_set.order_by('author__sortable_name').all())
        reviews = []
        for author in authors:
            peer_reviews = PeerReview.objects.filter(student=author, submission__assignment=rubric.reviewed_assignment)
            completed_reviews = 0
            for peer_review in peer_reviews:
                if peer_review.comments.count() >= number_of_criteria:
                    completed_reviews += 1
            reviews.append({
                'author_name': author.sortable_name,
                'completed': completed_reviews,
                'total': peer_reviews.count()
            })
        return {'reviews': reviews}
