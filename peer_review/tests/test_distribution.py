import string
from functools import partial
from datetime import datetime
from statistics import mean, stdev

from hypothesis import given
from hypothesis.extra.django.models import models
from hypothesis.strategies import composite, sets, integers, lists, just, text
from dateutil.relativedelta import relativedelta

from peer_review.models import CanvasAssignment, CanvasStudent, CanvasSubmission, CanvasCourse, CanvasSection, Rubric
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


@composite
def canvas_assignment(draw, course_strategy, due_date_utc_strategy, is_peer_review_assignment_strategy):
    _course = draw(course_strategy)
    _due_date_utc = draw(due_date_utc_strategy)
    _is_peer_review_assignment = draw(is_peer_review_assignment_strategy)
    _id = draw(db_id())
    _title = draw(name())
    assignment = CanvasAssignment(id=_id,
                                  title=_title,
                                  course=_course,
                                  due_date_utc=_due_date_utc,
                                  is_peer_review_assignment=_is_peer_review_assignment)
    assignment.save()
    return assignment


def _add_sections_to_rubric(sections, _rubric):
    for section in sections:
        _rubric.sections.add(section)
    return just(_rubric)


@composite
def rubric(draw, prompt_strategy, peer_review_strategy, sections):
    _peer_review = draw(peer_review_strategy)
    _rubric = Rubric(id=draw(db_id()),
                     description=draw(name()),
                     reviewed_assignment=draw(prompt_strategy),
                     passback_assignment=_peer_review,
                     peer_review_open_date=_peer_review.due_date_utc,
                     distribute_peer_reviews_for_sections=True)
    _rubric.save()
    for section in sections:
        _rubric.sections.add(section)
    return _rubric


@composite
def complete_rubric(draw, course):

    now = datetime.utcnow()
    five_minutes = relativedelta(minutes=5)
    five_minutes_ago = now - five_minutes
    five_minutes_from_now = now + five_minutes

    just_course = just(course)

    prompt = draw(canvas_assignment(just_course,
                                    just(five_minutes_ago),
                                    just(False)))
    peer_review = draw(canvas_assignment(just_course,
                                         just(five_minutes_from_now),
                                         just(True)))

    return draw(rubric(just(prompt), just(peer_review), course.sections.all()))


def canvas_section(course):
    return models(CanvasSection, id=db_id(), name=name(), course=just(course))


def _add_section_to_student(section, student):
    student.sections.add(section)
    return just(student)


def canvas_student(section):
    return models(CanvasStudent,
                  id=db_id(),
                  username=name(),
                  full_name=name(),
                  sortable_name=name()) \
        .flatmap(partial(_add_section_to_student, section))


def generate_students_for_section(section):
    return lists(canvas_student(section), min_size=4, max_size=30).map(lambda _: section)


def generate_sections_for_course(course):
    section = canvas_section(course).flatmap(generate_students_for_section)
    return lists(section, min_size=2, max_size=10).map(lambda _: course)


def canvas_course():
    return models(CanvasCourse, id=db_id(), name=name())

complete_course = canvas_course().flatmap(generate_sections_for_course)
