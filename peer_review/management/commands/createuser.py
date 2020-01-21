from django.contrib.auth.models import User
from django.core.management.base import BaseCommand

from rolepermissions.roles import assign_role

import random, string

RANDOM_PASSWORD_DEFAULT_LENGTH = 8

class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('--username', dest='username', type=str, required=True)
        parser.add_argument('--email', dest='email', type=str, required=False)
        parser.add_argument('--password', dest='password', type=str, required=False)
        parser.add_argument('--role', dest='role', type=str, required=False)

    def handle(self, *args, **options):
        username = options.get('username')
        password = options.get('password')
        email = options.get('email')
        if password is None:
            password = ''.join(random.sample(string.ascii_letters, RANDOM_PASSWORD_DEFAULT_LENGTH))
            self.stderr.write ("Password not specified on command line generated password {}".format(password))
        
        role = options.get('role')
        if role is None:
            role = "student"

        try:
            # Might just be changing the user
            user_obj = User.objects.get(username=username)
        except User.DoesNotExist:
            self.stdout.write ("Creating regular user {}".format(username))
            user_obj = User.objects.create_user(username=username, email=email, password=password)
        finally: 
            user_obj.set_password(password)
            assign_role(user_obj, role)
            user_obj.save()
