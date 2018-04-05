import logging

from toolz.itertoolz import groupby
from toolz.functoolz import thread_last
from rolepermissions.roles import get_user_roles
from django.db.models import Subquery
from django.core.exceptions import PermissionDenied

import peer_review.etl as etl
from peer_review.models import CanvasStudent, PeerReviewComment, Criterion
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


def _denormalize_comments(comments_qs):
    comments_by_author_id = groupby(lambda c: c.peer_review.submission.author_id, comments_qs)

    comments = []
    for i, entry in enumerate(comments_by_author_id.items(), start=1):
        author_id, comments_for_author = entry
        data = {
            'id': i,
            'title': 'Student %d' % i,
            'entries': [
                {'id': comment.id,
                 'heading': comment.criterion.description,
                 'content': comment.comment}
                for comment in comments_for_author
            ]
        }
        comments.append(data)

    return {
        'title': comments_qs[0].peer_review.submission.assignment.title,
        'entries': comments
    }


@authorized_json_endpoint(roles=['student'])
def reviews_given(request, course_id, student_id, rubric_id):
    comments = PeerReviewComment.objects.filter(
        criterion_id__in=Subquery(
            Criterion.objects.filter(rubric_id=rubric_id).values('id')
        ),
        peer_review__student_id=student_id,
        peer_review__submission__assignment__course_id=course_id
    ) \
        .select_related('peer_review__student') \
        .select_related('peer_review__submission') \
        .select_related('criterion') \
        .order_by('peer_review__student_id', 'peer_review__id', 'criterion_id')

    return _denormalize_comments(comments)
