#!/bin/bash
# entrypoint-celery.sh

# Start the Celery worker
exec celery -A starwarsrest worker --loglevel=info