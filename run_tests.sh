#!/bin/bash
# run_tests.sh

echo "Starting test execution inside Docker container..."

# Make sure we're in the right directory
cd /app

# Run the tests with coverage using test settings
echo "Running tests with coverage..."
coverage run --source='.' manage.py test starwarsrest.tests -v 2

# Generate coverage report
echo "Generating coverage report..."
coverage report

# Generate HTML coverage report
echo "Generating HTML coverage report..."
coverage html

echo "Tests completed. Check coverage reports in htmlcov/ directory."