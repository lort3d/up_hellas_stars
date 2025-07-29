from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

class Command(BaseCommand):
    help = 'Creates default users (admin and user) if they do not exist.'

    def handle(self, *args, **options):
        User = get_user_model()
        if not User.objects.filter(username='admin').exists():
            User.objects.create_superuser('admin', 'admin@example.com', 'admin')
            self.stdout.write(self.style.SUCCESS('Successfully created superuser "admin"'))
        else:
            self.stdout.write(self.style.WARNING('User "admin" already exists.'))

        if not User.objects.filter(username='user').exists():
            User.objects.create_user('user', 'user@example.com', 'user')
            self.stdout.write(self.style.SUCCESS('Successfully created user "user"'))
        else:
            self.stdout.write(self.style.WARNING('User "user" already exists.'))
