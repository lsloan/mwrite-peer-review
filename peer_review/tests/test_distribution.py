import string
from statistics import mean, stdev

from hypothesis import given
from hypothesis.strategies import composite, sets, integers, lists, just, text
from hypothesis.extra.django.models import models

from peer_review.models import CanvasStudent, CanvasSubmission, CanvasCourse, CanvasSection
from peer_review.distribution import make_distribution


# TODO maybe rewrite this using Hypothesis's Django support?
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

alphabet = string.ascii_lowercase + string.ascii_uppercase


def db_id():
    return integers(min_value=10000, max_value=1000000)


def name():
    return text(alphabet=alphabet, min_size=3, max_size=15)


def generate_students_for_section(section):
    return lists(models(CanvasStudent,
                        id=db_id(),
                        full_name=name(),
                        sortable_name=name(),
                        username=name()),
                 min_size=4,
                 max_size=2000) \
        .map(lambda ss: list(map(lambda s: s.sections.add(section), ss)))


def make_section_with_students(course):
    return models(CanvasSection,
                  id=db_id(),
                  name=name(),
                  course=just(course)) \
        .flatmap(generate_students_for_section)


def generate_sections_for_course(course):
    return lists(make_section_with_students(course), min_size=1, max_size=10).map(lambda _: course)

complete_course = models(CanvasCourse, id=db_id(), name=name()).flatmap(generate_sections_for_course)
