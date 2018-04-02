from toolz.itertoolz import groupby
from toolz.dicttoolz import valfilter
from toolz.functoolz import thread_last
from django.db import models
from django.db.models import Subquery, OuterRef, Count, Case, When, Value, F

from peer_review.util import some


class CanvasCourse(models.Model):

    id = models.IntegerField(primary_key=True)
    name = models.TextField()

    def to_dict(self, levels=1):
        if levels >= 1:
            return {'id': self.id, 'name': self.name}
        else:
            return self.id

    class Meta:
        db_table = 'canvas_courses'


class CanvasSection(models.Model):

    id = models.IntegerField(primary_key=True)
    course = models.ForeignKey(CanvasCourse, on_delete=models.CASCADE, related_name='sections')
    name = models.TextField()

    def to_dict(self, levels=1):
        if levels >= 1:
            course = self.course.to_dict(levels=levels-1)
            return {'id': self.id,
                    'name': self.name,
                    'course': course}
        else:
            return self.id

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
    course = models.ForeignKey(CanvasCourse, on_delete=models.CASCADE)

    def to_dict(self, levels=1):
        if levels >= 1:
            next_levels = levels - 1
            return {'id': self.id,
                    'sortable_name': self.sortable_name,
                    'full_name': self.full_name,
                    'username': self.username,
                    'sections': [section.to_dict(levels=next_levels)
                                 for section in self.sections.all()],
                    'course': self.course.to_dict(levels=next_levels)}
        else:
            return self.id

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

    @staticmethod
    def _make_review(peer_review):
        return {
            'review_id': peer_review.id,
            'review_is_complete': peer_review.review_is_complete
        }

    @staticmethod
    def _make_data(entry):
        prompt_id, peer_reviews = entry
        prompt_name = peer_reviews[0].submission.assignment.title
        due_date_utc = peer_reviews[0].submission.assignment.rubric_for_prompt.passback_assignment.due_date_utc
        return {
            'prompt_name':  prompt_name,
            'due_date_utc': due_date_utc,
            'reviews':      sorted(map(PeerReview._make_review, peer_reviews), key=lambda r: r['review_id'])
        }

    @staticmethod
    def review_status_for_student(student_id):
        qs = PeerReview.objects.filter(student_id=student_id) \
            .select_related('submission__assignment__rubric_for_prompt') \
            .annotate(
            number_of_criteria=Subquery(
                Criterion.objects.filter(rubric_id=OuterRef('submission__assignment__rubric_for_prompt__id'))
                    .values('rubric')
                    .annotate(count=Count('id'))
                    .values('count')
            )
        ) \
            .annotate(
            number_of_comments=Subquery(
                PeerReviewComment.objects.filter(peer_review__id=OuterRef('id'))
                    .values('peer_review')
                    .annotate(count=Count('id'))
                    .values('count')
            )
        ) \
            .annotate(
            review_is_complete=Case(
                When(number_of_comments=F('number_of_criteria'), then=Value(True)),
                default=Value(False),
                output_field=models.BooleanField()
            )
        ) \
            .order_by('submission__assignment_id', 'id')

        reviews = thread_last(qs,
                              (groupby, lambda pr: pr.submission.assignment_id),
                              (valfilter, lambda prs: some(lambda pr: not pr.review_is_complete, prs)),
                              (lambda d: d.items(),),
                              (map, PeerReview._make_data))

        sorted_reviews = sorted(reviews, key=lambda r: r['due_date_utc'])
        for review in sorted_reviews:
            review['due_date_utc'] = review['due_date_utc'].strftime('%Y-%m-%d %H:%M:%SZ')

        return sorted_reviews

    class Meta:
        db_table = 'peer_reviews'
        unique_together = (('student', 'submission'),)


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
