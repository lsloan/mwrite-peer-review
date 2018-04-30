# M-Write Peer Review

## Deployment Overview

M-Write Peer Review is intended to be hosted using Docker containers, and comes with three Dockerfiles
for the different parts of the application.  They are:

- [dockerfiles/api.Dockerfile](dockerfiles/api.Dockerfile) -- The Django-based API (and legacy views, for now) hosted with [gunicorn](http://gunicorn.org/)
- [dockerfiles/frontend.Dockerfile](dockerfiles/frontend.Dockerfile) -- A VueJS SPA frontend hosted with Apache httpd
- [dockerfiles/api.Dockerfile](dockerfiles/api.Dockerfile) -- A backend container for scheduled jobs (currently just review distribution)

With the proper build arguments (see [here](#build-configuration)) and runtime environment variables (see [here](#runtime-environment)),
this app should be able to be run just using Docker; however, documentation for running M-Write Peer Review
using the OpenShift Container Platform is also provided.

## Build Configuration

The included Dockerfiles support ARGs that allow aspects of the build to be modified.  You can also
pass these as environment variables in OpenShift.

| Variable                         | Dockerfile  | Description                                                                                              |
| -------------------------------- | ----------  | -------------------------------------------------------------------------------------------------------- |
| MPR_WORKING_DIRECTORY            | api, jobs   | The source and working directory for the API and jobs containers; optional (defaults to `/usr/src/app`). |
| MPR_API_URL                      | frontend    | The API URL for the frontend to use; **required**.                                                       |
| MPR_GOOGLE_ANALYTICS_TRACKING_ID | tracking ID | Google analytics tracking ID                                                                             |

## Runtime Environment

_**TODO** -- need to separate these by container type (job / API)_

The API and jobs containers derive their runtime configuration from the following environment variables:

| Variable                         | Type                  | Optional (Default) | Description                                                                                                                        |
| -------------------------------- | --------------------- | ------------------ | ---------------------------------------------------------------------------------------------------------------------------------- |
| MPR_DEBUG_MODE                   | boolean               | Yes (false)        | Sets Django's [DEBUG](https://docs.djangoproject.com/en/1.11/ref/settings/#debug) setting                                          |
| MPR_ALLOWED_HOSTS                | string[, string, ...] | No                 | Sets Django's [ALLOWED_HOSTS](https://docs.djangoproject.com/en/1.11/ref/settings/#allowed-hosts) setting                          |
| MPR_APP_HOST                     | string                | No                 | Used to identify LTI external tool assignments as belonging to this app                                                            |
| MPR_LANDING_ROUTE                | url                   | No                 | URL to redirect user after successful LTI launch                                                                                   | 
| MPR_FRONTEND_RESOURCES_DOMAIN    | domain name only      | No                 | Frontend site's domain name; used for CORS whitelist                                                                               | 
| MPR_LMS_URL                      | url                   | No                 | LMS (Canvas) URL; used for X-Frame-Options: ALLOW-FROM entry for iframe launches                                                   | 
| MPR_CANVAS_API_URL               | url                   | No                 | Canvas API URL; used for all Canvas API calls                                                                                      | 
| MPR_CANVAS_API_TOKEN             | token                 | No                 | Canvas API token; used for all Canvas API calls                                                                                    | 
| MPR_SECRET_KEY_PATH              | file path             | No                 | File to use for Django's [SECRET_KEY](https://docs.djangoproject.com/en/1.11/ref/settings/#secret-key) setting                     |
| MPR_SUBMISSIONS_PATH             | directory path        | No                 | Directory for submission storage; can be read-only for the API but must be read-write for the jobs container                       |
| MPR_LTI_CREDENTIALS_PATH         | json file path        | No                 | JSON file for LTI credentials                                                                                                      |
| MPR_DB_CONFIG_PATH               | json file path        | No                 | JSON file for Django's [DATABASES](https://docs.djangoproject.com/en/1.11/ref/settings/#databases) `'default'` entry               |
| MPR_TIMEZONE                     | Unix timezone         | No                 | Sets Django's [TIME_ZONE](https://docs.djangoproject.com/en/1.11/ref/settings/#time-zone) setting                                  | 
| MPR_SESSION_COOKIE_DOMAIN        | domain name only      | No                 | Sets Django's [SESSION_COOKIE_DOMAIN](https://docs.djangoproject.com/en/1.11/ref/settings/#session-cookie-domain) setting for CORS |
| MPR_CSRF_COOKIE_DOMAIN           | domain name only      | No                 | Sets Django's [CSRF_COOKIE_DOMAIN](https://docs.djangoproject.com/en/1.11/ref/settings/#csrf-cookie-domain) setting for CORS       |
| MPR_GOOGLE_ANALYTICS_TRACKING_ID | tracking ID           | No                 | Google analytics tracking ID for legacy views; **deprecated**                                                                      |

The jobs container also uses the following environment variables:

| Variable              | Type                | Optional (default) | Description                                                                                                         |
| --------------------- | ------------------- | ------------------ | ------------------------------------------------------------------------------------------------------------------- |
| MPR_EMAIL_HOST        | email               | No                 | Sets Django's [EMAIL_HOST](https://docs.djangoproject.com/en/1.11/ref/settings/#std:setting-EMAIL_HOST) setting     |
| MPR_EMAIL_PORT        | int                 | No                 | Sets Django's [EMAIL_PORT](https://docs.djangoproject.com/en/1.11/ref/settings/#std:setting-EMAIL_PORT) setting     |
| MPR_SERVER_FROM_EMAIL | email               | No                 | Sets Django's [SERVER_EMAIL](https://docs.djangoproject.com/en/1.11/ref/settings/#std:setting-SERVER_EMAIL) setting |
| MPR_SERVER_TO_EMAILS  | email[, email, ...] | No                 | Used to derive Django's [ADMINS](https://docs.djangoproject.com/en/1.11/ref/settings/#std:setting-ADMINS) setting   |

See the [API's OpenShift deployment](config/server/example/openshift/dc/api-dc.yaml) config for examples.
  
## OpenShift Setup

As mentioned previously, M-Write Peer Review supports being run using Docker; however, at the time of this writing
the OpenShift Container Platform (version 3.6) is used in production.  The instructions below demonstrate how to
set up an environment given an empty project (referred to hereafter as the `mwrite-peer-review-dev` namespace).
Refer frequently to the OpenShift Container Platform [documentation](https://docs.openshift.com/container-platform/3.6/dev_guide/index.html).

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

Examples of all of these are available in the [config/server/example/openshift](config/server/example/openshift)
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
        $ python -c "import string,random; uni=string.ascii_letters+string.digits+string.punctuation; print ''.join([random.SystemRandom().choice(uni) for i in range(random.randint(45,50))])" >> secret.key
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

Any LTI method can be used; an example [lti_config.xml](config/server/example/lti_config.xml)
has been included.
