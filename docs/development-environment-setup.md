# Setting Up Your Development Environment

These instructions will get you started with a development environment for M-Write Peer Review.

## Dependencies

You will need the following tools first:

* Python 3 (up to Python 3.6) and pip3
* MySQL 5.7 or later
* A recent version of NodeJS and npm

You will also need a Canvas API token (preferably in Canvas Dev) so that the tool can pull assignment data from
(at least one) test course(s).  **M-Write Peer Review is tightly integrated with Canvas, and thus this step is
required.**

## Cloning The Project

You can clone the following URL:

```bash
$ git clone https://github.com/M-Write/mwrite-peer-review.git
```

If you prefer to create a personal fork of this repository, use the GitHub UI and clone that repository instead.

## Backend Setup

Perform these steps in order (unless you know what you're doing).

### Create a new database on your running MySQL instance.

It can be named whatever you like (and will be configured below).

### Create a virtualenv

Using a Python virtual environment will make dependency management much easier.  Follow the instructions
[here](https://virtualenv.pypa.io/en/stable/).  It's best to create one virtualenv per project.  Put your new virtual
environment anywhere you like (`venv/` is `.gitignore`d if you prefer to keep your virtualenv collocated with
the project's source code).

### Create server configuration files

First, create directory under `config/server` to store local configuration files (I generally call mine `local`, making
the relative path `config/server/local`).

Create the following files:

#### `database.json`

Modify the configuration below to match your MySQL instance configuration.

```json
{
  "ENGINE": "django.db.backends.mysql",
  "NAME": "mwrite",
  "USER": "mwrite",
  "PASSWORD": "mwrite",
  "HOST": "127.0.0.1",
  "PORT": 3306
}
```

#### `lti_credentials.json`

This is a JSON file that contains a single key-value pair.  The key is the LTI consumer key and the value is the
LTI consumer secret.

```json
{"12345678901234567890": "secret"}
```

#### `secret.key`

This file is used verbatim for Django's
[SECRET_KEY](https://docs.djangoproject.com/en/1.11/ref/settings/#std:setting-SECRET_KEY) setting.

```text
something
```

#### `server.env`

Most of M-Write Peer Review's configuration is derived from environment variables.  The following is a minimal example;
make sure to replace the `<... ...>` placeholders with the real values.

```bash
export PS1="(mpr env) $PS1"

export DJANGO_SETTINGS_MODULE=mwrite_peer_review.settings.api
export MPR_DEBUG_MODE=true

export MPR_ALLOWED_HOSTS=localhost
export MPR_APP_HOST=api.peer-review-nonprod.mwrite.openshift.dsc.umich.edu
export MPR_LANDING_ROUTE=http://localhost:8080
export MPR_FRONTEND_RESOURCES_DOMAIN=localhost:8080

export MPR_LMS_URL=https://umich-dev.instructure.com
export MPR_CANVAS_API_URL=https://umich-dev.instructure.com/api/v1/
export MPR_CANVAS_API_TOKEN=<...your Canvas API token...>

export MPR_SECRET_KEY_PATH=config/server/local/secret.key
export MPR_SUBMISSIONS_PATH=<...some temporary path...>
export MPR_LTI_CREDENTIALS_PATH=config/server/local/lti_credentials.json
export MPR_DB_CONFIG_PATH=config/server/local/database.json
export MPR_TIMEZONE=America/Detroit

export MPR_SESSION_COOKIE_DOMAIN=localhost
export MPR_CSRF_COOKIE_DOMAIN=localhost
```

You will `source` this file before running the API.

### Activate Your Environment

Activate your virtualenv and source the environment file we just created:

```bash
$ source venv/bin/activate
$ source config/local/server.env
```

*(Tip: You can combine the above two commands in a bash alias to save a few keystrokes. I.e., put the following in your
`~/.bashrc`: `alias mpr='source venv/bin/activate && source config/local/server.env'`)*

### Install Backend Dependencies

Install the backend dependencies:

```bash
$ pip install -r requirements.txt
```

### Run database migrations to set up your (new, empty) database

```bash
$ ./manage.py migrate
```

### Create test users

Open a Django shell:

```bash
$ ./manage.py shell
```

A Python REPL will open; enter the following:

```python
from django.contrib.auth.models import User
from rolepermissions.roles import assign_role

test_student = User.objects.create_user('test_student', password='testpass')
assign_role(test_student, 'student')
test_student.save()

test_instructor = User.objects.create_user('test_instructor', password='testpass')
assign_role(test_instructor, 'instructor')
test_instructor.save()
```

The above steps will create two test users, one with the `student` role and the other with the `instructor` role.  You
will use those to log into the app.

## Frontend Setup

### Install Frontend Dependencies

```bash
$ npm install
```

## Running The App

### Backend

In a new terminal window, activate your virtualenv and source the server environment as described
[above](#activate-your-environment).

Then run the following:

```bash
$ ./manage.py runserver
```

Django will start its development server and watch your Python source code for changes; it will automatically restart
the server to load new code when you save Python files.

### Frontend

In a new terminal window, run the following:

```bash
$ npm run dev
```

NPM is configured to watch the Javascript source code and rebuild it automatically when you save changes.

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
