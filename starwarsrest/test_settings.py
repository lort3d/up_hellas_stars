"""
Test settings for starwarsrest project.
These settings are used when running tests to ensure a clean database schema.
"""

import sys
from .settings import *
import dj_database_url

# Use a separate schema for tests in the same PostgreSQL database
# This ensures a fresh schema for each test run while keeping the same engine
DATABASES = {
    'default': dj_database_url.parse(
        config('DATABASE_URL', default='postgresql://starwarsuser:starwarspass@localhost:5432/starwarsdb')
    )
}

# Modify the database configuration to use a separate test schema
if 'test' in sys.argv or 'test_coverage' in sys.argv:
    DATABASES['default']['TEST'] = {
        'NAME': 'test_starwarsdb',
        'CREATE_DB': False,  # We'll create the schema ourselves
    }
    # Use a separate schema for tests
    DATABASES['default']['OPTIONS'] = {
        'options': '-c search_path=test_starwarsdb,public'
    }

# Use our custom test runner
TEST_RUNNER = 'starwarsrest.test_runner.SchemaTestRunner'

# Disable migrations for faster tests
class DisableMigrations:
    def __contains__(self, item):
        return True
    
    def __getitem__(self, item):
        return None

MIGRATION_MODULES = DisableMigrations()

# Use a simpler password hasher for faster tests
PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.MD5PasswordHasher',
]

# Disable logging during tests for cleaner output
LOGGING_CONFIG = None