# Application Configuration

M-Write Peer Review uses environment variables to configure both its build and runtime environments.

## Build Configuration

The included Dockerfiles support ARGs that allow aspects of the build to be modified.  You can also
pass these as environment variables in OpenShift.

| Variable                         | Dockerfile | Description                                                                                              |
| -------------------------------- | ---------- | -------------------------------------------------------------------------------------------------------- |
| MPR_WORKING_DIRECTORY            | api, jobs  | The source and working directory for the API and jobs containers; optional (defaults to `/usr/src/app`). |
| MPR_API_URL                      | frontend   | The API URL for the frontend to use; **required**.                                                       |
| MPR_GOOGLE_ANALYTICS_TRACKING_ID | frontend   | Google analytics tracking ID                                                                             |

## Runtime Environment

### Backend Environment Variables

The API and jobs containers derive their runtime configuration from the following environment variables:

| Variable                         | Type                  | Optional (Default)   | Description                                                                                                                        |
| -------------------------------- | --------------------- | -------------------- | ---------------------------------------------------------------------------------------------------------------------------------- |
| MPR_DEBUG_MODE                   | boolean               | Yes (false)          | Sets Django's [DEBUG](https://docs.djangoproject.com/en/1.11/ref/settings/#debug) setting                                          |
| MPR_ALLOWED_HOSTS                | string[, string, ...] | No                   | Sets Django's [ALLOWED_HOSTS](https://docs.djangoproject.com/en/1.11/ref/settings/#allowed-hosts) setting                          |
| MPR_APP_HOST                     | string                | No                   | Used to identify LTI external tool assignments as belonging to this app                                                            |
| MPR_LANDING_ROUTE                | url                   | No                   | URL to redirect user after successful LTI launch                                                                                   | 
| MPR_FRONTEND_RESOURCES_DOMAIN    | domain name only      | No                   | Frontend site's domain name; used for CORS whitelist                                                                               | 
| MPR_LMS_URL                      | url                   | No                   | LMS (Canvas) URL; used for X-Frame-Options: ALLOW-FROM entry for iframe launches                                                   | 
| MPR_CANVAS_API_URL               | url                   | No                   | Canvas API URL; used for all Canvas API calls                                                                                      | 
| MPR_CANVAS_API_TOKEN             | token                 | No                   | Canvas API token; used for all Canvas API calls                                                                                    | 
| MPR_SECRET_KEY_PATH              | file path             | No                   | File to use for Django's [SECRET_KEY](https://docs.djangoproject.com/en/1.11/ref/settings/#secret-key) setting                     |
| MPR_SUBMISSIONS_PATH             | directory path        | No                   | Directory for submission storage; can be read-only for the API but must be read-write for the jobs container                       |
| MPR_LTI_CREDENTIALS_PATH         | json file path        | No                   | JSON file for LTI credentials                                                                                                      |
| MPR_DB_CONFIG_PATH               | json file path        | No                   | JSON file for Django's [DATABASES](https://docs.djangoproject.com/en/1.11/ref/settings/#databases) `'default'` entry               |
| MPR_TIMEZONE                     | Unix timezone         | No                   | Sets Django's [TIME_ZONE](https://docs.djangoproject.com/en/1.11/ref/settings/#time-zone) setting                                  | 
| MPR_SESSION_COOKIE_DOMAIN        | domain name only      | No                   | Sets Django's [SESSION_COOKIE_DOMAIN](https://docs.djangoproject.com/en/1.11/ref/settings/#session-cookie-domain) setting for CORS |
| MPR_CSRF_COOKIE_DOMAIN           | domain name only      | No                   | Sets Django's [CSRF_COOKIE_DOMAIN](https://docs.djangoproject.com/en/1.11/ref/settings/#csrf-cookie-domain) setting for CORS       |
| DJANGO_SETTINGS_MODULE           | Python module         | Yes (API); no (jobs) | Overrides the default settings file; must be set for the jobs container for cron to pick up environment variables                  |

### jobs-only Environment Variables

The jobs container also uses the following environment variables:

| Variable                    | Type                | Optional              | Description                                                                                                         |
| ---------------------       | ------------------- | ------------------    | ------------------------------------------------------------------------------------------------------------------- |
| MPR_EMAIL_HOST              | email               | No                    | Sets Django's [EMAIL_HOST](https://docs.djangoproject.com/en/1.11/ref/settings/#std:setting-EMAIL_HOST) setting     |
| MPR_EMAIL_PORT              | int                 | No                    | Sets Django's [EMAIL_PORT](https://docs.djangoproject.com/en/1.11/ref/settings/#std:setting-EMAIL_PORT) setting     |
| MPR_SERVER_FROM_EMAIL       | email               | No                    | Sets Django's [SERVER_EMAIL](https://docs.djangoproject.com/en/1.11/ref/settings/#std:setting-SERVER_EMAIL) setting |
| MPR_SERVER_TO_EMAILS        | email[, email, ...] | No                    | Used to derive Django's [ADMINS](https://docs.djangoproject.com/en/1.11/ref/settings/#std:setting-ADMINS) setting   |
| MPR_BACKUP_S3_BUCKET        | string              | Yes (see description) | AWS S3 bucket for storing SQL dumps and submission archives; leave unset to disable backups                         |
| MPR_BACKUP_PREFIX           | path                | Yes                   | Path to store temporary backup files; defaults to /srv/mwrite-peer-review-backups                                   |
| MPR_BACKUP_DB_CONFIG_FILE   | path                | Yes                   | Path to M-Write Peer Review's database config JSON file; defaults to /etc/mwrite-peer-review/database.json          |
| MPR_BACKUP_SUBMISSIONS_PATH | path                | Yes                   | Path to M-Write Peer Review's submission storage path; defaults to /srv/mwrite-peer-review/submissions              |
| MYSQLDUMP_OPTIONS           | string              | Yes                   | Command line options for mysqldump; required because MySQL 8 has different default behavior than 5.7                |

See the [API's](config/server/example/openshift/dc/api-dc.yaml) and [job container's](config/server/example/openshift/dc/jobs-dc.yaml) OpenShift deployment config for examples.
