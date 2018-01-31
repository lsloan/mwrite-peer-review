import io
import os
import csv
import json
import logging
import mimetypes
from datetime import datetime
from itertools import chain, zip_longest
from collections import OrderedDict

import dateutil.parser
from dateutil.tz import tzutc
from django.conf import settings
from django.db import transaction
from django.db.models import Q, F, Count, Case, When, Value, BooleanField, Max
from django.http import HttpResponse, Http404, JsonResponse
from django.shortcuts import redirect
from django.views.generic import View, TemplateView
from django.core.exceptions import PermissionDenied
from rolepermissions.roles import get_user_roles
from rolepermissions.checkers import has_role
from rolepermissions.mixins import HasRoleMixin
from toolz.functoolz import thread_last
from toolz.itertoolz import unique

from peer_review.models import *
from peer_review.util import parse_json_body, some
from peer_review.decorators import authenticated_json_endpoint
from peer_review.etl import persist_assignments, AssignmentValidation

logger = logging.getLogger(__name__)


# TODO refactor / move me
@authenticated_json_endpoint
def user_roles(request):
    roles = [role.get_name() for role in get_user_roles(request.user)]
    return JsonResponse({'roles': roles})


# TODO needs to handle assignment level launches
class CourseIndexView(HasRoleMixin, View):
    allowed_roles = ['instructor', 'student']

    # noinspection PyMethodMayBeStatic
    def get(self, request, *args, **kwargs):
        course_id = int(self.request.session['lti_launch_params']['custom_canvas_course_id'])
        course_title = self.request.session['lti_launch_params']['context_title']

        CanvasCourse.objects.update_or_create(id=course_id, defaults={'name': course_title})

        route_params = [course_id]

        url_pattern = '/course/%s/dashboard/%s'
        if has_role(request.user, 'instructor'):
            assignment_id = self.request.session['lti_launch_params'].get('custom_canvas_assignment_id')
            if assignment_id and assignment_id.strip():
                route_params.append(int(assignment_id))
                url_pattern = '/course/%d/rubric/assignment/%d'
            else:
                route_params.append('instructor')
        elif has_role(request.user, 'student'):
            route_params.append('student')
        else:
            raise RuntimeError('Unrecognized role for user %s' % request.user)

        return redirect(url_pattern % tuple(route_params))


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

        fetched_assignments = persist_assignments(course_id)

        try:
            passback_assignment = CanvasAssignment.objects.get(id=passback_assignment_id)
        except CanvasAssignment.DoesNotExist:
            raise Http404

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
        assignments = list(self._get_unclaimed_assignments(course_id))
        if existing_prompt:
            assignments.insert(0, existing_prompt)
        if existing_revision:
            assignments.insert(0, existing_revision)
        criteria = [c.description for c in existing_rubric.criteria.all()] if existing_rubric else None
        return {
            'course_id': course_id,
            'passback_assignment_id': passback_assignment_id,
            'passback_assignment': passback_assignment,
            'potential_prompts_and_rubrics': json.dumps({a.id: a.title for a in assignments}),
            'validations': json.dumps({assignment.id: assignment.validation for assignment in fetched_assignments},
                                      default=AssignmentValidation.json_default),
            'existing_prompt': existing_prompt,
            'existing_revision': existing_revision,
            'existing_rubric': existing_rubric,
            'criteria': json.dumps(criteria),
            'review_is_in_progress': review_is_in_progress,
            'title': self.request.session['lti_launch_params']['context_title'],
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

        if 'peer_review_open_date' not in params or not params['peer_review_open_date'].strip():
            return HttpResponse('Missing peer review open date.', status=400)
        else:
            peer_review_open_date = dateutil.parser.parse(params['peer_review_open_date'])

        if 'peer_review_open_date_is_prompt_due_date' not in params:
            return HttpResponse('Missing peer review open date is prompt due date flag.', status=400)
        else:
            peer_review_open_date_is_prompt_due_date = params['peer_review_open_date_is_prompt_due_date']

        # TODO disabled (for now) due to lack of demand
        # if 'distribute_peer_reviews_for_sections' not in params:
        #     return HttpResponse('Missing flag for section-only peer review distribution')
        # else:
        #     distribute_peer_reviews_for_sections = params['distribute_peer_reviews_for_sections']
        distribute_peer_reviews_for_sections = False

        logger.info('peer review open date = %s' % peer_review_open_date)

        try:
            with transaction.atomic():
                prompt_assignment = CanvasAssignment.objects.get(id=prompt_assignment_id)
                passback_assignment = CanvasAssignment.objects.get(id=passback_assignment_id)
                if revision_assignment_id:
                    revision_assignment = CanvasAssignment.objects.get(id=revision_assignment_id)
                else:
                    revision_assignment = None
                rubric_defaults = {
                    'description': rubric_description,
                    'reviewed_assignment': prompt_assignment,
                    'passback_assignment': passback_assignment,
                    'revision_assignment': revision_assignment,
                    'peer_review_open_date': peer_review_open_date,
                    'peer_review_open_date_is_prompt_due_date': peer_review_open_date_is_prompt_due_date,
                    'distribute_peer_reviews_for_sections': distribute_peer_reviews_for_sections
                }
                rubric, created = Rubric.objects.update_or_create(reviewed_assignment=prompt_assignment_id,
                                                                  defaults=rubric_defaults)
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

    ERROR_RESPONSE = HttpResponse('You cannot review this submission because it was not assigned to you.', status=403)
    ERROR_TEMPLATE = 'Student %d (%s) tried to access submission %d (by %s), but'

    # TODO use error template for error responses
    def get_context_data(self, **kwargs):

        student_id = self.request.session['lti_launch_params']['custom_canvas_user_id']
        submission_id = kwargs['submission_id']

        try:
            student = CanvasStudent.objects.get(id=student_id)
        except CanvasStudent.DoesNotExist:
            logger.warning('Student %d does not exist' % student_id)
            return PeerReviewView.ERROR_RESPONSE

        try:
            submission = CanvasSubmission.objects.get(id=submission_id)
        except CanvasSubmission.DoesNotExist:
            logger.warning('User \'%s\' (student id = %d) tried to access submission %d, which does not exist' %
                           (student.username, student.id, submission_id))
            return PeerReviewView.ERROR_RESPONSE

        try:
            PeerReview.objects.get(student=student, submission=submission)
        except PeerReview.DoesNotExist:
            logger.warning("""User \'%s\' (student id = %d) tried to access submission %d (by \'%s\')
                              but does not have permission!""" %
                           (student.username, student.id, submission.id, submission.author.username))
            return PeerReviewView.ERROR_RESPONSE

        rubric = Rubric.objects.get(reviewed_assignment=submission.assignment)
        criteria = Criterion.objects.filter(rubric=rubric)
        course = CanvasCourse.objects.get(id=int(kwargs['course_id']))
        return {
            'submission': submission,
            'rubric': rubric,
            'criteria': criteria,
            'title': course.name,
            'course_id': course.id
        }

    # noinspection PyMethodMayBeStatic
    def post(self, request, *args, **kwargs):

        student_id = self.request.session['lti_launch_params']['custom_canvas_user_id']
        try:
            student = CanvasStudent.objects.get(id=student_id)
        except CanvasStudent.DoesNotExist:
            logger.warning('Student %d does not exist' % student_id)
            return HttpResponse('That student does not exist.', status=400)

        submission_id = kwargs['submission_id']
        user_comments = parse_json_body(request.body)

        try:
            submission = CanvasSubmission.objects.get(id=submission_id)
        except CanvasSubmission.DoesNotExist:
            return Http404

        try:
            peer_review = PeerReview.objects.get(student_id=student_id, submission_id=submission_id)
        except PeerReview.DoesNotExist:
            logger.warning('Student %s tried to submit a review for a submission they were not assigned'
                           % student.username)
            return HttpResponse('You were not assigned that submission.', status=403)

        rubric = Rubric.objects.get(reviewed_assignment=submission.assignment)
        user_comment_criteria_ids = [com['criterion_id'] for com in user_comments]
        user_comment_criteria = Criterion.objects.filter(id__in=user_comment_criteria_ids)
        if user_comment_criteria.count() != rubric.criteria.count():
            logger.warning('Criterion IDs do not for review on submission %d for student "%s"'
                           % (submission_id, student.username))
            return HttpResponse('Criterion IDs do not match.', status=400)

        rubric_criteria_ids = map(lambda cri: cri.id, rubric.criteria.all())
        existing_comments = PeerReviewComment.objects.filter(peer_review=peer_review,
                                                             criterion_id__in=rubric_criteria_ids)
        if rubric.criteria.count() == existing_comments.count():
            logger.warning('Student "%s" tried to submit a review that has already been completed' % student.username)
            return HttpResponse('This review has already been completed.', status=400)
        elif existing_comments.count() > 0:
            logger.warning('Somehow %d has only %d out of %d comments for %d!!!',
                           student_id, existing_comments.count(), rubric.criteria.count(), submission_id)

        comments = [PeerReviewComment(criterion=Criterion.objects.get(id=c['criterion_id']),
                                      comment=c['comment'],
                                      commented_at_utc=datetime.now(tzutc()),
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
        course_id = int(self.request.session['lti_launch_params']['custom_canvas_course_id'])
        fetched_assignments = {a.id: a for a in persist_assignments(course_id)}
        peer_review_assignments = CanvasAssignment.objects.filter(id__in=fetched_assignments.keys(),
                                                                  is_peer_review_assignment=True) \
                                                          .order_by('due_date_utc')

        reviews = []
        prompt_assignments = []
        for assignment in peer_review_assignments:
            rubric = Rubric.objects.filter(passback_assignment=assignment)
            num_reviews = 0
            received_reviews = 0
            if rubric:
                number_of_criteria = rubric[0].criteria.count()

                prompt_assignment = assignment.rubric_for_review.reviewed_assignment
                prompt_assignment.validation = fetched_assignments[prompt_assignment.id].validation
                prompt_assignments.append(prompt_assignment)

                submissions = prompt_assignment.canvas_submission_set.annotate(Count('peer_reviews_for_submission'))

                for submission in submissions:
                    num_reviews += submission.peer_reviews_for_submission__count
                    peer_reviews_per_submission = CanvasSubmission.num_comments_each_review_per_submission.__get__(submission)\
                                                                .filter(received__gte = number_of_criteria)
                    received_reviews += len(peer_reviews_per_submission)

            reviews.append({
                'assignment': assignment,
                'num_reviews': num_reviews,
                'received_reviews': received_reviews,
            })

        return {
            'title': self.request.session['lti_launch_params']['context_title'],
            'course_id': course_id,
            'validation_info': json.dumps({a.id: a.validation for a in prompt_assignments},
                                          default=AssignmentValidation.json_default),
            'reviews': reviews,
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
        reviews = OrderedDict()
        for rubric in rubrics:
            submissions = rubric.reviewed_assignment.canvas_submission_set  \
                .filter(peer_reviews_for_submission__student_id=student_id) \
                .annotate(Count('peer_reviews_for_submission__comments'))   \
                .annotate(peer_review_complete=Case(
                    When(peer_reviews_for_submission__comments__count__gte=rubric.criteria.count(), then=Value(True)),
                    default=Value(False),
                    output_field=BooleanField()
                ))
            details = {
                'title': rubric.reviewed_assignment.title,
                'due_date': rubric.passback_assignment.due_date_utc,
                'submissions': submissions
            }
            if some(lambda s: not s.peer_review_complete, details['submissions']):
                reviews[rubric.reviewed_assignment_id] = details

        finished_prompt_id = self.request.GET.get('finished')
        if finished_prompt_id and len(reviews) == 0:
            finished_prompt = CanvasAssignment.objects.get(id=int(finished_prompt_id))
        else:
            finished_prompt = None

        submissions_reviewed = \
            PeerReview.objects.filter(submission__author_id=student_id,
                                      submission__assignment__course_id=course_id,
                                      submission__assignment__is_peer_review_assignment=False) \
                              .order_by('submission__assignment__due_date_utc') \
                              .annotate(Count('comments', distinct=True)) \
                              .annotate(Count('submission__assignment__rubric_for_prompt__criteria', distinct=True)) \
                              .filter(comments__count__gte=
                                      F('submission__assignment__rubric_for_prompt__criteria__count')) \
                              .values_list('submission')

        # see https://code.djangoproject.com/ticket/10060
        review_submission_counts = OrderedDict()
        for submission_id, in submissions_reviewed:
            if submission_id in review_submission_counts:
                review_submission_counts[submission_id] += 1
            else:
                review_submission_counts[submission_id] = 1
        reviews_received = [(CanvasSubmission.objects.get(id=submission_id), number_of_reviews)
                            for submission_id, number_of_reviews in review_submission_counts.items()]

        course = CanvasCourse.objects.get(id=int(kwargs['course_id']))

        return {'reviews_to_complete': reviews.values(),
                'reviews_received': reviews_received,
                'finished_prompt': finished_prompt,
                'title': course.name,
                'course_id': course.id}


class AssignmentStatus(HasRoleMixin, TemplateView):
    allowed_roles = 'instructor'
    template_name = 'assignment_status.html'

    # TODO see how much of this can be accomplished with aggregation via the ORM
    def get_context_data(self, **kwargs):

        try:
            rubric = Rubric.objects.get(id=kwargs['rubric_id'])
        except Rubric.DoesNotExist:
            return Http404

        submissions = rubric.reviewed_assignment.canvas_submission_set.all()

        reviews = []
        sections = set()
        for submission in submissions:
            total_completed_num = submission.total_completed_by_a_student.count()
            completed_reviews_num = submission.num_comments_each_review_per_student       \
                                              .filter(completed__gte=rubric.num_criteria) \
                                              .count()

            total_received_num = submission.total_received_of_a_student.count()
            received_reviews_num = submission.num_comments_each_review_per_submission   \
                                             .filter(received__gte=rubric.num_criteria) \
                                             .count()

            if rubric.sections.all():
                author_sections = submission.author.sections.filter(id__in=rubric.sections.values_list('id', flat=True))
            else:
                author_sections = submission.author.sections.all()

            for section in author_sections:
                sections.add(section)

            reviews.append({
                'author':          submission.author,
                'total_completed': total_completed_num,
                'completed':       completed_reviews_num,
                'total_received':  total_received_num,
                'received':        received_reviews_num,
                'sections':        author_sections,
                'json_sections':   json.dumps(list(author_sections.values_list('id', flat=True)))
            })

        sections = list(sections)
        sections.sort(key=lambda s: s.name)

        course = CanvasCourse.objects.get(id=int(kwargs['course_id']))
        return {
            'course_id': course.id,
            'title':     course.name,
            'reviews':   reviews,
            'rubric':    rubric,
            'sections':  sections
        }


class SingleReviewDetailView(HasRoleMixin, TemplateView):
    allowed_roles = ['student', 'instructor']
    template_name = 'single_review_details.html'

    def get_context_data(self, **kwargs):

        user_id = int(self.request.session['lti_launch_params']['custom_canvas_user_id'])
        user_is_instructor = has_role(self.request.user, 'instructor')

        submission = CanvasSubmission.objects.get(id=kwargs['submission_id'])
        if not user_is_instructor and user_id != submission.author_id:
            raise PermissionDenied

        peer_review_ids = PeerReview.objects.filter(submission=submission).values_list('id', flat=True)
        rubric = submission.assignment.rubric_for_prompt
        details = [(criterion,
                    PeerReviewComment.objects.filter(criterion=criterion, peer_review_id__in=peer_review_ids)
                                             .order_by('peer_review__submission__author_id'))
                   for criterion in rubric.criteria.all()]

        course_id = int(kwargs['course_id'])
        context = {'title': CanvasCourse.objects.get(id=course_id).name,
                   'prompt_title': submission.assignment.title,
                   'user_is_instructor': user_is_instructor,
                   'review': details}
        if user_is_instructor:
            context['course_id'] = course_id
        return context


class ReviewsForAStudentView(HasRoleMixin, TemplateView):
    allowed_roles = 'instructor'
    template_name = 'reviews_for_a_student.html'

    def get_context_data(self, **kwargs):

        student = CanvasStudent.objects.get(id=kwargs['student_id'])

        assignments = CanvasSubmission.objects.filter(author__id=student.id).values('assignment')
        rubrics = Rubric.objects.filter(reviewed_assignment__in=assignments)

        reviews = []
        for rubric in rubrics:
            reviews.append({
                'rubric_id': rubric.id,
                'title': rubric.passback_assignment.title,
            })

        rubric = Rubric.objects.get(id=kwargs['rubric_id'])
        number_of_criteria = Rubric.num_criteria.__get__(rubric)
        submission = rubric.reviewed_assignment.canvas_submission_set.get(author__id=student.id)

        due_date_passed = datetime.now(tzutc()) > rubric.passback_assignment.due_date_utc

        completed = []
        completed_num = 0
        total_completed = CanvasSubmission.total_completed_by_a_student.__get__(submission)
        for peer_review in total_completed:
            completed_review = False
            submit_time = None
            comments = PeerReviewComment.objects.filter(peer_review__id=peer_review.id)
            if comments.count() >= number_of_criteria:
                submit_time = comments.aggregate(Max('commented_at_utc'))['commented_at_utc__max']
                completed_review = True
                completed_num += 1

            is_late = True if submit_time is None else submit_time > rubric.passback_assignment.due_date_utc

            completed.append({
                'student': peer_review.submission.author,
                'student_first_name': peer_review.submission.author.full_name.split()[0],
                'completed': completed_review,
                'submission': peer_review.submission,
                'submit_time': submit_time,
                'is_late': is_late,
                'review_status_incomplete': not completed_review and due_date_passed
            })

        received = []
        received_num = 0
        total_received = CanvasSubmission.total_received_of_a_student.__get__(submission)
        for peer_review in total_received:
            received_review = False
            submit_time = None
            comments = PeerReviewComment.objects.filter(peer_review__id=peer_review.id)
            if comments.count() >= number_of_criteria:
                submit_time = comments.aggregate(Max('commented_at_utc'))['commented_at_utc__max']
                received_review = True
                received_num += 1

            is_late = True if submit_time is None else submit_time > rubric.passback_assignment.due_date_utc

            if '@' in peer_review.student.username:
                reviewer_email = peer_review.student.username
            else:
                reviewer_email = '%s@umich.edu' % peer_review.student.username

            received.append({
                'student': peer_review.student,
                'student_first_name': peer_review.student.full_name.split()[0],
                'reviewer_email': reviewer_email,
                'received': received_review,
                'submit_time': submit_time,
                'is_late': is_late,
                'review_status_incomplete': not received_review and due_date_passed
            })

        if '@' in student.username:
            student_email = student.username
        else:
            student_email = '%s@umich.edu' % student.username

        course = CanvasCourse.objects.get(id=int(kwargs['course_id']))
        return {'prompt_title': rubric.reviewed_assignment.title,
                'rubric_id': rubric.id,
                'student_id': student.id,
                'student_name': student.full_name,
                'student_email': student_email,
                'student_first_name': student.full_name.split()[0],
                'reviews': reviews,
                'total_completed': len(total_completed),
                'completed_num': completed_num,
                'total_received': len(total_received),
                'received_num': received_num,
                'completed_and_received_reviews': zip_longest(completed, received),
                'submission': submission,
                'title': course.name,
                'course_id': course.id,
                'due_date_passed': due_date_passed}


class AllStudentsReviews(HasRoleMixin, TemplateView):
    allowed_roles = 'instructor'
    template_name = 'reviews_for_all_students.html'

    def get_context_data(self, **kwargs):
        course = CanvasCourse.objects.get(id=int(kwargs['course_id']))
        canvas_students = CanvasStudent.objects.filter(
            id__in=course.sections.all().values_list('students', flat=True)
        )

        student_data = []
        for student in canvas_students:
            sections = student.sections.all()
            student_data.append({
                'id': student.id,
                'name': student.sortable_name,
                'sections': sections,
                'json_sections': json.dumps(list(sections.values_list('id', flat=True)))
            })

        return {
            'course_id': course.id,
            'title': course.name,
            'sections': course.sections.all(),
            'students': student_data
        }


class OverviewForAStudent(HasRoleMixin, TemplateView):
    allowed_roles = 'instructor'
    template_name = 'overview_for_a_student.html'

    def get_context_data(self, **kwargs):

        student_id = kwargs['student_id']
        student = CanvasStudent.objects.get(id=student_id)

        assignments = CanvasSubmission.objects.filter(author__id=student_id).values('assignment')
        rubrics = Rubric.objects.filter(reviewed_assignment__in=assignments)

        reviews = []
        for rubric in rubrics:
            number_of_criteria = Rubric.num_criteria.__get__(rubric)

            submission = rubric.reviewed_assignment.canvas_submission_set.get(author__id=student_id)

            total_completed = CanvasSubmission.total_completed_by_a_student.__get__(submission)
            peer_reviews_completed = CanvasSubmission.num_comments_each_review_per_student.__get__(submission) \
                                                     .filter(completed__gte=number_of_criteria)
            completed_reviews = len(peer_reviews_completed)

            total_received = CanvasSubmission.total_received_of_a_student.__get__(submission)
            peer_reviews_received = CanvasSubmission.num_comments_each_review_per_submission.__get__(submission) \
                                                    .filter(received__gte=number_of_criteria)
            received_reviews = len(peer_reviews_received)

            reviews.append({
                'title': rubric.passback_assignment.title,
                'rubric_id': rubric.id,
                'total_completed': len(total_completed),
                'completed': completed_reviews,
                'total_received': len(total_received),
                'received': received_reviews,
            })

        course = CanvasCourse.objects.get(id=int(kwargs['course_id']))

        return {'title': course.name,
                'course_id': course.id,
                'student_id': student_id,
                'student_name': student.full_name,
                'student_first_name': student.full_name.split()[0],
                'reviews': reviews}


class OverviewDownload(HasRoleMixin, TemplateView):
    allowed_roles = 'instructor'

    def get(self, request, *args, **kwargs):

        output = io.StringIO()
        writer = csv.writer(output, delimiter=',', quoting=csv.QUOTE_MINIMAL)
        writer.writerow(['reviewer', 'author', 'criterion', 'comment'])

        assignments = CanvasSubmission.objects.filter(author__id=kwargs['student_id']).values('assignment')
        rubrics = Rubric.objects.filter(reviewed_assignment__in=assignments)

        for rubric in rubrics:
            submission = rubric.reviewed_assignment.canvas_submission_set.get(author__id=kwargs['student_id'])

            total_completed = CanvasSubmission.total_completed_by_a_student.__get__(submission)
            comments_completed = PeerReviewComment.objects.filter(peer_review__in=total_completed)
            for comment in comments_completed:
                writer.writerow([comment.peer_review.student.sortable_name, comment.peer_review.submission.author.sortable_name, comment.criterion.id, comment.comment])

            total_received = CanvasSubmission.total_received_of_a_student.__get__(submission)
            comments_received = PeerReviewComment.objects.filter(peer_review__in=total_received)
            for comment in comments_received:
                writer.writerow([comment.peer_review.student.sortable_name, comment.peer_review.submission.author.sortable_name, comment.criterion.id, comment.comment])

        response = HttpResponse(output.getvalue(), content_type="text/csv")
        response["Content-Disposition"] = "attachment"

        return response


class ReviewsDownload(HasRoleMixin, TemplateView):
    allowed_roles = 'instructor'

    def get(self, request, *args, **kwargs):

        output = io.StringIO()
        writer = csv.writer(output, delimiter=',', quoting=csv.QUOTE_MINIMAL)
        writer.writerow(['reviewer', 'author', 'criterion', 'comment'])

        rubric = Rubric.objects.get(id=kwargs['rubric_id'])
        submission = rubric.reviewed_assignment.canvas_submission_set.get(author__id=kwargs['student_id'])

        total_completed = CanvasSubmission.total_completed_by_a_student.__get__(submission)
        comments_completed = PeerReviewComment.objects.filter(peer_review__in=total_completed)

        for comment in comments_completed:
            writer.writerow([comment.peer_review.student.sortable_name, comment.peer_review.submission.author.sortable_name, comment.criterion.id, comment.comment])

        total_received = CanvasSubmission.total_received_of_a_student.__get__(submission)
        comments_received = PeerReviewComment.objects.filter(peer_review__in=total_received)
        for comment in comments_received:
            writer.writerow([comment.peer_review.student.sortable_name, comment.peer_review.submission.author.sortable_name, comment.criterion.id, comment.comment])

        response = HttpResponse(output.getvalue(), content_type="text/csv")
        response["Content-Disposition"] = "attachment"

        return response


class SubmissionDownloadView(HasRoleMixin, View):
    allowed_roles = ['instructor', 'student']

    def get(self, request, *args, **kwargs):

        submission_id = int(kwargs['submission_id'])

        if not has_role(request.user, 'instructor'):
            student_id = int(self.request.session['lti_launch_params']['custom_canvas_user_id'])
            submission_ids_for_review = PeerReview.objects.filter(student_id=student_id).values_list('submission_id',
                                                                                                     flat=True)
            submissions_by_author = CanvasSubmission.objects.filter(author_id=student_id).values_list('id', flat=True)
            if submission_id not in submission_ids_for_review and submission_id not in submissions_by_author:
                raise PermissionDenied

        try:
            submission = CanvasSubmission.objects.get(id=submission_id)
        except CanvasSubmission.DoesNotExist:
            raise Http404

        with open(os.path.join(settings.MEDIA_ROOT, 'submissions', submission.filename), 'rb') as submission_file:
            submission_bytes = submission_file.read()

        content_type = mimetypes.guess_type(submission.filename)[0] or 'application/octet-stream'
        response = HttpResponse(submission_bytes, content_type)
        response['Content-Disposition'] = 'attachment; filename="%s"' % submission.filename

        return response
