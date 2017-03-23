import re
import requests
from urllib.parse import urljoin
from django.conf import settings

_page_regex = re.compile('<(?P<page_url>.*)>.*rel="(?P<page_key>.*)"')
_routes = {
    'assignments': {'route': 'courses/%s/assignments'}
}


def _make_headers():
    return {'Authorization': 'Bearer %s' % settings.CANVAS_API_TOKEN}


def _make_url(resource, params):
    return urljoin(settings.CANVAS_API_URL,
                   _routes[resource]['route'] % tuple(params))


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
    while True:
        headers = _make_headers()
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        resources += response.json()
        url = _parse_links(response).get('next')
        if not url:
            break
    return resources
