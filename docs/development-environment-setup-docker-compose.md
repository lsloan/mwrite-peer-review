# Development Environment Setup (Docker-Compose)

These instructions will get you started with a development environment for M-Write Peer Review.

## Dependencies

You will need the following tools first:

* [Docker](https://www.docker.com/products/docker-desktop)

You will also need a Canvas API token (preferably in Canvas Dev) so that the tool can pull assignment data from (at least one) test course(s).  **M-Write Peer Review is tightly integrated with Canvas, and thus this step is required.**

## Cloning The Project

You can clone the following URL:

```bash
$ git clone https://github.com/M-Write/mwrite-peer-review.git
```

If you prefer to create a personal fork of this repository, use the GitHub UI and clone that repository instead.

### Create server configuration files

There is a directory here with local configuration in `.local`

#### `database.json`

Contains the database configuration credentials, pre-populated for local host

#### `lti_credentials.json`

This is a JSON file that contains a single key-value pair.  The key is the LTI consumer key and the value is the LTI consumer secret.

#### `secret.key`

This file is used verbatim for Django's
[SECRET_KEY](https://docs.djangoproject.com/en/1.11/ref/settings/#std:setting-SECRET_KEY) setting.

#### `.env`

Note: The .env file needs to go at the root level of the project.

Most of M-Write Peer Review's configuration is derived from environment variables.  The following is a minimal example;
make sure to replace the `<... ...>` placeholders with the real values.  See
[Application Configuration](application-configuration.md) for more information.

```bash
DJANGO_SETTINGS_MODULE=mwrite_peer_review.settings.api
MPR_DEBUG_MODE=true

MPR_ALLOWED_HOSTS=localhost,0.0.0.0
MPR_APP_HOST=dev-api-mwrite-peer-review.tl.it.umich.edu
MPR_LANDING_ROUTE=http://localhost:8080
MPR_FRONTEND_RESOURCES_DOMAIN=localhost:8080

MPR_LMS_URL=https://umich-dev.instructure.com
MPR_CANVAS_API_URL=https://umich-dev.instructure.com/api/v1/
MPR_CANVAS_API_TOKEN=<...your Canvas API token...>

MPR_SECRET_KEY_PATH=.local/secret.key
MPR_SUBMISSIONS_PATH=<...some temporary path...>
MPR_LTI_CREDENTIALS_PATH=.local/lti_credentials.json
MPR_DB_CONFIG_PATH=.local/database.json
MPR_TIMEZONE=America/Detroit

MPR_SESSION_COOKIE_DOMAIN=localhost
MPR_CSRF_COOKIE_DOMAIN=localhost
```

You will `source` this file before running the API.

## Backend Setup

Docker compose now can be used to set these all up. The typical pattern is
# Bring all the conatiners down
docker-compose down
# Build all the containers
docker-compose build
# Bring all the containers up (add -d to detach them)
docker-compose up 

The MySQL database files are stored locally in the .data directory.  Remove this directory to clean the database.

### Run database migrations to set up your (new, empty) database (if necessary)

```bash
docker exec -it mwrite_api ./scripts/migrateandcreateusers.bash
```

### Create test users

These are created by the above script but you can use the `createuser` management command to add more.

```bash 
docker exec -it mwrite_api python manage.py createuser --username=test_student --password=testpass --role=student
docker exec -it mwrite_api python manage.py createuser --username=test_instructor --password=testpass --role=instructor
```

## Logging In

In [DEBUG](https://docs.djangoproject.com/en/1.11/ref/settings/#std:setting-DEBUG) mode, the API will serve a debug
login page at http://localhost:8000/accounts/login (assuming you haven't changed the port, etc.).  Navigate to that
page and log in with the credentials you created [above](#create-test-users).

When you log in, you will next be presented with a debug LTI parameters form.  This lets you set login parameters
that would normally be set via the LTI launch request.  In particular, M-Write Peer Review requires:
* The launch Canvas course ID
* The launch Canvas course title
* The Canvas user ID
* The user's LTI role
* The user's Canvas username

Once you have entered that information, you will be redirected to the frontend (by default, http://localhost:8080).

## Running the job
