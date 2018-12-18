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

    latestTimestamp: str = None
    latestIntervalSeconds: float = None
    latestIntervalOk: bool = False

    latestMessage: JobLog = JobLog.objects.order_by('-' + JobLog.timestamp.field_name).first()

    if (latestMessage is not None):
        latestTimestamp = latestMessage.timestamp.isoformat()
        latestIntervalSeconds = (now - latestMessage.timestamp).total_seconds()
        latestIntervalOk = latestIntervalSeconds < jobIntervalSeconds

    jobsResult = {
        'latestTimestamp': latestTimestamp,
        'latestIntervalSeconds': latestIntervalSeconds,
        'latestIntervalOk': latestIntervalOk,
        'ok': latestIntervalOk,  # watchman requires "ok"; undocumented
    }

    if (not latestTimestamp):
        jobsResult['errorMessage'] = 'Unable to find a timestamp for the latest job run.'
    elif (not latestIntervalOk):
        jobsResult['errorMessage'] = 'Latest job run is not within the past {} minutes.'.format(jobIntervalMinutes)

    return {
        'jobs': jobsResult,
    }
