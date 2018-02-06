import logging

from rolepermissions.roles import get_user_roles

from peer_review.models import CanvasStudent
from peer_review.decorators import authorized_json_endpoint, authenticated_json_endpoint

logger = logging.getLogger(__name__)


@authenticated_json_endpoint
def logged_in_user_details(request):
    roles = [role.get_name() for role in get_user_roles(request.user)]
    course_id = request.session['lti_launch_params']['custom_canvas_course_id']
    return {
        'username': request.user.username,
        'course_id': course_id,
        'roles': roles
    }


@authorized_json_endpoint(roles=['instructor'])
def all_students(request, course_id):
    students = CanvasStudent.objects.filter(course_id=course_id)
    return [student.to_dict(levels=2) for student in students]
