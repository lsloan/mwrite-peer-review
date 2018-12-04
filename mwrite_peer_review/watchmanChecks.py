from datetime import datetime

from dateutil.tz import tzutc
from watchman.decorators import check

from peer_review.models import JobLog


@check
def jobsCheck() -> dict:
    jobIntervalMinutes: int = 15
    jobIntervalToleranceMinutes: int = 2
    jobIntervalSeconds: int = (jobIntervalMinutes + jobIntervalToleranceMinutes) * 60

    now: datetime = datetime.now(tzutc())
    latestMessage: JobLog = JobLog.objects.order_by('-' + JobLog.timestamp.field_name).first()

    latestIntervalSeconds: int = (now - latestMessage.timestamp).total_seconds()

    return {
        'jobs': {
            'latestTimestamp': latestMessage.timestamp.isoformat(),
            'latestIntervalSeconds': latestIntervalSeconds,
            'latestIntervalOk': latestIntervalSeconds < jobIntervalSeconds,
            'ok': latestIntervalSeconds < jobIntervalSeconds,  # watchman requires "ok"; undocumented; bug?
        }
    }
