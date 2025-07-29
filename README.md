# Star Wars REST API

A Django REST API for Star Wars data with integration to SWAPI (Star Wars API).


## Assignment related notes
- Docker was used for the containarization of the project as POC of usual practices.
- Docker links the project directory in the containers, it only copies the requirments.
- Redis cache was not in the assignement instructions but it was implemented as a POC of usual practices. It Caches the get requests and invalidates the cache on model changes.
- Nginx, gunicorn cache was not in the assignement instructions but it was implemented as a POC of usual practices. Gunicorn starts with the reload flag as part of the dev env.
- Django was used because Im more familiar with the framework. Judging by the assignment instructions about "database errors", I supposed that you propably wanted to see a Data Access Object layer, even thought its not "native" to django logic.
- Django Rest Framework is used for the implementation of the REST logic, its widely adopted and provides ready to go authentication/permission methods, serialization etc.
- Regarding the creation of a service to fetch data from SWAPI, I decided to create a managment command that uses Celery to creates tasks and introduce async logic.
- I was trying to think of a way and introduce a "I feel a disturbance in the force" logic in that app, that why if you set the env var ALLOW_UNOFFICIAL_RECORDS to false, if you try to use the API to create records that are not found in SWAPI you will be presented with an error.
- Regarding the xxx, for very large numbers of records, batch create should be made in chucks and not load the memory indefinetily.
- To make it easier for the assignemet to be tested, after docker-compose up an admin and simple user is created, also SWAPI is used to populate the data. For the tests to run using coverage, run the ./run_tests.sh from the web container

## Feature updates
- For very large numbers of records fetched by SWAPI, batch create should be made in chunks and not as the current code implementation
- On next release, populate_swapi_data will facilitate celery beat to check for updated records


## Table of Contents

- [Features](#features)
- [Technologies Used](#technologies-used)
- [Architecture](#architecture)
- [Requirements](#requirements)
- [Getting Started](#getting-started)
  - [Quick Start with Docker](#quick-start-with-docker)
  - [Environment Variables](#environment-variables)
- [API Endpoints](#api-endpoints)
  - [Characters](#characters)
  - [Films](#films)
  - [Starships](#starships)
- [Authentication](#authentication)
- [Data Population](#data-population)
- [Testing](#testing)
- [Project Structure](#project-structure)

## Features

- RESTful API endpoints for Characters, Films, and Starships
- Data validation against SWAPI with option to allow custom records
- Search functionality for all entity types
- Pagination for large result sets
- Swagger API documentation
- Dockerized for easy deployment
- Redis caching for improved performance
- Celery for asynchronous tasks
- Authentication with token-based system

## Technologies Used

- Python 3.12
- Django 5.0
- Django REST Framework
- PostgreSQL
- Redis
- Celery
- Docker & Docker Compose
- Gunicorn
- SWAPI (Star Wars API)

## Architecture

The application follows a layered architecture pattern:

1. **Models Layer** - Django models defining the data structure
2. **DAO Layer** - Data Access Objects for database operations
3. **Services Layer** - External API integrations
4. **Views Layer** - Business logic and REST API endpoints
5. **Serializers Layer** - Data serialization/deserialization


## Requirements

- Docker
- Docker Compose

## Getting Started

### Quick Start with Docker

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd up_hellas_stars
   ```

2. Start the application:
   ```bash
   docker-compose up --build
   ```

3. The API will be available at `http://localhost:8000`

4. API documentation is available at `http://localhost:8000/api/docs/`

5. Admin interface is available at `http://localhost:8000/admin/`
   - Default superuser: username `admin`, password `admin`
   - Default simple user: username `user`, password `user`

### Environment Variables

| Variable | Description | Default Value |
|----------|-------------|---------------|
| `DEBUG` | Django debug mode | 1 |
| `SECRET_KEY` | Django secret key | Auto-generated |
| `DB_HOST` | Database host | db |
| `DB_NAME` | Database name | starwarsdb |
| `DB_USER` | Database user | starwarsuser |
| `DB_PASSWORD` | Database password | starwarspass |
| `DB_PORT` | Database port | 5432 |
| `ALLOW_UNOFFICIAL_RECORDS` | Allow creation of custom records not found in SWAPI | True |
| `REDIS_URL` | Redis connection URL | redis://localhost:6379/1 |
| `CELERY_BROKER_URL` | Celery broker URL | redis://localhost:6379/0 |
| `CELERY_RESULT_BACKEND` | Celery result backend | redis://localhost:6379/0 |

Note: Instead of using a DATABASE_URL, this project now uses individual environment variables for database configuration.

## API Endpoints

All endpoints support standard REST operations with pagination and filtering.

### Characters

- `GET /api/characters/` - List all characters
- `POST /api/characters/` - Create a new character
- `GET /api/characters/{id}/` - Get a specific character
- `PUT /api/characters/{id}/` - Update a character
- `PATCH /api/characters/{id}/` - Partially update a character
- `DELETE /api/characters/{id}/` - Delete a character
- `GET /api/characters/search/?name={name}` - Search characters by name

### Films

- `GET /api/films/` - List all films
- `POST /api/films/` - Create a new film
- `GET /api/films/{id}/` - Get a specific film
- `PUT /api/films/{id}/` - Update a film
- `PATCH /api/films/{id}/` - Partially update a film
- `DELETE /api/films/{id}/` - Delete a film
- `GET /api/films/search/?name={name}` - Search films by name

### Starships

- `GET /api/starships/` - List all starships
- `POST /api/starships/` - Create a new starship
- `GET /api/starships/{id}/` - Get a specific starship
- `PUT /api/starships/{id}/` - Update a starship
- `PATCH /api/starships/{id}/` - Partially update a starship
- `DELETE /api/starships/{id}/` - Delete a starship
- `GET /api/starships/search/?name={name}` - Search starships by name

## Authentication

The API uses session and token-based authentication. 
To get a token:

1. Create a user account through the admin interface or API
2. Request a token using the management command:
   ```bash
   docker-compose exec web python manage.py get_user_token <username>
   ```
3. Include the token in the Authorization header:
   ```
   Authorization: Token <your-token>
   ```

## Data Population

The application comes with a management command to populate the database with real Star Wars data from SWAPI:

```bash
docker-compose exec web python manage.py populate_swapi_data
```

This command will:
1. Fetch all films, characters, and starships from SWAPI
2. Create records in the database
3. Establish relationships between entities
4. Handle duplicates by checking SWAPI IDs

The population process is asynchronous using Celery.

## Testing

To run tests with coverage:
```bash
docker-compose exec web ./run_tests.sh
```

The project includes:
- Tests for data access objects
- Tests for models and services
- Tests for API endpoints
- Tests for management commands

## Project Structure

```
starwarsrest/
├── management/
│   └── commands/
│       ├── populate_swapi_data.py - Management command to populate data from SWAPI
│       └── get_user_token.py - Management command to get user authentication token
├── migrations/ - Database migration files
├── __init__.py
├── apps.py - Django app configuration
├── asgi.py - ASGI config for Django
├── cache_middleware.py - Redis cache middleware
├── cache_utils.py - Cache utilities
├── celery.py - Celery configuration
├── dao.py - Data Access Object patterns
├── models.py - Data models for Characters, Films, and Starships
├── permissions.py - Custom permission classes
├── serializers.py - Serialization logic
├── services.py - Business logic and SWAPI integration
├── settings.py - Django settings
├── signals.py - Django signals
├── tasks.py - Celery tasks
├── test_runner.py - Custom test runner
├── test_settings.py - Test settings
├── tests.py - Unit tests
├── tests_dao.py - DAO tests
├── tests_endpoints.py - Endpoint tests
├── tests_get_user_token.py - Token command tests
├── tests_management_command.py - Management command tests
├── urls.py - URL routing
├── views.py - API views and viewsets
└── wsgi.py - WSGI config for Django
```