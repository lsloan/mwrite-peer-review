import logging
from datetime import datetime
from collections import OrderedDict

from toolz.itertoolz import unique, frequencies, take

from django.db import transaction

from peer_review.etl import persist_students, persist_sections, persist_submissions, persist_assignments
from peer_review.models import CanvasCourse, CanvasStudent, CanvasAssignment, PeerReview, PeerReviewDistribution

log = logging.getLogger('management_commands')


DEFAULT_NUMBER_OF_REVIEWS_PER_STUDENT = 3


def add_to_distribution(rubric, students, n=DEFAULT_NUMBER_OF_REVIEWS_PER_STUDENT):
    reviews = PeerReview.objects.filter(submission__assignment=rubric.reviewed_assignment)
    submission_ids = reviews.values_list('submission', flat=True)
    review_counts = frequencies(submission_ids)

    new_reviews = []
    for student in students:
        sorted_review_counts = sorted(review_counts.items(), key=lambda p: p[1])
        submission_ids_for_review = map(
            lambda p: p[0],
            take(n, sorted_review_counts)
        )
        for submission_id in submission_ids_for_review:
            review = PeerReview(student=student, submission_id=submission_id)
            new_reviews.append(review)
            review_counts[submission_id] += 1

    PeerReview.objects.bulk_create(new_reviews)


def make_distribution(students, submissions, n=DEFAULT_NUMBER_OF_REVIEWS_PER_STUDENT):
    if submissions.count() < (DEFAULT_NUMBER_OF_REVIEWS_PER_STUDENT + 1):
        raise RuntimeError('Not enough submissions to distribute for assignment %s' % submissions.first().assignment_id)

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


def distribute_reviews(rubric, utc_timestamp, force_distribution=False):

    # TODO need this safety check?
    rubric_tz = rubric.peer_review_open_date.tzinfo
    if rubric.peer_review_open_date > datetime.now(rubric_tz):
        args = (rubric.id, rubric.peer_review_open_date)
        msg = 'peer reviews before rubric %d\'s peer review open date (which is %s)' % args
        if not force_distribution:
            msg = 'Tried to distribute %s' % msg
            log.error(msg)
            raise RuntimeError(msg)
        else:
            log.warning('Forcing distribution of %s' % msg)

    log.info('Beginning review distribution for rubric %d' % rubric.id)

    if rubric.distribute_peer_reviews_for_sections:

        if not rubric.sections.all().exists():
            msg = 'Rubric %d is setup to distribute within sections, but no sections are configured!'
            log.error(msg)
            raise RuntimeError(msg)

        log.info('Submissions for prompt %d will be distributed only within sections' % rubric.reviewed_assignment.id)
        reviews = {}
        for section in rubric.sections.all():
            log.info('Distributing reviews for section %d' % section.id)
            submissions = rubric.reviewed_assignment.canvas_submission_set.filter(author__in=section.students.all())
            author_ids = submissions.values_list('author', flat=True)
            students = CanvasStudent.objects.filter(id__in=author_ids)
            reviews_for_section, _ = make_distribution(students, submissions)

            for student_id in reviews_for_section.keys():
                if student_id in reviews:
                    msg = 'Duplicate students found when distributing for section %d' % section.id
                    log.error(msg)
                    raise RuntimeError(msg)

            reviews.update(reviews_for_section)
    else:
        log.info('Submissions for prompt %d will be distributed across all sections' % rubric.reviewed_assignment.id)
        submissions = rubric.reviewed_assignment.canvas_submission_set.all()
        students = CanvasStudent.objects.filter(id__in=submissions.values_list('author', flat=True))
        reviews, _ = make_distribution(students, submissions)

    peer_reviews = [PeerReview(student_id=student_id, submission_id=submission_id)
                    for student_id, submission_ids in reviews.items()
                    for submission_id in submission_ids]

    if len(peer_reviews) > 0:
        log.info('Persisting %d peer reviews pairings for rubric %d' % (len(peer_reviews), rubric.id))
        PeerReview.objects.bulk_create(peer_reviews)
        PeerReviewDistribution.objects.create(rubric=rubric,
                                              is_distribution_complete=True,
                                              distributed_at_utc=utc_timestamp)
    else:
        log.error('No peer reviews were created for rubric %d' % rubric.id)


# TODO this isn't concurrency safe.  we're going to get around this for now by just using a single instance per course
def review_distribution_task(utc_timestamp, force_distribution=False):
    log.info('Starting review distribution at %s' % utc_timestamp.isoformat())

    log.info('Persisting assignments for all courses')
    for course in CanvasCourse.objects.all():
        log.debug('Persisting assignments for course %d' % course.id)
        persist_assignments(course.id)

    try:
        prompts_for_distribution = CanvasAssignment.objects.filter(
            rubric_for_prompt__peer_review_distribution=None,
            rubric_for_prompt__peer_review_open_date__lt=utc_timestamp
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
                    log.info('Fetching and persisting submissions for prompt %d...' % prompt.id)
                    persist_submissions(prompt)
                    log.info('Finished persisting submissions for prompt %d' % prompt.id)

                    log.info('Distributing for prompt %d for review...' % prompt.id)
                    with transaction.atomic():
                        distribute_reviews(prompt.rubric_for_prompt, utc_timestamp, force_distribution)
                    log.info('Finished review distribution for prompt %d' % prompt.id)

                except Exception as ex:
                    # TODO expose failed prompt distribution to health check
                    log.exception('Skipping review distribution for prompt %d due to error' % prompt.id)

                log.info('Finished distributing reviews for prompt %d' % prompt.id)
    except Exception as ex:
        # TODO expose failed "all" distribution to health check
        log.exception('Review distribution failed due to uncaught exception')
        raise ex

    log.info('Finished review distribution that began at %s' % utc_timestamp.isoformat())
