# Frontend Overview

M-Write Peer Review has a SPA (Single Page App) frontend written in [Vue.js](https://vuejs.org/).  It uses
[NPM](https://www.npmjs.com/) for dependency management, [Babel](https://babeljs.io/) as an ES6 transpiler,
[webpack](https://webpack.js.org/) as a build management tool and [ESLint](https://eslint.org/) as its linter.
The frontend portion of M-Write Peer Review was created using the [Vue.js CLI tool](https://cli.vuejs.org/), but this
is not required for further development.

## Hosting / Artifacts

In production, M.P.R.'s frontend is built into a single file for each type of resource: HTML, Javascript and CSS.
It is served strictly from unauthenticated Apache HTTPD using our `frontend` container (see
[OpenShift Setup and Deployment](openshift-setup-and-deployment.md) for more details).

## Authentication

See [Authentication and Authorization](authentication-and-authorization.md).

## Components

The frontend uses Vue's [single-file component](https://vuejs.org/v2/guide/single-file-components.html) concept
pervasively. 

## Routing

The frontend uses [vue-router](https://router.vuejs.org/) for its frontend routing configuration.  One key design
goal is that **all of the frontend's state should be derived from the URL**; that is, any necessary request parameters
or other information required to fetch its data should be entirely encapsulated in the URL.  This preserves the ability
of users to (e.g.) bookmark a page and always come back to the same place.

As discussed in [Authentication and Authorization](authentication-and-authorization.md), M.P.R. uses roles-based
authorization.  The frontend keeps track of these roles and uses them to enable navigation only to views that the user
is authorized to see (the API also does this, so this is more of a convenience to the user -- the frontend can always
display a "permission denied" page).  See [here](/frontend/src/router/index.js), [here](/frontend/src/router/guards.js)
and [here](/frontend/src/router/helpers.js) for implementation details.

## Fetching and Using Data

There are many views in the app that "hydrate" their components with the data from a single API call.  This is fine as
long as that data never needs to be shared across multiple component subtrees; however, there are several situations
where the same (or similar) data needs to be shared across the app.  In these situations, we use
[Vuex](https://vuex.vuejs.org/) as a "single source of truth" for shared data.  This has proven particularly useful in
concert with Vue's [computed properties](https://vuejs.org/v2/guide/computed.html) support.  Together these allow a
developer to pull normalized data from the API and specify transformations *declaratively*.  The net result of this is
that the amount of mutable state (and therefore surface area for bugs) is drastically reduced (at the cost of a higher
initial learning curve).

In general, you should consider these as best practices:
* If data is only used for one component (or one tree of components), a direct AJAX call is fine
* If data is shared between multiple subtrees / across different sections of the app, use Vuex to pull normalized data
from the API and denormalize it with [Vuex getters](https://vuex.vuejs.org/guide/getters.html) or component-level
computed properties (I like to keep references to the Vuex `$store` as high in the component tree as possible -- ideally
at the page-level component, but YMMV)
* Regardless, try to keep mutable state to as few `data` entries as possible, and use computed properties for any
transformations that you need to do
