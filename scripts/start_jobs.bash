#!/usr/bin/env bash

set -x
printenv >> /etc/environment
crond -f
