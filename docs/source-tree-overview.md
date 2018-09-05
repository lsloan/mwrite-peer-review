# Source Tree Overview

This document is a brief description of the M-Write Peer Review source tree.

## `/`

The source root.

### `.babelrc`

[Babel](https://babeljs.io/) configuration file

### `.editorconfig`

[EditorConfig](https://editorconfig.org/) configuration file

### `.eslintignore`, `.eslintrc.js`

[ESLint](https://eslint.org/) configuration files

### `manage.py`

Django management script; see [here](https://docs.djangoproject.com/en/1.11/ref/django-admin/)

### `package.json`, `package-lock.json`

Frontend (NPM) dependency configuration

### `requirements.txt`

Backend (pip) dependency configuration

### `README.md`

Documentation [table of contents](../README.md)

## `build/`

This directory holds [webpack](https://webpack.js.org/) configuration files and other frontend-related build
configuration.  It should be checked into source control.

### `build/webpack.*.conf.js`

Webpack configuration files themselves

## `config/`

This directory holds the build-environment-specific webpack configuration.  See this directory if you want to configure
a specific environment (e.g. dev, test, prod) for the frontend.

## `server/`

This directory holds server configuration for local development.  **This directory is `.gitignore`d (with the exception
of `server/example`) and should *not* be checked into source control.**  Any files you create for setting up a new
development environment should go here (see [Development Environment Setup](development-environment-setup.md)).

### `server/example/`

This directory contains example environment variables for the API, including a production environment example and
LTI XML configuration file for adding M-Write Peer Review to a course in Canvas.

### `server/example/openshift`

This directory contains example OpenShift resources for setting up a new environment.

## `dist/`

This directory is where the frontend's built artifacts are located.  It is `.gitignore`d and should not be checked
into source control.

## `djangolti/`

This directory holds the Python code that allows Django to handle LTI launch requests.

## `dockerfiles/`

This directory holds the Dockerfiles used for building the containers used for hosting the app.  See
[Application Configuration](application-configuration.md) for more information.

## `docs/`

This directory holds technical documentation about M-Write Peer Review.

## `frontend/`

This is the source directory for the [Vue.js](https://vuejs.org/)-based SPA frontend.

## `mwrite_peer_review/`

This is the backend API's Django's project configuration.

### `mwrite_peer_review/settings/`

This package holds the backend's settings and configuration code.

### `mwrite_peer_review/urls.py`

This module is the API's URL routing configuration.

## `node_modules/`

Directory used by NPM for resolving frontend dependencies.  It is `.gitignore`d and should not be checked
into source control.

## `peer_review/`

This is the API's Python package.

## `scripts/`

This folder holds `bash` scripts used for various administration and deployment tasks, including starting the API
on the server side, S3 backups and review distribution.
