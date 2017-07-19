import logging

from toolz.itertoolz import unique
from toolz.functoolz import thread_last

from django.db import transaction

from peer_review.etl import persist_students, persist_submissions
from peer_review.models import CanvasAssignment

log = logging.getLogger(__name__)


def distribute_reviews(prompt_id):
    raise NotImplemented()


# TODO think about how multiple instances may react to each other trying to do this -- wrap in transactions, locks, etc.
def review_distribution_task(utc_timestamp):
    log.info('Starting review distribution at %s' % utc_timestamp)

    try:
        # TODO remove assignments with no due date
        prompts_for_distribution = CanvasAssignment.objects.filter(
            rubric_for_prompt__peer_review_distribution=None,
            rubric_for_prompt__revision_assignment__due_date_utc__lt=utc_timestamp
        )

        if not prompts_for_distribution:
            log.info('No prompts ready for review distribution.')
        else:
            course_ids = unique(map(lambda a: a.course_id, prompts_for_distribution))
            for course_id in course_ids:
                log.info('Persisting students for course %d' % course_id)
                persist_students(course_id)

            for prompt in prompts_for_distribution:
                log.info('Distributing reviews for prompt %d...' % prompt.id)

                with transaction.atomic():
                    try:
                        log.debug('Fetching and persisting submissions for prompt %d...' % prompt.id)
                        persist_submissions(prompt.course_id, prompt.id)
                        log.debug('Finished persisting submissions for prompt %d' % prompt.id)

                        log.debug('Distributing for prompt %d for review...' % prompt.id)
                        distribute_reviews(prompt.id)
                        log.debug('Finished review distribution for prompt %d' % prompt.id)

                        distribution = prompt.rubric_for_prompt.peer_review_distribution
                        distribution.is_distribution_complete = True
                        distribution.distributed_at_utc = utc_timestamp  # TODO correct?
                        distribution.save()

                    except Exception as ex:
                        # TODO expose failed prompt distribution to health check
                        log.error('Skipping review distribution for prompt %d due to error' % prompt.id, ex)

                log.info('Finished distributing reviews for prompt %d' % prompt.id)
    except Exception as ex:
        # TODO expose failed "all" distribution to health check
        log.error('Review distribution failed due to uncaught exception', ex)
        raise ex

    log.info('Finished review distribution that began at %s' % utc_timestamp)
