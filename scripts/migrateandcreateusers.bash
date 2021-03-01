#!/bin/sh

python manage.py migrate

python manage.py createuser --username=test_student --password=testpass --role=student

python manage.py createuser --username=test_instructor --password=testpass --role=instructor
