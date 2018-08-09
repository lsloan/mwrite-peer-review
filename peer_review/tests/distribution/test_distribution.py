import pytest
from datetime import datetime
from statistics import mean, stdev

from hypothesis import given
from hypothesis.strategies import integers

from peer_review.tests.distribution.fixtures import test_models, rubric_tree_with_mocked_requests
from peer_review.models import CanvasStudent, CanvasSubmission, PeerReview
from peer_review.distribution import make_distribution, review_distribution_task
from .strategies import students_and_submissions


@given(sns=students_and_submissions(), n=integers(min_value=1, max_value=5))
def test_distribution(sns, n):
    students, submissions = sns
    reviews, counts = make_distribution(students, submissions, n)
    for student_id, submissions_to_review in reviews.items():
        assert student_id not in submissions_to_review
        assert len(submissions_to_review) == len(set(submissions_to_review))
        assert len(submissions_to_review) == n
    m = mean(counts.values())
    s = stdev(counts.values(), m)
    assert s < 0.25


# noinspection PyShadowingNames
@pytest.mark.django_db(True)
def test_distribution_task_for_all_sections(rubric_tree_with_mocked_requests):
    rubric = rubric_tree_with_mocked_requests

    review_distribution_task(datetime.utcnow(), True)

    assert rubric.peer_review_distribution.is_distribution_complete

    # each submission should have at least one reviewer
    submissions = rubric.reviewed_assignment.canvas_submission_set.all()
    for submission in submissions:
        assert PeerReview.objects.filter(submission_id=submission.id).exists()

    authors = CanvasStudent.objects.filter(
        id__in=submissions.values_list('author_id', flat=True)
    )
    for author in authors:
        # each student should have at least one review for the prompt
        submissions_for_prompt = CanvasSubmission.objects.filter(assignment_id=rubric.reviewed_assignment)
        submission_ids_for_prompt = submissions_for_prompt.values_list('id', flat=True)
        peer_reviews_for_student = PeerReview.objects.filter(
            student=author,
            submission_id__in=submission_ids_for_prompt
        )
        assert peer_reviews_for_student.exists()

        # each review should be for a distinct submission
        submission_ids_for_peer_review = peer_reviews_for_student.values_list('submission_id')
        assert peer_reviews_for_student.count() == submission_ids_for_peer_review.count()

        # students should not be reviewing their own submission
        own_submission = CanvasSubmission.objects.get(assignment=rubric.reviewed_assignment, author=author)
        assert own_submission.id not in submission_ids_for_peer_review


# noinspection PyShadowingNames
@pytest.mark.skip(reason='Section-only distribution is currently unused')
@pytest.mark.django_db(True)
def test_distribution_task_within_sections(rubric_tree_with_mocked_requests):
    rubric = rubric_tree_with_mocked_requests

    review_distribution_task(datetime.utcnow(), True)

    submissions = rubric.reviewed_assignment.canvas_submission_set.all()
    authors = CanvasStudent.objects.filter(id__in=submissions.values_list('author_id', flat=True))

    # each student should only be reviewing submissions from his/her section
    for author in authors:
        author_sections = author.sections.filter(id__in=rubric.sections.values_list('id', flat=True))
        assert len(author_sections) == 1
        other_section_ids = rubric.sections.exclude(id=author_sections[0].id).values_list('id', flat=True)
        other_section_student_ids = CanvasStudent.objects.filter(sections__id__in=other_section_ids) \
            .values_list('id', flat=True)
        submissions_not_to_review = submissions.filter(author_id__in=other_section_student_ids)
        erroneous_peer_reviews = PeerReview.objects.filter(
            student=author,
            submission_id__in=submissions_not_to_review.values_list('id', flat=True)
        )
        assert not erroneous_peer_reviews.exists()
