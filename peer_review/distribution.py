import logging
from datetime import datetime
from functools import partial
from collections import OrderedDict

from toolz.itertoolz import unique
from toolz.dicttoolz import merge_with

from django.db import transaction

from peer_review.etl import persist_students, persist_sections, persist_submissions
from peer_review.models import CanvasAssignment, PeerReview

log = logging.getLogger(__name__)


def _throw_on_duplicates(section, vals):
    msg = 'Duplicate students found when distributing for section %d' % section.id
    log.error(msg)
    raise RuntimeError(msg)


def make_distribution(students, submissions, n=3):
    submissions_by_id = {submission.id: submission for submission in submissions}

    submissions_to_review_by_student = {student.id: set() for student in students}
    review_count_by_submission = {submission.id: 0 for submission in submissions}

    for student in students:
        # TODO careful... this may not terminate. probably an issue when len(students) < n
        while len(submissions_to_review_by_student[student.id]) < n:
            review_count_by_submission = OrderedDict(sorted(review_count_by_submission.items(), key=lambda t: t[1]))
            for submission_id, _ in review_count_by_submission.items():
                if submissions_by_id[submission_id].author_id != student.id \
                        and submission_id not in submissions_to_review_by_student[student.id]:
                    review_count_by_submission[submission_id] += 1
                    submissions_to_review_by_student[student.id].add(submission_id)
                    break

    return submissions_to_review_by_student, review_count_by_submission


def distribute_reviews(rubric):

    # TODO need this safety check?
    rubric_tz = rubric.peer_review_open_date.tzinfo
    if rubric.peer_review_open_date > datetime.now(rubric_tz):
        args = (rubric.id, rubric.peer_review_open_date)
        log.error('Tried to distribute peer reviews before rubric %d\'s peer review open date (which is %s)' % args)
        return

    log.info('Beginning review distribution for rubric %d' % rubric.id)

    if rubric.distribute_peer_reviews_for_sections:
        log.info('Submissions for prompt %d will be distributed only within sections' % rubric.reviewed_assignment.id)
        reviews = {}
        for section in rubric.sections.all():
            log.info('Distributing reviews for section %d' % section.id)
            submissions = rubric.reviewed_assignment.canvas_submission_set.filter(sections__in=[section])
            students = submissions.values('author')
            reviews_for_section, _ = make_distribution(students, submissions)
            reviews = merge_with(partial(_throw_on_duplicates, section), reviews, reviews_for_section)
    else:
        log.info('Submissions for prompt %d will be distributed across all sections' % rubric.prompt.id)
        submissions = rubric.reviewed_assignment.canvas_submission_set
        students = submissions.values('author')
        reviews, _ = make_distribution(students, submissions)

    peer_reviews = [PeerReview(student_id=student_id, submission_id=submission_id)
                    for student_id, submission_ids in reviews.items()
                    for submission_id in submission_ids]
    log.info('Persisting %d peer reviews pairings for rubric %d' % (len(peer_reviews), rubric.id))
    PeerReview.objects.bulk_create(peer_reviews)


# TODO think about how multiple instances may react to each other trying to do this -- wrap in transactions, locks, etc.
def review_distribution_task(utc_timestamp):
    log.info('Starting review distribution at %s' % utc_timestamp.isoformat())

    try:
        # TODO remove assignments with no due date
        prompts_for_distribution = CanvasAssignment.objects.filter(
            rubric_for_prompt__peer_review_distribution=None,
            rubric_for_prompt__reviewed_assignment__due_date_utc__lt=utc_timestamp
        )

        if not prompts_for_distribution:
            log.info('No prompts ready for review distribution.')
        else:
            courses = unique(map(lambda a: a.course, prompts_for_distribution))
            for course in courses:
                log.info('Persisting sections for course %d' % course.id)
                persist_sections(course.id)

                log.info('Persisting students for course %d' % course.id)
                persist_students(course.id)

            for prompt in prompts_for_distribution:
                log.info('Distributing reviews for prompt %d...' % prompt.id)

                try:
                    log.debug('Fetching and persisting submissions for prompt %d...' % prompt.id)
                    persist_submissions(prompt)
                    log.debug('Finished persisting submissions for prompt %d' % prompt.id)

                    log.debug('Distributing for prompt %d for review...' % prompt.id)
                    with transaction.atomic():
                        rubric = prompt.rubric_for_prompt
                        distribute_reviews(rubric)
                        distribution = rubric.peer_review_distribution
                        distribution.is_distribution_complete = True
                        distribution.distributed_at_utc = utc_timestamp  # TODO correct?
                        distribution.save()
                    log.debug('Finished review distribution for prompt %d' % prompt.id)

                except Exception as ex:
                    # TODO expose failed prompt distribution to health check
                    log.error('Skipping review distribution for prompt %d due to error' % prompt.id, ex)

                log.info('Finished distributing reviews for prompt %d' % prompt.id)
    except Exception as ex:
        # TODO expose failed "all" distribution to health check
        log.error('Review distribution failed due to uncaught exception', ex)
        raise ex

    log.info('Finished review distribution that began at %s' % utc_timestamp.isoformat())
