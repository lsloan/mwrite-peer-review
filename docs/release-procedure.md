# Release Procedure

The rest of the documentation (but especially [Application Configuration](application-configuration.md) and
[OpenShift Setup and Deployment](openshift-setup-and-deployment.md)) should be considered required reading.

## Steps

1. Merge from the `develop` branch to the `master` branch (**`master` is considered production-ready by definition**)
2. Create an annotated [tag](https://git-scm.com/book/en/v2/Git-Basics-Tagging) on `master` named for the version to be
released
    * M-Write Peer Review roughly adheres to a [semantic versioning](https://semver.org/) scheme; that is, it uses
    three digits in the form X.Y.Z, where X are major versions, Y are minor versions (generally used for per-term releases)
    and Z are bug fix versions.
3. Push `master` and the new tag
4. Start a new build in OpenShift
    ```bash
    $ oc start-build bc/mwrite-peer-review-prod-api
    $ oc start-build bc/mwrite-peer-review-prod-frontend
    $ oc start-build bc/mwrite-peer-review-prod-jobs
    `````````
5. If the new release entails database schema changes, take a backup (see [here](jobs-overview.md#automated-backups))
    ```bash
    $ oc get pods # find the current api pod
    $ oc rsh mwrite-peer-review-prod-api-X-YYYYY # where X and YYYYY are found in the previous step
    # scripts/backup_data.bash
    ```
6. Deploy the new build to production
    ```bash
    $ oc rollout latest dc/mwrite-peer-review-prod-api
    $ oc rollout latest dc/mwrite-peer-review-prod-frontend
    $ oc rollout latest dc/mwrite-peer-review-prod-jobs
    ```
7. If the new release entails database schema changes, perform a database migration
    ```bash
    $ oc get pods # find the new api pod
    $ oc rsh mwrite-peer-review-prod-api-X-YYYYY # where X and YYYYY are found in the previous step
    # DJANGO_SETTINGS_MODULE=mwrite_peer_review.settings.api ./manage.py migrate
    ```
    If you need to rollback, either use `manage.py migrate` (see
    [here](https://docs.djangoproject.com/en/1.11/ref/django-admin/#django-admin-migrate)) or restore the database from
    the backup taken in step #5.
8. Perform post-release testing
9. If this is the beginning of a new term, add M-Write Peer Review as an LTI external tool to the appropriate courses
