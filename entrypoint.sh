#!/bin/bash
# entrypoint.sh

# Run migrations
echo "Running migrations..."
python manage.py makemigrations
python manage.py migrate --noinput

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --noinput

# Create superuser if it doesn't exist
echo "Creating superuser..."
python manage.py shell -c "
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@example.com', 'admin')
    print('Superuser created.')
else:
    print('Superuser already exists.')
"

# Create a regular user if it doesn't exist
echo "Creating regular user..."
python manage.py shell -c "
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='user').exists():
    User.objects.create_user('user', 'user@example.com', 'user')
    print('Regular user created.')
else:
    print('Regular user already exists.')
"

# Populate SWAPI data only once
if [ ! -f /app/.swapi_data_populated ]; then
    echo "Populating SWAPI data..."
    python manage.py populate_swapi_data
    touch /app/.swapi_data_populated
    echo "SWAPI data populated."
else
    echo "SWAPI data already populated, skipping."
fi

# Start the application
exec "$@"