import pytest
from datetime import datetime
from statistics import mean, stdev

from hypothesis import given
from hypothesis.strategies import integers

import peer_review.tests.canvas.fixtures as f
from peer_review.models import CanvasStudent, CanvasSubmission, PeerReview
from peer_review.distribution import make_distribution, review_distribution_task
from .strategies import students_and_submissions


# noinspection PyUnusedLocal
@pytest.fixture
def canvas_integration_rubrics(transactional_db):
    # TODO need to find a way to not need to hard code these. config files?
    return f.canvas_integration_course(15, [108, 109, 129])


@given(sns=students_and_submissions(), n=integers(min_value=1, max_value=5))
def test_make_distribution(sns, n):
    students, submissions = sns
    reviews, counts = make_distribution(students, submissions, n)
    for student_id, submissions_to_review in reviews.items():
        assert student_id not in submissions_to_review
        assert len(submissions_to_review) == len(set(submissions_to_review))
        assert len(submissions_to_review) == n
    m = mean(counts.values())
    s = stdev(counts.values(), m)
    assert s < 0.25


# noinspection PyShadowingNames,PyUnusedLocal
@pytest.mark.django_db(True)
def test_distribution_task(canvas_integration_rubrics):
    test_rubric = canvas_integration_rubrics[0]

    review_distribution_task(datetime.utcnow(), True)

    assert test_rubric.peer_review_distribution.is_distribution_complete

    # each submission should have at least one review
    submissions = CanvasSubmission.objects.filter(
        id__in=test_rubric.reviewed_assignment.canvas_submission_set.values_list('id', flat=True)
    )
    for submission in submissions:
        assert PeerReview.objects.filter(submission_id=submission.id).exists()

    # each student should have at least one review
    authors = CanvasStudent.objects.filter(
        id__in=submissions.values_list('author_id', flat=True)
    )
    for author in authors:
        assert PeerReview.objects.filter(student_id=author.id).exists()
