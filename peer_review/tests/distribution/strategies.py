import string
from itertools import chain
from datetime import timedelta

import pytz
from hypothesis.strategies import just, composite, text, lists, datetimes
from hypothesis.extra.django.models import models

from peer_review.models import CanvasStudent, CanvasSubmission, Criterion, CanvasCourse, CanvasAssignment, Rubric, \
    CanvasSection

alphabetic = text(alphabet=string.ascii_letters, min_size=3)
course = models(CanvasCourse, name=alphabetic)


def prompt(course_model, due_date_utc):
    return models(
        CanvasAssignment,
        is_peer_review_assignment=just(False),
        title=alphabetic,
        course=just(course_model),
        due_date_utc=just(due_date_utc)
    )


def peer_review_assignment(course_model, due_date_utc):
    return models(
        CanvasAssignment,
        is_peer_review_assignment=just(True),
        title=alphabetic,
        course=just(course_model),
        due_date_utc=just(due_date_utc)
    )


def rubric(prompt_model, peer_review_assignment_model):
    return models(
        Rubric,
        description=alphabetic,
        reviewed_assignment=just(prompt_model),
        passback_assignment=just(peer_review_assignment_model),
        revision_assignment=just(None),
        revision_fetch_complete=just(False),
        peer_review_open_date_is_prompt_due_date=just(True),
        peer_review_open_date=just(prompt_model.due_date_utc),
        distribute_peer_reviews_for_sections=just(False)
    )


def _criteria(rubric_model):
    criterion = models(Criterion, description=alphabetic, rubric=just(rubric_model))
    return lists(criterion, min_size=1, average_size=3, max_size=10, unique_by=lambda c: c.id)


@composite
def complete_rubric(draw):
    """A Hypothesis strategy to generate a course, prompt and peer review assignment, rubric and criteria."""
    course_model = draw(course)

    prompt_due_date = draw(datetimes(timezones=just(pytz.UTC)))
    prompt_model = draw(prompt(course_model, prompt_due_date))

    peer_review_due_date_minimum = (prompt_due_date + timedelta(minutes=10)).replace(tzinfo=None)
    peer_review_due_date = draw(datetimes(min_value=peer_review_due_date_minimum, timezones=just(pytz.UTC)))
    peer_review_assignment_model = draw(peer_review_assignment(course_model, peer_review_due_date))

    rubric_model = draw(rubric(prompt_model, peer_review_assignment_model))
    criteria_models = draw(_criteria(rubric_model))

    return rubric_model


def _sections(course_model):
    section = models(CanvasSection, name=alphabetic, course=just(course_model))
    return lists(section, min_size=1)


@composite
def student(draw, section_model):
    student_model = draw(models(
        CanvasStudent,
        full_name=alphabetic,       # TODO should be more realistic-ish
        sortable_name=alphabetic,   # TODO should be more realistic-ish
        username=alphabetic,
    ))
    student_model.courses.add(section_model.course)
    student_model.sections.add(section_model)
    return student_model


@composite
def students_for_sections(draw, section_models):
    all_students = []
    for section_model in section_models:
        all_students.append(draw(lists(
            student(section_model),
            min_size=4,
            max_size=50
        )))
    return list(chain(*all_students))


def submission(prompt_model, student_model):
    return models(
        CanvasSubmission,
        filename=alphabetic,      # TODO should a corresponding stub file be created?
        assignment=just(prompt_model),
        author=just(student_model)
    )


@composite
def _student_submissions_for_prompt(draw, prompt_model, student_models):
    all_submissions = []
    for student_model in student_models:
        _submission = draw(submission(prompt_model, student_model))
        all_submissions.append(_submission)
    return all_submissions


@composite
def rubric_ready_for_distribution(draw):
    _rubric = draw(complete_rubric())
    sections = draw(_sections(_rubric.reviewed_assignment.course))
    students = draw(students_for_sections(sections))
    submissions = draw(_student_submissions_for_prompt(_rubric.reviewed_assignment, students))
    return _rubric
