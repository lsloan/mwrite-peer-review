import logging
from datetime import datetime
from dateutil.tz import tzutc
from django.core.management import BaseCommand, CommandError
from peer_review.distribution import review_distribution_task

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Distributes submissions for peer review'

    def handle(self, *args, **options):
        try:
            review_distribution_task(datetime.now(tzutc()))
        except Exception as ex:
            logger.exception('Uncaught exception when running review distribution task')
            raise CommandError('Failed to start review distribution') from ex
