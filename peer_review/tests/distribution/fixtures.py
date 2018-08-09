from datetime import datetime
from collections import namedtuple

import pytest
from django.db.models import Max

import peer_review.canvas as canvas
from peer_review.tests.canvas.fixtures import *
from peer_review.models import Criterion, Rubric, CanvasSection, CanvasCourse, CanvasAssignment, CanvasStudent, \
    CanvasSubmission


# TODO refactor parts of this to be based on Hypothesis strategies


def next_id(model, id_field='id'):
    """Helper function for getting next IDs of non-autoincrement models.  Should only be used for tests."""
    max_key = id_field + '__max'
    max_id = model.objects.all().aggregate(Max(id_field))[max_key] or -1
    return max_id + 1


ModelsPackage = namedtuple('ModelsPackage', [
    'creation_time',
    'course',
    'prompt',
    'peer_review_assignment',
    'rubric'
])


@pytest.fixture
@pytest.mark.django_db(True)
def test_models():
    course = CanvasCourse(id=next_id(CanvasCourse), name='Test Course')
    course.save()

    for i in range(1, 4):
        section = CanvasSection(
            id=next_id(CanvasSection),
            name='Test Section %d' % i,
            course=course
        )
        section.save()

    now = datetime.utcnow()

    prompt_due_date = now + timedelta(minutes=1)
    prompt = CanvasAssignment(
        id=next_id(CanvasAssignment),
        title='Test Prompt',
        course=course,
        due_date_utc=prompt_due_date,
        is_peer_review_assignment=False
    )
    prompt.save()

    peer_review_due_date = now + timedelta(minutes=30)
    peer_review_assignment = CanvasAssignment(
        id=next_id(CanvasAssignment),
        title='Test Peer Review',
        course=course,
        due_date_utc=peer_review_due_date,
        is_peer_review_assignment=True
    )
    peer_review_assignment.save()

    rubric = Rubric(
        description='This is a test rubric.',
        reviewed_assignment=prompt,
        passback_assignment=peer_review_assignment,
    )
    rubric.save()

    for i in range(1, 4):
        criterion = Criterion(
            description='Test criterion %d' % i,
            rubric=rubric
        )
        criterion.save()

    return ModelsPackage(
        creation_time=now,
        course=course,
        prompt=prompt,
        peer_review_assignment=peer_review_assignment,
        rubric=rubric
    )


# noinspection PyShadowingNames,PyProtectedMember
@pytest.fixture
@pytest.mark.django_db(True)
def rubric_tree_with_mocked_requests(test_models, requests_mock):
    requests_mock.get(
        canvas._make_url('course', [test_models.course.id]),
        json=test_course_api(test_models.course)
    )

    def make_test_assignment(a):
        return test_assignment_api(test_models.creation_time, test_models.course, a)

    test_assignments = list(
        map(
            lambda a: test_assignment_api(test_models.creation_time, test_models.course, a),
            [test_models.prompt, test_models.peer_review_assignment]
        )
    )
    requests_mock.get(
        canvas._make_url('assignments', [test_models.course.id]),
        json=test_assignments
    )

    requests_mock.get(
        canvas._make_url('assignment', [test_models.course.id, test_models.prompt.id]),
        json=make_test_assignment(test_models.prompt)
    )

    requests_mock.get(
        canvas._make_url('assignment', [test_models.course.id, test_models.peer_review_assignment.id]),
        json=make_test_assignment(test_models.peer_review_assignment)
    )

    requests_mock.get(
        canvas._make_url('sections', [test_models.course.id]),
        json=test_sections_api(test_models.course.sections.all())
    )

    student_id_start = next_id(CanvasStudent)
    test_students = [
        test_student_api(
            test_models.creation_time,
            test_models.course,
            test_models.course.sections.all(),
            i
        )
        for i in range(student_id_start, student_id_start+4)
    ]
    requests_mock.get(
        canvas._make_url('students', [test_models.course.id]),
        json=test_students
    )

    submission_template = 'submission for %d'
    test_attachments = [
        bytes(submission_template % student['id'], 'utf8')
        for student in test_students
    ]
    submission_id_start = next_id(CanvasSubmission)
    test_submissions = [
        test_submission_api(
            test_models.creation_time,
            test_models.course,
            test_models.prompt,
            student,
            attachment,
            index
        )
        for index, (student, attachment) in enumerate(zip(test_students, test_attachments), start=submission_id_start)
    ]
    requests_mock.get(
        canvas._make_url('submissions', [test_models.course.id, test_models.prompt.id]),
        json=test_submissions
    )

    for submission, attachment_data in zip(test_submissions, test_attachments):
        url = submission['attachments'][0]['url']
        requests_mock.get(url, content=attachment_data)

    return test_models.rubric
