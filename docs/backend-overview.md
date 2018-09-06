# Backend Overview

M-Write Peer Review uses Python 3 (currently up to 3.6) and Django (currently 1.11 -- the most recent LTS version) for
it's API.  It does *not* currently use [Django Rest Framework](http://www.django-rest-framework.org/), but is
approaching a level of complexity where it might benefit from it in the future.

## Configuration

The API is configured mostly via environment variables; see [Application Configuration](application-configuration.md)
for more information.  It's main settings module is
[`mwrite_peer_review.settings.api`](/mwrite_peer_review/settings/api.py); see there for implementation details.

## Organization

### Models

M.P.R.'s Django models are kept in [`peer_review.models`](/peer_review/models.py).  See [Data Model](data-model.md) for
an in-depth description.

### Queries

In order to provide an abstraction layer between the API endpoints and the database models, M.P.R. uses the classes
and methods in [`peer_review.queries`](/peer_review/queries.py).  These often also do some light transformation (adding
foreign keys for related resources for collation purposes is common).

### Decorators and Helpers

In order to insulate the application logic from relying too much on particulars of Django, a few helper decorators
have been created.  These decorators are kept in [`peer_review.decorators`](/peer_review/decorators.py).  (The following
list describes the most commonly used decorators, but is not exhaustive.)

#### `authorized_endpoint`

This decorator ensures that the specified
[function-based view](https://docs.djangoproject.com/en/1.11/topics/http/views/) will only be accessible if the user
is logged in with one of the specified `roles` (see
[Authentication and Authorization](authentication-and-authorization.md)).  The view function must return an object of
type [HttpResponse](https://docs.djangoproject.com/en/1.11/ref/request-response/#django.http.HttpResponse).

#### `authorized_json_endpoint`

This decorator is a convenience version of the [above](#authorized_endpoint) that serializes built-in Python data
structures returned from the view function to JSON responses (see [here](/peer_review/decorators.py#L46) for
implementation details).

### Session Management, Authentication and Authorization

M.P.R. use's Django's [session system](https://docs.djangoproject.com/en/1.11/topics/http/sessions/), but uses an
custom [authentication backend](https://docs.djangoproject.com/en/1.11/topics/auth/customizing/) (written by
[@ksofa2](https://github.com/ksofa2) and modified to assign user roles) for handling LTI launch requests.  See
[Authentication and Authorization](authentication-and-authorization.md), [the `djangolti` package](/djangolti) and
[`mwrite_peer_review.settings.api`](/mwrite_peer_review/settings/api.py) for more details.

### Routing

API routes are configured in [`mwrite_peer_review.urls`](/mwrite_peer_review/urls.py).  See the
[Django documentation](https://docs.djangoproject.com/en/1.11/topics/http/urls/) for an explanation of how the URL
dispatcher works.

### API Endpoints

M.P.R.'s API endpoints are all kept in [`peer_review.api.endpoints`](/peer_review/api/endpoints.py) (but the app is
at or near a tipping point of complexity where it might be helpful to break these up in the future).  In general,
they delegate the logic of fetching their data to the [`peer_review.queries`](/peer_review/queries.py) module.

### Canvas Integration and ETL

The [`peer_review.canvas` module](/peer_review/canvas.py) provides an interface which with M.P.R. fetches course,
section, student, assignment and submission data from Canvas.  It uses a
[data-driven approach](/peer_review/canvas.py#L14) to provide a uniform API for different types of resources; simply
use `retrieve(resource, params...)`, which returns built-in Python data structures.

The [`peer_review.etl` module](/peer_review/etl.py) provides functions to pull descriptions of various resources from
Canvas and persist them as Django models (see [Data Model](data-model.md)).  It also handles certain edge cases, such
as resolving multiple Canvas assignment due dates into a single due date.  This module is used both by the API and the
[jobs container](jobs-overview.md).
