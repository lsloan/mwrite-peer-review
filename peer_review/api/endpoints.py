import logging

from rolepermissions.roles import get_user_roles

from peer_review.models import CanvasStudent
from peer_review.decorators import authorized_json_endpoint, authenticated_json_endpoint

logger = logging.getLogger(__name__)


@authorized_json_endpoint(roles=['instructor'])
def all_students(request, course_id):
    students = CanvasStudent.objects.filter(course_id=course_id)
    return [student.to_dict(levels=2) for student in students]


@authenticated_json_endpoint
def logged_in_user_details(request, course_id):
    roles = [role.get_name() for role in get_user_roles(request.user)]
    return {
        'username': request.user.username,
        'roles': roles
    }

