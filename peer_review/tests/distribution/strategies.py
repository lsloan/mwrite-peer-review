import string
from datetime import timedelta

import pytz
from hypothesis import assume
from hypothesis.strategies import just, composite, text, lists, datetimes, integers
from hypothesis.extra.django.models import models

from peer_review.models import CanvasStudent, CanvasSubmission, Criterion, CanvasCourse, CanvasAssignment, Rubric, \
    CanvasSection, PeerReview

alphabetic = text(alphabet=string.ascii_letters, min_size=3)
pk = integers(min_value=-2147483648, max_value=2147483647)
course = models(CanvasCourse, name=alphabetic)


def _model_id(m):
    return m.id


@composite
def unique_field(draw, model, field, field_strategy):
    value = draw(field_strategy)
    params = {field: value}
    assume(not model.objects.filter(**params).exists())
    return value


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
    return lists(criterion, min_size=1, average_size=3, max_size=10, unique_by=_model_id)


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


student = models(
    CanvasStudent,
    full_name=alphabetic,       # TODO should be more realistic-ish
    sortable_name=alphabetic,   # TODO should be more realistic-ish
    username=alphabetic
)
students = lists(student, min_size=4, max_size=50, unique_by=_model_id)


@composite
def students_not_for_peer_review(draw, prompt_model):
    _students = draw(students)

    def student_not_assigned_for_review(_student_model):
        reviews = PeerReview.objects.filter(submission__assignment=prompt_model, student=_student_model)
        return not reviews.exists()

    assume(all(map(student_not_assigned_for_review, _students)))
    return _students


@composite
def section(draw, course_model):
    _section_model = draw(models(CanvasSection, name=alphabetic, course=just(course_model)))

    def _add_students_to_section(student_models):
        for s in student_models:
            s.courses.add(course_model)
            s.sections.add(_section_model)
        return just(student_models)

    draw(students.flatmap(_add_students_to_section))

    return _section_model


def student_with_relationships(section_model, student_model):
    student_model.courses.add(section_model.course)
    student_model.sections.add(section_model)
    return student_model


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
    _prompt = _rubric.reviewed_assignment
    _course = _prompt.course

    _sections = draw(lists(section(_course), min_size=1, unique_by=_model_id))

    _all_students = []
    for s in _sections:
        _all_students.extend(s.students.all())

    # TODO need a more reliable way to generate 1:1 student:submissions w/o drawing duplicates.
    # TODO the `assume` calls below are hacks; they work, but they significantly slow down
    # TODO example generation and virtually ensure that that the number of students in the test
    # TODO will be low.
    all_submissions = set()
    for s in _all_students:
        _submission = draw(submission(_prompt, s))
        all_submissions.add(_submission.id)
    assume(len(all_submissions) == len(set(s.id for s in _all_students)))
    assume(len(all_submissions) >= 4)

    return _rubric
