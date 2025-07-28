from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from django.core.exceptions import ValidationError


class Command(BaseCommand):
    help = 'Retrieve or generate authentication token for a user'

    def add_arguments(self, parser):
        parser.add_argument('username', type=str, help='Username to get token for')

    def handle(self, *args, **options):
        username = options['username']

        try:
            # Try to get the user
            user = User.objects.get(username=username)
            self.stdout.write(
                self.style.SUCCESS(f'Found user: {user.username}')
            )
        except User.DoesNotExist:
            self.stdout.write(
                self.style.ERROR(f'User {username} does not exist. Use --create-user to create them.')
            )
            return

        # Get or create the token for the user
        token, created = Token.objects.get_or_create(user=user)
        
        if created:
            self.stdout.write(
                self.style.SUCCESS(f'Created new token for {user.username}: {token.key}')
            )
        else:
            self.stdout.write(
                self.style.SUCCESS(f'Existing token for {user.username}: {token.key}')
            )