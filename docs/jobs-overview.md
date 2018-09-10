# Scheduled Jobs Overview

M-Write Peer Review uses a separate container that runs [cron](https://en.wikipedia.org/wiki/Cron) in the foreground to
run regularly-scheduled jobs.  See [Application Configuration](application-configuration.md) for information on how
to configure the jobs container.  Alpine Linux provides BSD-like script folders under `/etc/periodic` to provide easy
scheduling (see the jobs container's [Dockerfile](/dockerfiles/jobs.Dockerfile) for more information).

## Error Reporting

The jobs container uses Django's [admin email handler](https://docs.djangoproject.com/en/1.11/topics/logging/) to send
emails for log events with a log level of `ERROR` or higher.  It sends them to the email addresses specified by the
`MPR_SERVER_TO_EMAILS` (see [Application Configuration](application-configuration.md) for all environment variables
related to emails).

## Jobs

### Review Distribution

M-Write Peer Review automatically distributes peer reviews based on the parent rubric's `peer_review_open_date` column
(see [Data Model](data-model.md) for more information).  This job is currently scheduled for every 15 minutes and
performs the following high level steps (see
[`peer_review.distribution.review_distribution_task`](/peer_review/distribution.py#L118) for implementation details):
1. Persist all assignments from all known courses
2. Find all prompt assignments with an associated *undistributed* rubric whose `peer_review_open_date` is now in the
past
3. Persist sections and students for all courses which are a parent of the assignments from step #2
4. For each prompt, persist all its submissions (metadata to the DB, submission files themselves to the submission
storage volume)
5. In a database transaction, create peer review pairings and persist them

Errors that occur on step #4 do not interrupt the whole process; rather, the prompt with a problem will be skipped until
the next 15 minute interval.  Other prompts for distribution will still be processed.

### Automated Backups

M-Write Peer Review has a scheduled task to back up its MySQL database and submission storage volume to an S3 bucket.
The S3 bucket to use is specified by the `MPR_BACKUP_S3_BUCKET` environment variable (see
[Application Configuration](application-configuration.md) for more environment variables affecting automated backups).
The current cadence for backups is daily (but see [#351](https://github.com/M-Write/mwrite-peer-review/issues/351)).

The backup script is [`scripts/backup_data.bash`](/scripts/backup_data.bash), which can also be used on its own / via
`oc rsh` to make a backup at any time.
