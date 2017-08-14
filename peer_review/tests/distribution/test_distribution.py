import pytest
from statistics import mean, stdev

from hypothesis import given
from hypothesis.strategies import integers

import peer_review.tests.canvas.fixtures as f
from peer_review.distribution import make_distribution
from .strategies import students_and_submissions


@pytest.fixture
def canvas_integration_rubrics():
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
def test_distribution_task(transactional_db, canvas_integration_rubrics):
    test_rubric = canvas_integration_rubrics[0]
    assert test_rubric
