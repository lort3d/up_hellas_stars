from io import StringIO
from django.test import TestCase
from django.core.management import call_command
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token


class GetUserTokenTest(TestCase):
    """Test cases for the get_user_token management command"""

    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )

    def test_create_token_for_existing_user(self):
        """Test creating token for existing user (when no token exists)"""
        
        # Capture command output
        out = StringIO()
        
        # Run the management command
        call_command('get_user_token', 'testuser', stdout=out)
        
        # Check that the command output contains success messages
        output = out.getvalue()
        self.assertIn('Found user: testuser', output)
        self.assertIn('Created new token for testuser:', output)
        
        # Check that a token was created
        token = Token.objects.get(user=self.user)
        self.assertIn(token.key, output)

    def test_get_token_for_existing_user(self):
        """Test getting token for existing user"""
        
        # Run the management command
        call_command('get_user_token', 'testuser')
        # Capture command output
        out = StringIO()
        
        # Run the management command
        call_command('get_user_token', 'testuser', stdout=out)
        call_command('get_user_token', 'testuser', stdout=out)
        
        # Check that the command output contains success messages
        output = out.getvalue()
        self.assertIn('Found user: testuser', output)
        self.assertIn('Existing token for testuser:', output)
        
        # Check that a token was created
        token = Token.objects.get(user=self.user)
        self.assertIn(token.key, output)

    def test_get_token_for_nonexistent_user(self):
        """Test getting token for nonexistent user"""
        # Capture command output
        out = StringIO()
        
        # Run the management command
        call_command('get_user_token', 'nonexistent', stdout=out)
        
        # Check that the command output contains error message
        output = out.getvalue()
        self.assertIn('User nonexistent does not exist', output)
        
        # Check that no token was created
        self.assertEqual(Token.objects.filter(user__username='nonexistent').count(), 0)