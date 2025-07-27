"""
Custom test runner for creating and cleaning up test schema.
"""

from django.test.runner import DiscoverRunner
from django.db import connection


class SchemaTestRunner(DiscoverRunner):
    """
    Custom test runner that creates a separate schema for tests.
    """

    def setup_databases(self, **kwargs):
        # Create the test schema before setting up databases
        with connection.cursor() as cursor:
            cursor.execute("CREATE SCHEMA IF NOT EXISTS test_starwarsdb")
            cursor.execute("SET search_path TO test_starwarsdb,public")
        
        # Call the parent method to continue with normal setup
        return super().setup_databases(**kwargs)

    def teardown_databases(self, old_config, **kwargs):
        # Clean up by dropping the test schema after tests
        with connection.cursor() as cursor:
            cursor.execute("DROP SCHEMA IF EXISTS test_starwarsdb CASCADE")
        
        # Call the parent method to continue with normal teardown
        return super().teardown_databases(old_config, **kwargs)