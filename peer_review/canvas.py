import re
import requests
import mimetypes
from io import SEEK_SET, SEEK_END
from toolz.dicttoolz import merge
from urllib.parse import urljoin
from django.conf import settings

# TODO rethink the token state flow???

_page_regex = re.compile('<(?P<page_url>.*)>.*rel="(?P<page_key>.*)"')

# TODO would be nice to have a mechanism for declaring with HTTP verbs each resource supports
_routes = {
    'course':               {'route': 'courses/%s'},
    'assignments':          {'route': 'courses/%s/assignments'},
    'assignment':           {'route': 'courses/%s/assignments/%s'},
    'assignment-overrides': {'route': 'courses/%s/assignments/%s/overrides'},
    'submissions':          {'route': 'courses/%s/assignments/%s/submissions'},
    'submission_file':      {'route': 'courses/%s/assignments/%s/submissions/self/files'},
    'students':             {'route': 'courses/%s/users',
                             'params': {
                                 'enrollment_type[]': ['student'],
                                 'include[]':         ['enrollments']
                             }},
    'sections':             {'route': 'courses/%s/sections'}
}


def _make_headers():
    return {'Authorization': 'Bearer %s' % settings.CANVAS_API_TOKEN}


def _make_url(resource, params):
    return urljoin(settings.CANVAS_API_URL, _routes[resource]['route'] % tuple(params))


def _parse_links(response):
    link_header = response.headers.get('link')
    if link_header:
        link_parts = link_header.split(',')
        matches = [_page_regex.match(page) for page in link_parts]
        links = {match.group('page_key'): match.group('page_url')
                 for match in matches}
        return links


def retrieve(resource, *params):
    resources = []
    url = _make_url(resource, params)
    route_params = _routes[resource].get('params') if 'params' in _routes[resource] else {}
    while True:
        headers = _make_headers()
        response = requests.get(url, headers=headers, params=merge(route_params, {'per_page': 500}))  # TODO clean me
        response.raise_for_status()
        json_data = response.json()
        if isinstance(json_data, dict):
            resources = json_data
            break
        else:
            resources += json_data
        links = _parse_links(response)  # TODO may be able to replace with requests's link parsing
        url = links.get('next') if links else None
        if not url:
            break
        route_params = {}
    return resources


def delete(resource, *params):
    url = _make_url(resource, params)
    headers = _make_headers()
    response = requests.delete(url, headers=headers)
    response.raise_for_status()
    return response


def create(resource, *params, **kwargs):
    response = requests.post(_make_url(resource, params),
                             json=kwargs['data'],
                             headers=_make_headers())
    response.raise_for_status()
    return response.json()


def upload_submission(user_token, course_id, assignment_id, filename, contents, mime_type=None):

    # TODO don't do this
    saved_token = settings.CANVAS_API_TOKEN
    settings.CANVAS_API_TOKEN = user_token

    if not mime_type:
        mime_type, _ = mimetypes.guess_type(filename)
        if not mime_type:
            raise RuntimeError('Unknown MIME type for %s' % filename)

    contents.seek(0, SEEK_END)
    file_size = contents.tell()
    contents.seek(0, SEEK_SET)

    file_desc = {
        'name': filename,
        'size': file_size,
        'content_type': mime_type
    }
    pending_file_desc = create('submission_file', course_id, assignment_id, data=file_desc)

    file_upload_response = requests.post(pending_file_desc['upload_url'],
                                         data=pending_file_desc['upload_params'],
                                         files={'file': contents},
                                         allow_redirects=False)
    file_upload_response.raise_for_status()

    file_confirmation_response = requests.post(file_upload_response.headers['location'])
    file_confirmation_response.raise_for_status()

    # TODO remove this when we fix the above
    settings.CANVAS_API_TOKEN = saved_token

    return file_confirmation_response.json()
