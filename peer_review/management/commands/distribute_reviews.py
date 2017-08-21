from datetime import datetime
from dateutil.tz import tzutc
from django.core.management import BaseCommand, CommandError
from peer_review.distribution import review_distribution_task


class Command(BaseCommand):
    help = 'Distributes submissions for peer review'

    def handle(self, *args, **options):
        try:
            review_distribution_task(datetime.now(tzutc()))
        except Exception as ex:
            raise CommandError('Failed to start review distribution') from ex
