"""
Django settings for mwrite_peer_review project.

Generated by 'django-admin startproject' using Django 1.10.6.

For more information on this file, see
https://docs.djangoproject.com/en/1.10/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.10/ref/settings/
"""

import os
import json
from os import getenv


def read_file_from_env(var):
    filename = os.environ[var]
    with open(filename, 'r') as file:
        contents = file.read()
    return contents.strip()


def getenv_bool(var, default='0'):
    return getenv(var, default).lower() in ('yes', 'on', 'true', '1',)


def getenv_csv(var, default=''):
    val = getenv(var, default)

    if len(val) == 0:
        return []

    return [x.strip(' ') for x in val.split(',')]


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

SECRET_KEY = read_file_from_env('MPR_SECRET_KEY_PATH')

DEBUG = getenv_bool('MPR_DEBUG_MODE')

ALLOWED_HOSTS = getenv_csv('MPR_ALLOWED_HOSTS')

APP_HOST = os.environ['MPR_APP_HOST']

GOOGLE_ANALYTICS_TRACKING_ID = os.environ.get('MPR_GOOGLE_ANALYTICS_TRACKING_ID')

# Storage configuration
MEDIA_ROOT = os.environ['MPR_SUBMISSIONS_PATH']

# LTI configuration
LTI_CONSUMER_SECRETS = json.loads(read_file_from_env('MPR_LTI_CREDENTIALS_PATH'))
LTI_APP_REDIRECT = os.environ['MPR_LANDING_ROUTE']
LTI_ENFORCE_SSL = False  # TODO want this to be True in prod; add config for X-Forwarded etc.

# Canvas API configuration
CANVAS_API_URL = os.environ['MPR_CANVAS_API_URL']
CANVAS_API_TOKEN = os.environ['MPR_CANVAS_API_TOKEN']

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'whitenoise.runserver_nostatic',
    'django.contrib.staticfiles',
    'rolepermissions',
    'djangolti',
    'peer_review',
    'health_check',
    'health_check.db',
    'corsheaders'
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'peer_review.middleware.FixedUserAgentMiddleware',
    'peer_review.middleware.safari_iframe_launch_middleware'
]

AUTHENTICATION_BACKENDS = [
    'djangolti.backends.LtiBackend'
]
if DEBUG:
    AUTHENTICATION_BACKENDS += ['django.contrib.auth.backends.ModelBackend']
    LOGIN_REDIRECT_URL = '/debug/lti'

ROLEPERMISSIONS_MODULE = 'mwrite_peer_review.roles'

SESSION_COOKIE_NAME = 'id'
SESSION_COOKIE_AGE = 3600
SESSION_COOKIE_SECURE = not DEBUG
SESSION_COOKIE_HTTPONLY = True
SESSION_EXPIRE_AT_BROWSER_CLOSE = True
SESSION_COOKIE_DOMAIN = os.environ['MPR_SESSION_COOKIE_DOMAIN']
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
CSRF_HEADER_NAME = 'HTTP_X_CSRF_TOKEN'
CSRF_COOKIE_HTTPONLY = True
CSRF_COOKIE_SECURE = not DEBUG
CSRF_COOKIE_NAME = 'fp'
CSRF_COOKIE_DOMAIN = os.environ['MPR_CSRF_COOKIE_DOMAIN']
X_FRAME_OPTIONS = 'ALLOW-FROM %s' % os.environ['MPR_LMS_URL']
SAFARI_LAUNCH_COOKIE = 'safari_launch'
CORS_ALLOW_CREDENTIALS = True
CORS_ORIGIN_WHITELIST = [
    os.environ['MPR_FRONTEND_RESOURCES_DOMAIN']
]

ROOT_URLCONF = 'mwrite_peer_review.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'peer_review.context_processors.google_analytics'
            ],
        },
    },
]

WSGI_APPLICATION = 'mwrite_peer_review.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.10/ref/settings/#databases

DATABASES = {
    'default': json.loads(read_file_from_env('MPR_DB_CONFIG_PATH'))
}


# Password validation
# https://docs.djangoproject.com/en/1.10/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/1.10/topics/i18n/

LANGUAGE_CODE = 'en-us'
USE_I18N = True
USE_L10N = True
USE_TZ = True
TIME_ZONE = os.environ['MPR_TIMEZONE']
TIME_OUTPUT_FORMAT = '%b %-d %-I:%M %p'  # if running on Windows, replace - with #


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.10/howto/static-files/

# TODO hacky. separate static files into their own artifact
STATIC_URL = LTI_APP_REDIRECT if LTI_APP_REDIRECT[-1] == '/' else LTI_APP_REDIRECT + '/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'


LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'all': {
            'format': ('%(levelname)s %(asctime)s %(module)s %(process)d '
                       '%(thread)d %(message)s'),
        },
        'debug': {
            'format': ('%(asctime)s %(levelname)s %(message)s '
                       '%(pathname)s:%(lineno)d'),
        },
        'simple': {
            'format': '%(levelname)s %(name)s %(message)s'
        },
        'access_logs': {
            'format': '%(message)s',
        },

    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'debug',
        },
    },
    'loggers': {
        '': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': True,
        },
    },
}
