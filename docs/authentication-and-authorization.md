# Authentication and Authorization

## Overview

User authentication to M-Write Peer Review is only supported via LTI.  A launch URL (`/launch`) accepts an LTI `POST`
request and, if successful, generates a session cookie and redirects the user to the frontend domain.

## Design Constraints

The frontend itself is served unauthenticated, but it consumes an API which requires authentication on every request.
During the early stages of the frontend's design, I opted to use cookie-based authentication rather than a
[JSON Web Token (JWT)](https://jwt.io/)-based approach, for two reasons:
1. The only consumer of this API is the frontend, so all requests will come from a browser
2. JWTs are ill suited for session management (see
[here](http://cryto.net/~joepie91/blog/2016/06/13/stop-using-jwt-for-sessions/) for a detailed explanation of why)

Cookie have the benefit of browser security (i.e., they can be set as `Secure` and `HttpOnly`; M.P.R. does this
in production), but this choice has implications:
1. Users authenticate against the API via an LTI launch, so session cookies must be issues on the API side
2. Browsers can allow `HttpOnly` cookies to be shared between domains via the `Domain` attribute of the `Set-Cookie`
header
3. **However**, most browsers will only share cookies between a parent domain and subdomains.
4. (Furthermore, browsers do different things for cookies on `localhost`; Chrome, for example, considers all `localhost`
domains to be the same domain, regardless of the specified port.)

Ultimately this necessitates that the API be served on a subdomain of the frontend.  Currently we use
`api.peer-review.mwrite.ai.umich.edu` for the API and `peer-review.mwrite.ai.umich.edu` for the frontend.

Django supports passing the CSRF token as a cookie, so this cookie must also set the frontend in its `Domain` attribute.

In order to allow cross-domain requests, the API must send `Access-Control-Allow-Origin` headers for the frontend's
domain on every response. 

Finally, since session cookies have the `HttpOnly` attribute set (and are thus inaccessible from Javascript), the
app also has the following constraints:
1. Requests from the client to the API must use `XMLHttpRequest`'s `withCredentials` option set to `true` so that the
browser will send cookies along with every request (see
[here](https://developer.mozilla.org/en-US/docs/Web/API/XMLHttpRequest/withCredentials); in practice M.P.R.
uses [axios](https://github.com/axios/axios) for AJAX, but the same constraint applies).
2. The server must send the `Access-Control-Allow-Credentials` header with a value of `true` with every response

The API-side responsibilities described above are handled entirely by the
[django-cors-headers](https://github.com/ottoyiu/django-cors-headers) library, with its relevant configuration passed
in via environment variables (see [Application Configuration](application-configuration.md)).

The client has this logic encapsulated in the `services/api` module; use this for non-Vue-component scenarios and use
the `plugins/api` module for Vue / router-aware AJAX requests (the plugin version uses the service, but has the
additional behavior of redirecting the user to an error page if the API responds with an error).

## User Roles

M-Write Peer Review uses roles-based authorization (using the
[django-role-permissions](https://django-role-permissions.readthedocs.io/en/stable/) library) and has two roles:
1. Student (for the `Learner` LTI role)
2. Instructor (for the `Instructor`, `urn:lti:role:ims/lis/TeachingAssistant`, or `ContentDeveloper` LTI roles)

Writing Fellows are generally added to courses as TAs and are considered Instructors.

The API uses the `authorized_endpoint` and `authorized_json_endpoint` (see
[`peer_review.decorators`](/peer_review/decorators.py)) decorators to mark an endpoint as requiring a specific role.

The frontend also keeps track of the current user's role and uses it for routing.  See
[here](frontend-overview.md#routing) for more information.
