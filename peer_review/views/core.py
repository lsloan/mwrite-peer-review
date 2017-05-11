import json
import logging
from datetime import datetime
from itertools import chain

from django.db import transaction
from django.db.models import Q, Count, Case, When, Value, BooleanField
from django.http import HttpResponse, Http404
from django.shortcuts import redirect
from django.template.loader import render_to_string
from django.views.generic import View, TemplateView
from rolepermissions.checkers import has_role
from rolepermissions.mixins import HasRoleMixin
from toolz.functoolz import thread_last
from toolz.itertoolz import unique

from peer_review.etl import persist_assignments, AssignmentValidation
from peer_review.models import Rubric, Criterion, CanvasAssignment, PeerReviewDistribution, CanvasSubmission, \
    PeerReview, PeerReviewComment
from peer_review.util import parse_json_body

logger = logging.getLogger(__name__)


class UnauthorizedView(TemplateView):
    template_name = '403.html'


# TODO needs to handle assignment level launches
class IndexView(HasRoleMixin, View):
    allowed_roles = ['instructor', 'student']

    # noinspection PyMethodMayBeStatic
    def get(self, request, *args, **kwargs):
        if has_role(request.user, 'instructor'):
            response = redirect('/dashboard/instructor')
        elif has_role(request.user, 'student'):
            response = redirect('/dashboard/student')
        else:
            raise RuntimeError('Unrecognized role for user %s' % request.user)
        return response


class RubricCreationFormView(HasRoleMixin, TemplateView):
    allowed_roles = 'instructor'
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
        existing_prompt = existing_rubric.reviewed_assignment if existing_rubric else None
        existing_revision = existing_rubric.revision_assignment if existing_rubric else None
        fetched_assignments = persist_assignments(course_id)
        assignments = list(self._get_unclaimed_assignments(course_id))
        if existing_prompt:
            assignments.insert(0, existing_prompt)
        if existing_revision:
            assignments.insert(0, existing_revision)
        criterion_card_html = render_to_string('criterion_card.html', {'removable': True})
        return {
            'course_id': course_id,
            'passback_assignment_id': passback_assignment_id,
            'potential_prompts_and_rubrics': json.dumps({a.id: a.title for a in assignments}),
            'validations': json.dumps({assignment.id: assignment.validation for assignment in fetched_assignments},
                                      default=AssignmentValidation.json_default),
            'should_show_revision_info': not (review_is_in_progress and not existing_revision),
            'existing_prompt': existing_prompt,
            'existing_revision': existing_revision,
            'existing_rubric': existing_rubric,
            'review_is_in_progress': review_is_in_progress,
            'criterion_card_html': criterion_card_html.replace('\n', '')
        }

    # noinspection PyMethodMayBeStatic
    def post(self, request, *args, **kwargs):
        params = parse_json_body(request.body)
        passback_assignment_id = int(kwargs['assignment_id'])

        if not params.get('prompt_id'):
            return HttpResponse('Missing prompt assignment.', status=400)
        else:
            prompt_assignment_id = params['prompt_id']

        revision_assignment_id = params['revision_id']

        if 'description' not in params or not params['description'].strip():
            return HttpResponse('Missing rubric description.', status=400)
        else:
            rubric_description = params['description'].strip()

        if 'criteria' not in params or len(params['criteria']) < 1:
            return HttpResponse('Missing criteria.', status=400)
        else:
            criteria = [Criterion(description=criterion) for criterion in params['criteria']]

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
class PeerReviewView(HasRoleMixin, TemplateView):
    allowed_roles = 'student'
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


class InstructorDashboardView(HasRoleMixin, TemplateView):
    allowed_roles = 'instructor'
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


class StudentDashboardView(HasRoleMixin, TemplateView):
    allowed_roles = 'student'
    template_name = 'student_dashboard.html'

    def get_context_data(self, **kwargs):
        course_id = self.request.session['lti_launch_params']['custom_canvas_course_id']
        student_id = self.request.session['lti_launch_params']['custom_canvas_user_id']
        rubrics = Rubric.objects.filter(reviewed_assignment__course_id=course_id,
                                        peer_review_distribution__is_distribution_complete=True)\
                                .order_by('reviewed_assignment__due_date_utc')
        reviews = [(rubric.reviewed_assignment.title,
                    {'due_date': rubric.passback_assignment.due_date_utc,
                     'submissions': rubric.reviewed_assignment.canvas_submission_set
                                                              .filter(peerreview__student_id=student_id)
                                                              .annotate(Count('peerreview__comments'))
                                                              .annotate(peer_review_complete=Case(
                                                                  When(peerreview__comments__count__gte=
                                                                       rubric.criteria.count(),
                                                                       then=Value(True)),
                                                                  default=Value(False),
                                                                  output_field=BooleanField()))})
                   for rubric in rubrics]
        received_reviews = [(rubric.reviewed_assignment.title,
                             rubric.reviewed_assignment.canvas_submission_set
                                                       .filter(peerreview__submission__author_id=student_id)
                                                       .annotate(Count('peerreview__comments'))
                                                       .filter(peerreview__comments__count__gte=rubric.criteria.count()))
                            for rubric in rubrics]
        return {'reviews_to_complete': reviews,
                'reviews_received': received_reviews}


class ReviewsByStudentView(HasRoleMixin, TemplateView):
    allowed_roles = 'instructor'
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
                'author': author,
                'completed': completed_reviews,
                'total': peer_reviews.count()
            })
        return {'reviews': reviews,
                'rubric': rubric}
