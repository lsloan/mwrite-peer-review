import logging

from rolepermissions.roles import get_user_roles

import peer_review.etl as etl
from peer_review.models import CanvasStudent, CanvasCourse
from peer_review.queries import ReviewDetails
from peer_review.api.util import merge_validations
from peer_review.util import to_camel_case, keymap_all
from peer_review.decorators import authorized_json_endpoint, authenticated_json_endpoint

logger = logging.getLogger(__name__)


@authenticated_json_endpoint
def logged_in_user_details(request):
    roles = [role.get_name() for role in get_user_roles(request.user)]
    course_id = request.session['lti_launch_params']['custom_canvas_course_id']
    course_name = CanvasCourse.objects.get(id=course_id).name
    return {
        'username': request.user.username,
        'course_id': course_id,
        'course_name': course_name,
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

    details = ReviewDetails.get(course_id, fetched_assignment_ids)

    validations = {a.id: a.validation for a in assignments}
    details_with_validations = merge_validations(details, validations)

    return keymap_all(to_camel_case, details_with_validations)
