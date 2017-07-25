from django.db import models


class CanvasAssignment(models.Model):

    class Meta:
        managed = False
        db_table = 'canvas_assignments'

    id = models.IntegerField(primary_key=True)
    title = models.TextField()
    course_id = models.IntegerField()
    due_date_utc = models.DateTimeField(blank=True, null=True)
    is_peer_review_assignment = models.BooleanField(default=False)

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
    section = models.TextField()
    full_name = models.TextField()
    sortable_name = models.TextField()


# noinspection PyClassHasNoInit
class CanvasSubmission(models.Model):

    class Meta:
        managed = False
        db_table = 'canvas_submissions'

    id = models.IntegerField(primary_key=True)
    author = models.ForeignKey(CanvasStudent, models.DO_NOTHING)
    assignment = models.ForeignKey(CanvasAssignment, models.DO_NOTHING, related_name='canvas_submission_set')
    filename = models.CharField(unique=True, max_length=255)
    
    @property
    def total_completed_by_a_student(self):
        return PeerReview.objects.filter(student=self.author, submission__assignment=self.assignment)
                            
    @property
    def total_received_of_a_student(self):
        return PeerReview.objects.filter(submission=self)

    @property
    def num_comments_each_review_per_studetn(self):
        return PeerReview.objects.filter(student=self.author, submission__assignment=self.assignment)\
                                .annotate(completed = models.Count('comments', distinct=True))   

    @property
    def num_comments_each_review_per_submission(self):
        return PeerReview.objects.filter(submission=self)\
                                .annotate(received = models.Count('comments', distinct=True))

# noinspection PyClassHasNoInit
class Rubric(models.Model):

    class Meta:
        managed = False
        db_table = 'rubrics'

    id = models.AutoField(primary_key=True)
    description = models.TextField()
    reviewed_assignment = models.OneToOneField(CanvasAssignment,
                                               models.DO_NOTHING,
                                               unique=True,
                                               blank=True,
                                               null=True,
                                               related_name='rubric_for_prompt')
    passback_assignment = models.OneToOneField(CanvasAssignment,
                                               models.DO_NOTHING,
                                               unique=True,
                                               related_name='rubric_for_review')
    revision_assignment = models.OneToOneField(CanvasAssignment,
                                               models.DO_NOTHING,
                                               unique=True,
                                               blank=True,
                                               null=True,
                                               related_name='rubric_for_revision')
    revision_fetch_complete = models.BooleanField(default=False)

    @property
    def num_criteria(self):
        return Criterion.objects.filter(rubric=self).count()

# noinspection PyClassHasNoInit
class Criterion(models.Model):

    class Meta:
        managed = False
        db_table = 'criteria'

    id = models.AutoField(primary_key=True)
    description = models.TextField()
    rubric = models.ForeignKey(Rubric, models.DO_NOTHING, related_name='criteria')

    def __str__(self):
        return self.description


# noinspection PyClassHasNoInit
class PeerReview(models.Model):

    class Meta:
        managed = False
        db_table = 'peer_reviews'
        unique_together = (('student', 'submission'),)

    id = models.AutoField(primary_key=True)
    student = models.ForeignKey(CanvasStudent, models.DO_NOTHING, related_name='peer_reviews_for_student')
    submission = models.ForeignKey(CanvasSubmission, models.DO_NOTHING, related_name='peer_reviews_for_submission')


# noinspection PyClassHasNoInit
class PeerReviewComment(models.Model):

    class Meta:
        managed = False
        db_table = 'peer_review_comments'
        unique_together = (('criterion', 'peer_review'),)

    id = models.AutoField(primary_key=True)
    criterion = models.ForeignKey(Criterion, models.DO_NOTHING)
    peer_review = models.ForeignKey(PeerReview, models.DO_NOTHING, related_name='comments')
    comment = models.TextField()
    commented_at_utc = models.DateTimeField(blank=True, null=True)


# noinspection PyClassHasNoInit
class PeerReviewDistribution(models.Model):

    class Meta:
        managed = False
        db_table = 'peer_review_distributions'

    id = models.AutoField(primary_key=True)
    rubric = models.OneToOneField(Rubric, models.DO_NOTHING, related_name='peer_review_distribution')
    is_distribution_complete = models.BooleanField(default=False)
    distributed_at_utc = models.DateTimeField(blank=True, null=True)
