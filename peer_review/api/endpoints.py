import logging
from itertools import chain

from rolepermissions.roles import get_user_roles
from django.core.exceptions import PermissionDenied, ObjectDoesNotExist
from django.views.decorators.http import require_POST

import peer_review.etl as etl
from peer_review.models import CanvasCourse, CanvasStudent, PeerReview, Rubric, PeerReviewEvaluation
from peer_review.queries import InstructorDashboardStatus, StudentDashboardStatus
from peer_review.api.util import merge_validations
from peer_review.util import to_camel_case, keymap_all
from peer_review.decorators import authorized_json_endpoint, authenticated_json_endpoint, json_body

log = logging.getLogger(__name__)


@authenticated_json_endpoint
def logged_in_user_details(request):
    roles = [role.get_name() for role in get_user_roles(request.user)]
    course_id = request.session['lti_launch_params']['custom_canvas_course_id']
    user_id = request.session['lti_launch_params']['custom_canvas_user_id']
    return {
        'username': request.user.username,
        'user_id': int(user_id),
        'course_id': int(course_id),
        'roles': roles
    }


# TODO refactor this based on what we're actually using on the new students list implementation
@authorized_json_endpoint(roles=['instructor'])
def all_students(request, course_id):
    etl.persist_sections(course_id)
    etl.persist_students(course_id)

    course_model = CanvasCourse.objects.get(id=course_id)
    course = {'id': course_model.id, 'name': course_model.name}

    students = []
    for student in CanvasStudent.objects.filter(course_id=course_id):
        sections = []
        for section in student.sections.filter(course_id=course_id):
            sections.append({
                'id': section.id,
                'name': section.name,
                'course': course
            })
        students.append({
            'id': student.id,
            'sortable_name': student.sortable_name,
            'full_name': student.full_name,
            'username': student.username,
            'sections': sections,
            'course': course
        })

    return students


@authorized_json_endpoint(roles=['instructor'])
def all_peer_review_assignment_details(request, course_id):
    etl.persist_course(course_id)
    assignments = etl.persist_assignments(course_id)
    fetched_assignment_ids = tuple(map(lambda a: a.id, assignments))

    details = InstructorDashboardStatus.get(course_id, fetched_assignment_ids)

    validations = {a.id: a.validation for a in assignments}
    details_with_validations = merge_validations(details, validations)

    return keymap_all(to_camel_case, details_with_validations)


def raise_if_not_current_user(request, user_id):
    logged_in_user_id = request.session['lti_launch_params']['custom_canvas_user_id']
    if logged_in_user_id != user_id:
        log.warning('User %s tried to access information for user %s without permission'
                    % (logged_in_user_id, user_id))
        raise PermissionDenied


def raise_if_peer_review_not_for_student(request, student_id, peer_review_id):
    if not PeerReview.objects.filter(id=peer_review_id, submission__author_id=student_id).exists():
        logged_in_user_id = request.session['lti_launch_params']['custom_canvas_user_id']
        log.warning('User %s tried to submit an invalid peer review evaluation for user %s and peer review %s'
                    % (logged_in_user_id, student_id, peer_review_id))
        raise PermissionDenied


@authorized_json_endpoint(roles=['student'])
def assigned_work(request, course_id, student_id):
    raise_if_not_current_user(request, student_id)
    return StudentDashboardStatus.assigned_work(course_id, student_id)


@authorized_json_endpoint(roles=['student'])
def completed_work(request, course_id, student_id):
    raise_if_not_current_user(request, student_id)
    return StudentDashboardStatus.completed_work(course_id, student_id)


def _denormalize_reviews(reviews):

    peer_review_ids = sorted(r.id for r in reviews)
    student_numbers = {pr_id: i for i, pr_id in enumerate(peer_review_ids)}

    return {
        'title': reviews[0].submission.assignment.title,
        'entries': [
            {
                'id': review.id,
                'student_id': student_numbers[review.id],
                'entries': [{'id': comment.id,
                             'heading': comment.criterion.description,
                             'content': comment.comment}
                            for comment in review.comments.all().order_by('criterion_id')]
            }
            for review in reviews
            if review.comments.exists()
        ]
    }


@authorized_json_endpoint(roles=['student'])
def reviews_given(request, course_id, student_id, rubric_id):
    raise_if_not_current_user(request, student_id)

    reviews = PeerReview.objects.filter(
        student_id=student_id,
        submission__assignment__course_id=course_id,
        submission__assignment__rubric_for_prompt=rubric_id
    )\
        .prefetch_related('comments')\
        .order_by('id')

    return _denormalize_reviews(reviews)


@authorized_json_endpoint(roles=['student'])
def reviews_received(request, course_id, student_id, rubric_id):
    raise_if_not_current_user(request, student_id)

    reviews = PeerReview.objects.filter(
        submission__assignment__course_id=course_id,
        submission__assignment__rubric_for_prompt__id=rubric_id,
        submission__author_id=student_id
    )\
        .order_by('id')

    peer_review_ids = [r.id for r in reviews]
    student_numbers = {pr_id: i for i, pr_id in enumerate(peer_review_ids)}

    comments = list(chain(*map(lambda r: r.comments.all(), reviews)))
    criterion_ids = set(c.criterion_id for c in comments)
    criterion_numbers = {cr_id: i for i, cr_id in enumerate(criterion_ids)}

    entries = []
    for comment in comments:
        try:
            comment.peer_review.evaluation
            evaluation_submitted = True
        except ObjectDoesNotExist:
            evaluation_submitted = False

        entries.append({
            'peer_review_id': comment.peer_review_id,
            'evaluation_submitted': evaluation_submitted,
            'reviewer_id': student_numbers[comment.peer_review_id],
            'criterion_id': criterion_numbers[comment.criterion_id],
            'criterion': comment.criterion.description,
            'comment_id': comment.id,
            'comment': comment.comment
        })

    prompt_title = Rubric.objects.get(id=rubric_id).reviewed_assignment.title

    return {
        'title': prompt_title,
        'entries': entries
    }


@require_POST
@json_body
@authorized_json_endpoint(roles=['student'])
def submit_peer_review_evaluation(request, body, course_id, student_id, peer_review_id):
    raise_if_not_current_user(request, student_id)
    raise_if_peer_review_not_for_student(request, student_id, peer_review_id)

    PeerReviewEvaluation.objects.create(
        peer_review_id=peer_review_id,
        usefulness=body['usefulness'],
        comment=body['comment']
    )

    return True
