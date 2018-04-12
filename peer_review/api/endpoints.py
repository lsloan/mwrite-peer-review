import logging
from itertools import chain

from rolepermissions.roles import get_user_roles
from django.core.exceptions import PermissionDenied

import peer_review.etl as etl
from peer_review.models import CanvasStudent, PeerReview, Rubric
from peer_review.queries import InstructorDashboardStatus, StudentDashboardStatus
from peer_review.api.util import merge_validations
from peer_review.util import to_camel_case, keymap_all
from peer_review.decorators import authorized_json_endpoint, authenticated_json_endpoint

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


@authorized_json_endpoint(roles=['instructor'])
def all_students(request, course_id):
    etl.persist_sections(course_id)
    etl.persist_students(course_id)
    students = CanvasStudent.objects.filter(course_id=course_id)
    return [student.to_dict(levels=2) for student in students]


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


@authorized_json_endpoint(roles=['student'])
def assigned_work(request, course_id, student_id):
    raise_if_not_current_user(request, student_id)
    return StudentDashboardStatus.assigned_work(student_id)


@authorized_json_endpoint(roles=['student'])
def completed_work(request, course_id, student_id):
    raise_if_not_current_user(request, student_id)
    return StudentDashboardStatus.completed_work(student_id)


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
    reviews = PeerReview.objects.filter(
        submission__assignment__course_id=course_id,
        submission__assignment__rubric_for_prompt__id=rubric_id,
        submission__author_id=student_id
    )\
        .order_by('id')

    peer_review_ids = [r.id for r in reviews]
    student_numbers = {pr_id: i for i, pr_id in enumerate(peer_review_ids)}

    comments = list(chain(*map(lambda r: r.comments.all(), reviews)))  # TODO sort comments?
    prompt_title = Rubric.objects.get(id=rubric_id).reviewed_assignment.title

    return {
        'title': prompt_title,
        'entries': [
            {
                'peer_review_id': comment.peer_review_id,
                'reviewer_id': student_numbers[comment.peer_review_id],
                'criterion_id': comment.criterion_id,
                'criterion': comment.criterion.description,
                'comment': comment.comment
            }
            for comment in comments
        ]
    }




