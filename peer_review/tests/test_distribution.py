from statistics import mean, stdev

from hypothesis import given
from hypothesis.strategies import composite, sets, integers

from peer_review.models import CanvasStudent, CanvasSubmission
from peer_review.distribution import make_distribution


@composite
def students_and_submissions(draw, min_size=50, average_size=1000, max_size=5000):
    ids = draw(sets(elements=integers(), min_size=min_size, average_size=average_size, max_size=max_size))
    students = {CanvasStudent(id=i) for i in ids}
    submissions = {CanvasSubmission(id=i, author_id=i) for i in ids}
    return students, submissions


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
