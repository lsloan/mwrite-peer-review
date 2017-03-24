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


# TODO move this somewhere else
class AssignmentValidation:

    # TODO move this somewhere else
    @staticmethod
    def _utc_to_local(date_utc):
        raise NotImplemented()

    def __init__(self, **kwargs):
        self.submission_upload_type = kwargs.get('submission_upload_type')
        self.allowed_submission_file_extensions = kwargs.get('allowed_extensions')
        self.local_due_date = AssignmentValidation._utc_to_local(kwargs.get('due_date_utc'))
        self.number_of_due_dates = kwargs.get('number_of_due_dates')
        self.section_name = kwargs.get('section_name')
        self.number_of_sections = kwargs.get('number_of_sections')
