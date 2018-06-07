from django.db import models


class CanvasCourse(models.Model):

    id = models.IntegerField(primary_key=True)
    name = models.TextField()

    class Meta:
        db_table = 'canvas_courses'


class CanvasSection(models.Model):

    id = models.IntegerField(primary_key=True)
    course = models.ForeignKey(CanvasCourse, on_delete=models.CASCADE, related_name='sections')
    name = models.TextField()

    class Meta:
        db_table = 'canvas_section'


class CanvasAssignment(models.Model):

    id = models.IntegerField(primary_key=True)
    title = models.TextField()
    course = models.ForeignKey(CanvasCourse, on_delete=models.CASCADE)
    due_date_utc = models.DateTimeField(blank=True, null=True)
    is_peer_review_assignment = models.BooleanField(default=False)

    def __init__(self, *args, **kwargs):
        self.validation = kwargs.get('validation')
        if 'validation' in kwargs:
            del kwargs['validation']
        super(CanvasAssignment, self).__init__(*args, **kwargs)

    class Meta:
        db_table = 'canvas_assignments'


# noinspection PyClassHasNoInit
class CanvasStudent(models.Model):

    id = models.IntegerField(primary_key=True)
    sections = models.ManyToManyField(CanvasSection, blank=True, related_name='students')
    full_name = models.TextField()
    sortable_name = models.TextField()
    username = models.TextField()
    courses = models.ManyToManyField(CanvasCourse, related_name='students')

    class Meta:
        db_table = 'canvas_students'


# noinspection PyClassHasNoInit
class CanvasSubmission(models.Model):

    id = models.IntegerField(primary_key=True)
    author = models.ForeignKey(CanvasStudent, on_delete=models.DO_NOTHING)
    assignment = models.ForeignKey(CanvasAssignment, on_delete=models.DO_NOTHING, related_name='canvas_submission_set')
    filename = models.CharField(unique=True, max_length=255)

    # TODO this needs a better name -- these are just assigned, may not be actually completed
    @property
    def total_completed_by_a_student(self):
        return PeerReview.objects.filter(student=self.author, submission__assignment=self.assignment)

    # TODO this needs a better name -- these are just assigned, may not be actually received
    @property
    def total_received_of_a_student(self):
        return PeerReview.objects.filter(submission=self)

    @property
    def num_comments_each_review_per_student(self):
        return PeerReview.objects.filter(student=self.author, submission__assignment=self.assignment) \
                                 .annotate(completed=models.Count('comments', distinct=True))

    @property
    def num_comments_each_review_per_submission(self):
        return PeerReview.objects.filter(submission=self) \
                                 .annotate(received=models.Count('comments', distinct=True))

    class Meta:
        db_table = 'canvas_submissions'


# noinspection PyClassHasNoInit
class Rubric(models.Model):

    id = models.AutoField(primary_key=True)
    description = models.TextField()
    reviewed_assignment = models.OneToOneField(CanvasAssignment,
                                               on_delete=models.DO_NOTHING,
                                               unique=True,
                                               blank=True,
                                               null=True,
                                               related_name='rubric_for_prompt')
    passback_assignment = models.OneToOneField(CanvasAssignment,
                                               on_delete=models.DO_NOTHING,
                                               unique=True,
                                               related_name='rubric_for_review')
    revision_assignment = models.OneToOneField(CanvasAssignment,
                                               on_delete=models.DO_NOTHING,
                                               unique=True,
                                               blank=True,
                                               null=True,
                                               related_name='rubric_for_revision')
    revision_fetch_complete = models.BooleanField(default=False)
    peer_review_open_date_is_prompt_due_date = models.BooleanField(default=True)
    peer_review_open_date = models.DateTimeField(blank=True, null=True)
    distribute_peer_reviews_for_sections = models.BooleanField(default=False)
    sections = models.ManyToManyField(CanvasSection, blank=True)

    @property
    def num_criteria(self):
        return Criterion.objects.filter(rubric=self).count()

    class Meta:
        db_table = 'rubrics'


# noinspection PyClassHasNoInit
class Criterion(models.Model):

    id = models.AutoField(primary_key=True)
    description = models.TextField()
    rubric = models.ForeignKey(Rubric, on_delete=models.DO_NOTHING, related_name='criteria')

    def __str__(self):
        return self.description

    class Meta:
        db_table = 'criteria'


# noinspection PyClassHasNoInit
class PeerReview(models.Model):

    id = models.AutoField(primary_key=True)
    student = models.ForeignKey(CanvasStudent, on_delete=models.DO_NOTHING,
                                related_name='peer_reviews_for_student')
    submission = models.ForeignKey(CanvasSubmission, on_delete=models.DO_NOTHING,
                                   related_name='peer_reviews_for_submission')

    class Meta:
        db_table = 'peer_reviews'
        unique_together = (('student', 'submission'),)


class PeerReviewEvaluation(models.Model):

    USEFULNESS_CHOICES = [
        (1, 'Very unuseful'),
        (2, 'Unuseful'),
        (3, 'Somewhat useful'),
        (4, 'Useful'),
        (5, 'Very useful')
    ]

    id = models.AutoField(primary_key=True)
    usefulness = models.IntegerField(choices=USEFULNESS_CHOICES)
    comment = models.TextField(null=True, blank=True)
    peer_review = models.OneToOneField(PeerReview, on_delete=models.CASCADE, related_name='evaluation')

    class Meta:
        db_table = 'peer_review_evaluations'


# noinspection PyClassHasNoInit
class PeerReviewComment(models.Model):

    id = models.AutoField(primary_key=True)
    criterion = models.ForeignKey(Criterion, on_delete=models.DO_NOTHING)
    peer_review = models.ForeignKey(PeerReview, on_delete=models.DO_NOTHING, related_name='comments')
    comment = models.TextField()
    commented_at_utc = models.DateTimeField(blank=True, null=True)

    class Meta:
        db_table = 'peer_review_comments'
        unique_together = (('criterion', 'peer_review'),)


# noinspection PyClassHasNoInit
class PeerReviewDistribution(models.Model):

    id = models.AutoField(primary_key=True)
    rubric = models.OneToOneField(Rubric, on_delete=models.DO_NOTHING, related_name='peer_review_distribution')
    is_distribution_complete = models.BooleanField(default=False)
    distributed_at_utc = models.DateTimeField(blank=True, null=True)

    class Meta:
        db_table = 'peer_review_distributions'
