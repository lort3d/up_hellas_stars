from io import StringIO
from django.test import TestCase
from django.core.management import call_command
from django.contrib.auth import get_user_model

class CreateDefaultUsersTest(TestCase):
    """Test cases for the create_default_users management command"""

    def test_create_users_successfully(self):
        """Test that admin and user accounts are created successfully"""
        User = get_user_model()
        self.assertEqual(User.objects.count(), 0)

        out = StringIO()
        call_command('create_default_users', stdout=out)

        self.assertEqual(User.objects.count(), 2)

        admin_user = User.objects.get(username='admin')
        self.assertTrue(admin_user.is_superuser)
        self.assertTrue(admin_user.is_staff)
        self.assertTrue(admin_user.is_active)
        self.assertIn('Successfully created superuser "admin"', out.getvalue())

        regular_user = User.objects.get(username='user')
        self.assertFalse(regular_user.is_superuser)
        self.assertFalse(regular_user.is_staff)
        self.assertTrue(regular_user.is_active)
        self.assertIn('Successfully created user "user"', out.getvalue())

    def test_users_already_exist(self):
        """Test that the command handles existing users gracefully"""
        User = get_user_model()
        User.objects.create_superuser('admin', 'admin@example.com', 'admin')
        User.objects.create_user('user', 'user@example.com', 'user')
        self.assertEqual(User.objects.count(), 2)

        out = StringIO()
        call_command('create_default_users', stdout=out)

        self.assertEqual(User.objects.count(), 2) # No new users should be created
        self.assertIn('User "admin" already exists.', out.getvalue())
        self.assertIn('User "user" already exists.', out.getvalue())
