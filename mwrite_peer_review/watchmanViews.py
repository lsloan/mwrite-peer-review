from __future__ import unicode_literals

from http import HTTPStatus
from itertools import chain

import watchman
import watchman.settings
import watchman.views
from django.core.handlers.wsgi import WSGIRequest
from django.http import Http404
from django.utils.translation import ugettext as _
from jsonview.decorators import json_view


def findKey(searchKey: str, data: dict) -> str:
    '''
    Search through a dictionary, which contains nested dictionaries or
    lists of nested dictionaries, looking for a specific key name.  This
    generator will yield the various values of the serach keys it finds.

    :param searchKey: str: Name of the key to find in the dictionaries.
    :param data: dict: A dictionary of nested (lists of) dictionaries.
    :return: A generator yielding one or more occurrences of `searchkey` values.
    '''
    for key, value in data.items():
        if key == searchKey:
            yield value
        elif isinstance(value, dict):
            for result in findKey(searchKey, value):
                yield result
        elif isinstance(value, list):
            for nestedDict in value:
                for result in findKey(searchKey, nestedDict):
                    yield result


@json_view
def ping(request: WSGIRequest) -> (dict, int, dict):
    '''
    Instead of watchman's default `ping()` (which simply returns "pong"), follow
    UMich recommendations to return a terse application status.
    Use watchman's own "run_checks" to run all the checks.
    Then reduce the check results to a single status based on
    whether the checks ended OK and their error messages or stacktraces.

    :param request: WSGIRequest object for the request.
    :return: Tuple containing:
        a dictionary with key "status" containing "OK" or "ERROR: [message]";
        HTTP status code;
        a dictionary of response headers.
        This will be turned into a complete response by `json_view`.
    '''
    checkResults, ok = watchman.views.run_checks(request)

    if not checkResults:
        raise Http404(_('No checks found'))

    httpStatus: int = HTTPStatus.OK if ok else int(watchman.settings.WATCHMAN_ERROR_CODE)

    briefResult: dict = None

    if (ok and ('error' not in checkResults)):
        # "error" appeared in checkResults when a bug in the code caused a stack dump.
        # However, "ok" was still "True" regardless of the error.  So, check for both.
        briefResult = {'status': 'OK'}
    else:
        errorMessages: str = '", "'.join(chain(
            findKey('errorMessage', checkResults),
            findKey('stacktrace', checkResults)))
        errorMessages = ('"' + errorMessages + '"'
                         if (errorMessages)
                         else '[error messages not found]')
        briefResult = {'status': 'ERROR: ' + errorMessages}

    responseHeaders: dict = {}
    if watchman.settings.EXPOSE_WATCHMAN_VERSION:
        responseHeaders[watchman.views.WATCHMAN_VERSION_HEADER] = watchman.__version__

    return briefResult, httpStatus, responseHeaders


@json_view
def index(request: WSGIRequest) -> (dict, int):
    '''
    Following UMich recommendations, provide a status index page that
    refers to other status pages with info about the application.  This
    index page should also include application version, hostname, and
    dependency information.

    :param request: WSGIRequest object for the request.
    :return: Tuple containing:
        a dictionary with key "status" containing "OK" or "ERROR: [message]";
        HTTP status code.
        This will be turned into a complete response by `json_view`.
    '''
    baseUrl: str = request.build_absolute_uri()
    statusUrls: dict = {
        statusEntry: baseUrl + statusEntry
        for statusEntry in ('ping', 'details', 'dashboard')}

    return statusUrls, HTTPStatus.MULTIPLE_CHOICES
