from django.db import models


class CanvasAssignment(models.Model):

    class Meta:
        managed = False
        db_table = 'canvas_assignments'

    id = models.AutoField(primary_key=True)
    title = models.TextField()
    course_id = models.IntegerField()
    due_date_utc = models.DateTimeField()
    is_peer_review_assignment = models.BooleanField()

    def __init__(self, *args, **kwargs):
        self.validation = kwargs.get('validation')
        super(CanvasAssignment, self).__init__(*args, **kwargs)
