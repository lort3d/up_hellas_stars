# Star Wars REST API

A Dockerized Django REST API for Star Wars data with integration to the Star Wars API (SWAPI).

## Features

- Dockerized application with Django, PostgreSQL, and Gunicorn
- RESTful API endpoints for Characters, Films, and Starships
- Integration with SWAPI for official Star Wars data
- Option to create custom/unofficial records
- Pagination and search functionality
- Swagger API documentation
- Unit tests with coverage reports

## Prerequisites

- Docker
- Docker Compose

## Quick Start

1. Clone the repository
2. Run `docker-compose up` to start the application
3. Access the API at `http://localhost:8000`
4. View API documentation at `http://localhost:8000/api/docs/`

## API Endpoints

### Characters
- `GET /api/characters/` - List all characters (paginated)
- `POST /api/characters/` - Create a new character
- `GET /api/characters/{id}/` - Retrieve a specific character
- `PUT /api/characters/{id}/` - Update a character
- `PATCH /api/characters/{id}/` - Partially update a character
- `DELETE /api/characters/{id}/` - Delete a character
- `GET /api/characters/search/?name={name}` - Search characters by name

### Films
- `GET /api/films/` - List all films (paginated)
- `POST /api/films/` - Create a new film
- `GET /api/films/{id}/` - Retrieve a specific film
- `PUT /api/films/{id}/` - Update a film
- `PATCH /api/films/{id}/` - Partially update a film
- `DELETE /api/films/{id}/` - Delete a film
- `GET /api/films/search/?name={name}` - Search films by name

### Starships
- `GET /api/starships/` - List all starships (paginated)
- `POST /api/starships/` - Create a new starship
- `GET /api/starships/{id}/` - Retrieve a specific starship
- `PUT /api/starships/{id}/` - Update a starship
- `PATCH /api/starships/{id}/` - Partially update a starship
- `DELETE /api/starships/{id}/` - Delete a starship
- `GET /api/starships/search/?name={name}` - Search starships by name

## Environment Variables

- `ALLOW_UNOFFICIAL_RECORDS` - Set to True to allow creating custom records with swapi_id=0

## Development

### Running Tests

```bash
docker-compose run web python manage.py test
```

### Generating Coverage Report

```bash
docker-compose run web coverage run --source='.' manage.py test
docker-compose run web coverage report
docker-compose run web coverage html
```

The HTML coverage report will be available in the `htmlcov/` directory.

## Data Population

To populate the database with data from SWAPI:

```bash
docker-compose run web python manage.py populate_swapi_data
```

To limit the number of records (default is 10 per entity type):

```bash
docker-compose run web python manage.py populate_swapi_data --limit 5
```

## Project Structure

```
starwarsrest/
├── starwarsrest/           # Django project settings
│   ├── settings.py         # Project settings
│   ├── urls.py             # URL routing
│   └── wsgi.py             # WSGI entry point
├── starwarsrest/           # Main Django app
│   ├── models.py           # Database models
│   ├── views.py            # API views
│   ├── serializers.py      # Data serializers
│   ├── services.py         # Business logic and SWAPI integration
│   ├── dao.py              # Data Access Objects
│   ├── tests.py            # Unit tests
│   └── management/
│       └── commands/
│           └── populate_swapi_data.py  # Data population script
├── Dockerfile              # Docker configuration for the app
├── docker-compose.yml      # Docker Compose configuration
├── requirements.txt        # Python dependencies
├── entrypoint.sh           # Docker entrypoint script
├── manage.py               # Django management script
├── .coveragerc             # Coverage configuration
└── README.md               # This file
```

## Architecture

This project follows a clean architecture pattern with clear separation of concerns:

1. **Models**: Define the data structure and relationships
2. **DAO (Data Access Objects)**: Handle database operations
3. **Services**: Contain business logic and external API integration
4. **Views**: Handle HTTP requests and responses
5. **Serializers**: Transform data between JSON and model instances

The SWAPI integration service validates records against the official Star Wars API before allowing creation of new records, unless the `ALLOW_UNOFFICIAL_RECORDS` environment variable is set to True.