import logging

from django.db.models import Count
from rolepermissions.roles import get_user_roles

from peer_review.models import CanvasStudent, CanvasAssignment
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


@authorized_json_endpoint(roles=['instructor'])
def all_peer_review_assignment_details(request, course_id):
    # TODO refresh assignments from canvas
    # TODO the var below should use these IDs, not all in the course (to avoid orphans)
    peer_review_assignments = CanvasAssignment.objects.filter(course_id=course_id, is_peer_review_assignment=True) \
                                  .order_by('due_date_utc') \
                                  .select_related('rubric_for_review') \
                                  .prefetch_related('rubric_for_review__criteria') \
                                  .annotate(number_of_criteria=Count('rubric_for_review__criteria'))
