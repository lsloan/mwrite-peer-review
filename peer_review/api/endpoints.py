import logging

from peer_review.models import CanvasStudent
from peer_review.decorators import authorized_json_endpoint

logger = logging.getLogger(__name__)


@authorized_json_endpoint(roles=['instructor'])
def all_students(request, course_id):
    students = CanvasStudent.objects.filter(course_id=course_id)
    return [student.to_dict(levels=2) for student in students]
