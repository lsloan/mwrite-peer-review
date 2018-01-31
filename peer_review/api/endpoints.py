import logging

from peer_review.models import CanvasStudent
from peer_review.decorators import authorized_json_endpoint


@authorized_json_endpoint(roles=['instructor'])
def all_students(request, course_id):
    return CanvasStudent.objects.filter(course_id=course_id)
