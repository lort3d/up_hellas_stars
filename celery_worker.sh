#!/bin/bash
# Script to start Celery worker for the starwarsrest project

cd /app
celery -A starwarsrest worker --loglevel=info