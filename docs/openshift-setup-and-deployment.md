# OpenShift Setup and Deployment 

M-Write Peer Review uses container-based deployments and is intended to be hosted using Docker.  It comes with three Dockerfiles for the different parts of the application.

These are:
- [dockerfiles/api.Dockerfile](/dockerfiles/api.Dockerfile) -- The Django-based API served by [gunicorn](http://gunicorn.org/)
- [dockerfiles/frontend.Dockerfile](/dockerfiles/frontend.Dockerfile) -- A Vue.js SPA frontend hosted with Apache httpd
- [dockerfiles/jobs.Dockerfile](/dockerfiles/jobs.Dockerfile) -- A backend container for scheduled jobs (currently, review distribution and automated backups to S3)

With the proper build arguments (see [here](/docs/application-configuration.md#build-configuration)) and runtime
environment variables (see [here](/docs/application-configuration.md#runtime-environment)), this app should be able to
be run just using Docker; however, documentation for running M-Write Peer Review using the OpenShift Container Platform
is also provided below.

## Configuration

M-Write Peer Review uses environment variables to configure both its build and runtime environments.  See
[Application Configuration](/docs/application-configuration.md) for more information.

## Creating A New Production(-Like) Environment In OpenShift

As mentioned previously, M-Write Peer Review supports being run using Docker; however, at the time of this writing
the OpenShift Container Platform (version 3.6) is used in production.  The instructions below demonstrate how to
set up an environment given an empty project (referred to hereafter as the `mwrite-peer-review-dev` namespace).
Refer frequently to the OpenShift Container Platform [documentation](https://docs.openshift.com/container-platform/3.6/dev_guide/index.html).

### Automatic Backups to S3

The jobs container uses a weekly cron job to back up the configured database and submission storage volume to S3.
See [`dockerfiles/jobs.Dockerfile`](/dockerfiles/jobs.Dockerfile) and [`scripts/backup_data.bash`](/scripts/backup_data.bash) for
implementation details.  See [Application Configuration](/docs/application-configuration.md#jobs-only-environment-variables)
for information about the related environment variables.

### Accessing Private Github Repositories

To allow OpenShift to pull from a private Github repository:

1. Create a deployment key
    ```bash
    $ ssh-keygen -t rsa -C "you@email.com" -f mwrite-peer-review-github-key
    ```
2. Add the deployment key to your Github repository (see [here](https://developer.github.com/v3/guides/managing-deploy-keys/))
3. Add the key as an OpenShift secret
    ```bash
    $ oc secrets mwrite-peer-review-github-key --ssh-secret=mwrite-peer-review-github-key
    ```

### Creating a new MySQL database (only for nonprod)

To create a non-prod MySQL instance (production DBs in OpenShift are currently not recommended by the ITS Container
Team), do:

    ```bash
    oc new-app mysql-persistent --name mwrite-peer-review-dev-db \
        -p MYSQL_USER=username                                   \
        -p MYSQL_PASSWORD=password                               \ 
        -p MYSQL_DATABASE=db_name                                \
        -p MYSQL_ROOT_PASSWORD=root_password                     \
        -p VOLUME_CAPACITY=512Mi                                 \
        -p MYSQL_VERSION=5.7                                     \
        -p MEMORY_LIMIT=512Mi                                    \
        -p DATABASE_SERVICE_NAME=mwrite-peer-review-dev-db
    ```

### OpenShift Resources

When using OpenShift, a variety of resources are required:
- A persistent volume claim for submission storage
- A secret for sensitive / private details like LTI credentials, DB config (including passwords), etc.
- Imagestreams for storing Docker images
- Build and deployment configs
- Services
- Routes

Examples of all of these are available in the [config/server/example/openshift](/config/server/example/openshift)
directory; please refer to these (but keep an eye out for `<...redacted...>` entries -- these signify something
sensitive that will need to be replaced).

These should be created in roughly the following order:
1. Create the secret:
    ```bash
    $ oc create -f config/server/example/openshift/secret/secret.yaml
    ```
    N.B. The file data should be base64 encoded; you can create the different files as below:
    * `secret.key` -- secret key file for Django; generate with
        ```bash
        $ python -c "import string,random; uni=string.ascii_letters+string.digits+string.punctuation; print(''.join([random.SystemRandom().choice(uni) for i in range(random.randint(45,50))]))" >> secret.key
        ```
    * `lti_credentials.json`
        ```bash
        # to generate consumer_key / consumer_secret
        $ cat /dev/urandom | env LC_CTYPE=C tr -dc 'a-zA-Z0-9' | fold -w 32 | head -n 1
        ```
        ```json
        {"consumer_key": "consumer_secret"}
        ```
    * `database.json`
        ```json
        {
          "ENGINE": "django.db.backends.mysql",
          "NAME": "mwrite",
          "USER": "mwrite",
          "PASSWORD": "mwrite",
          "HOST": "192.168.99.100",
          "PORT": "3306"
        }
        ```
    * `aws_credentials`
        ```text
        [default]
        aws_access_key_id=<...redacted...>
        aws_secret_access_key=<...redacted...>
        ```
2. Create the persistent volume claim for submission file storage:
    ```bash
    $ oc create -f pvc.yaml
    ```
    N.B. It might be necessary to create a ticket with the container team
    to create the underlying volumes.  They will need to know the
    requested size and access mode.  Do *not* specify a volumeName (or
    tell them what you give it, if you do).
3. Create the imagestreams:
    ```bash
    # for python-based containers
    $ oc create -f config/server/example/openshift/is/python-imagestream.yaml 
    $ oc create -f config/server/example/openshift/is/api-imagestream.yaml
    $ oc create -f config/server/example/openshift/is/jobs-imagestream.yaml

    $ for httpd-based containers    
    $ oc create -f config/server/example/openshift/is/httpd-imagestream.yaml
    $ oc create -f config/server/example/openshift/is/frontend-imagestream.yaml
    ```
4. Import the base images from Dockerhub:
    ```bash
    $ oc import-image python:3-alpine --from=python:3-alpine
    $ oc import-image httpd:2.4-alpine --from=httpd:2.4-alpine
    ```
5. Create the build configs for each container:
    ```bash
    $ oc create -f config/server/example/openshift/bc/api-bc.yaml
    $ oc create -f config/server/example/openshift/bc/frontend-bc.yaml
    $ oc create -f config/server/example/openshift/bc/jobs-bc.yaml
    ```
    N.B. Make sure the `source.git` sections match the desired repository and branch details.
    
    You can also create GitHub webhooks for automatically building images, if desired; see
    [the OpenShift documentation](https://docs.openshift.com/container-platform/3.6/dev_guide/builds/triggering_builds.html#github-webhooks)
    and [the GitHub documentation](https://developer.github.com/webhooks/).
6. Create the deployment configs for each container:
    ```bash
    $ oc create -f config/server/example/openshift/dc/api-dc.yaml
    $ oc create -f config/server/example/openshift/dc/frontend-dc.yaml
    $ oc create -f config/server/example/openshift/dc/jobs-dc.yaml
    ```
    N.B. Pay particular attention to the `volume` and `volumeMounts` sections for the API and jobs
    containers to see how those are set up.
7. Create the services for the API and frontend:
    ```bash
    $ oc create -f config/server/example/openshift/service/api-service.yaml
    $ oc create -f config/server/example/openshift/service/frontend-service.yaml
    ```
8. Create the routes for the API and frontend:
    ```bash
    $ oc create -f config/server/example/openshift/service/api-route.yaml
    $ oc create -f config/server/example/openshift/service/frontend-route.yaml
    ```
    N.B. It is **absolutely critical** that the API domain be a subdomain of the frontend
    domain; otherwise browsers will not set the session cookie for both domains,
    regardless of CORS settings.
7. Edit the created buildconfig to correct the Git repository URL (TODO still needed?), remove
   the Github secret under the `spec.triggers` section and add the correct 
   secret under `spec.source.sourceSecret` and `spec.source.name`
8. Start builds for all containers:
    ```bash
    $ oc start-build bc/mwrite-peer-review-dev-api
    $ oc start-build bc/mwrite-peer-review-dev-jobs
    $ oc start-build bc/mwrite-peer-review-dev-frontend 
    ```
10. `oc rsh` to a running API or jobs container and run the Django migrations.

## Adding The Tool To Canvas

Any LTI method can be used; an example [lti_config.xml](/config/server/example/lti_config.xml)
has been included.

## Jobs Debugging
To start a `jobs` pod in debug mode with an interactive shell, using the `mwrite-peer-review-dev` project:

1. Download a copy of the YAML file used to start the pod: https://github.com/tl-its-umich-edu/openshift-jenkins-configs/blob/master/pods/mwrite-peer-review-dev-15m.yaml

2. Starting the pod in debug mode:
    ```sh
    oc debug -f mwrite-peer-review-dev-15m.yaml
    ```
    That will start an interactive shell, `ash`.  `bash` is also available and can be started on demand.
    
3. To start a Python shell with Django and other libraries for MPR loaded, run:

    ```sh
    ./manage.py shell
    ```

    * 💡 If the shell doesn't start properly, it may be necessary to set the following environment variable, then try running the shell again:

        ```sh
        export DJANGO_SETTINGS_MODULE="${DJANGO_SETTINGS_MODULE:-mwrite_peer_review.settings.jobs}"
        ```

### Using `faketime`

`libfaketime` is installed and can be used to force the pod's clock to be set to any specific time.  Its CLI tool is called `faketime` and can be used like this:

* `faketime '2020-11-08 01:00:00' ./manage.py shell` – Start an interactive Django shell.
* `faketime '2020-11-08 01:00:00' ./scripts/distribute_reviews.bash` – Start the peer review distribution job.

The latter example was used to verify that a bugfix for a post-DST error was working correctly.



