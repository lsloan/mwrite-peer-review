import string

from hypothesis.strategies import composite, sets, integers, text, just, lists
from hypothesis.extra.django.models import models

from peer_review.models import CanvasStudent, CanvasSubmission, Criterion, CanvasCourse, CanvasAssignment, Rubric


@composite
def students(draw, min_size=1, average_size=10, max_size=25):
    ids = draw(sets(elements=integers(), min_size=min_size, average_size=average_size, max_size=max_size))
    return {CanvasStudent(id=i) for i in ids}


@composite
def students_and_submissions(draw, assignment_id=None):
    _students = draw(students(min_size=50, average_size=1000, max_size=5000))
    ids = (s.id for s in _students)
    submissions = {
        CanvasSubmission(id=i, author_id=i, assignment_id=assignment_id)
        for i in ids
    }
    return _students, submissions


alphabetic = text(alphabet=string.ascii_letters, min_size=3)
course = models(CanvasCourse, name=alphabetic)


def _prompt(course_model):
    return models(
        CanvasAssignment,
        is_peer_review_assignment=just(False),
        title=alphabetic,
        course=just(course_model)
    )


def _peer_review_assignment(course_model):
    return models(
        CanvasAssignment,
        is_peer_review_assignment=just(False),
        title=alphabetic,
        course=just(course_model)
    )


def _rubric(prompt_model, peer_review_assignment_model):
    return models(
        Rubric,
        description=alphabetic,
        reviewed_assignment=just(prompt_model),
        passback_assignment=just(peer_review_assignment_model)
    )


def _criteria(rubric_model):
    criterion = models(Criterion, description=alphabetic, rubric=just(rubric_model))
    return lists(criterion, min_size=1, average_size=3, max_size=10)


@composite
def complete_rubric(draw):
    """A Hypothesis strategy to generate a course, prompt and peer review assignment, rubric and criteria."""
    course_model = draw(course)
    prompt_model = draw(_prompt(course_model))
    peer_review_assignment_model = draw(_peer_review_assignment(course_model))
    rubric_model = draw(_rubric(prompt_model, peer_review_assignment_model))
    criteria_models = draw(_criteria(rubric_model))
    return just(rubric_model)
