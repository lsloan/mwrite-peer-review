from django.db import models


class CanvasAssignment(models.Model):

    class Meta:
        managed = False
        db_table = 'canvas_assignments'

    id = models.AutoField(primary_key=True)
    title = models.TextField()
    course_id = models.IntegerField()
    due_date_utc = models.DateTimeField(blank=True, null=True)
    is_peer_review_assignment = models.BooleanField(blank=True, null=True, default=False)

    def __init__(self, *args, **kwargs):
        self.validation = kwargs.get('validation')
        if 'validation' in kwargs:
            del kwargs['validation']
        super(CanvasAssignment, self).__init__(*args, **kwargs)


# noinspection PyClassHasNoInit
class CanvasStudent(models.Model):

    class Meta:
        managed = False
        db_table = 'canvas_students'

    id = models.IntegerField(primary_key=True)
    full_name = models.TextField()
    sortable_name = models.TextField()


# noinspection PyClassHasNoInit
class CanvasSubmission(models.Model):

    class Meta:
        managed = False
        db_table = 'canvas_submissions'

    id = models.IntegerField(primary_key=True)
    author = models.ForeignKey(CanvasStudent, models.DO_NOTHING)
    assignment = models.ForeignKey(CanvasAssignment, models.DO_NOTHING)
    filename = models.CharField(unique=True, max_length=255)


# noinspection PyClassHasNoInit
class Rubric(models.Model):

    class Meta:
        managed = False
        db_table = 'rubrics'

    description = models.TextField()
    reviewed_assignment = models.ForeignKey(CanvasAssignment, models.DO_NOTHING, unique=True, blank=True, null=True)
    passback_assignment = models.ForeignKey(CanvasAssignment, models.DO_NOTHING, unique=True)
    revision_assignment = models.ForeignKey(CanvasAssignment, models.DO_NOTHING, unique=True, blank=True, null=True)
    revision_fetch_complete = models.IntegerField()


# noinspection PyClassHasNoInit
class Criterion(models.Model):

    class Meta:
        managed = False
        db_table = 'criteria'

    description = models.TextField()
    rubric = models.ForeignKey(Rubric, models.DO_NOTHING)


# noinspection PyClassHasNoInit
class PeerReview(models.Model):

    class Meta:
        managed = False
        db_table = 'peer_reviews'
        unique_together = (('student', 'submission'),)

    student = models.ForeignKey(CanvasStudent, models.DO_NOTHING)
    submission = models.ForeignKey(CanvasSubmission, models.DO_NOTHING)


# noinspection PyClassHasNoInit
class PeerReviewComment(models.Model):

    class Meta:
        managed = False
        db_table = 'peer_review_comments'
        unique_together = (('criterion', 'peer_review'),)

    criterion = models.ForeignKey(Criterion, models.DO_NOTHING)
    peer_review = models.ForeignKey(PeerReview, models.DO_NOTHING)
    comment = models.TextField()
    commented_at_utc = models.DateTimeField(blank=True, null=True)


# noinspection PyClassHasNoInit
class PeerReviewDistribution(models.Model):

    class Meta:
        managed = False
        db_table = 'peer_review_distributions'

    rubric = models.ForeignKey(Rubric, models.DO_NOTHING)
    is_distribution_complete = models.IntegerField()
    distributed_at_utc = models.DateTimeField(blank=True, null=True)
