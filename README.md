# Star Wars REST API

A Django REST API for Star Wars data with integration to SWAPI (Star Wars API).

## Features

- RESTful API endpoints for Characters, Films, and Starships
- Data validation against SWAPI with option to allow custom records
- Search functionality for all entity types
- Pagination for large result sets
- Swagger API documentation
- Dockerized for easy deployment

## Requirements

- Docker
- Docker Compose

## Getting Started

1. Clone the repository:
   ```
   git clone <repository-url>
   cd starwars-rest-api
   ```

2. Start the application:
   ```
   docker-compose up --build
   ```

3. The API will be available at `http://localhost:8000`

4. API documentation is available at `http://localhost:8000/api/docs/`

## API Endpoints

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

## Environment Variables

- `DEBUG` - Django debug mode (default: 1)
- `SECRET_KEY` - Django secret key
- `DB_HOST` - Database host (default: db)
- `DB_NAME` - Database name (default: starwarsdb)
- `DB_USER` - Database user (default: starwarsuser)
- `DB_PASSWORD` - Database password (default: starwarspass)
- `DB_PORT` - Database port (default: 5432)
- `ALLOW_UNOFFICIAL_RECORDS` - Allow creation of custom records not found in SWAPI (default: True)

## Populate with SWAPI Data

To populate the database with data from SWAPI:
```
docker-compose exec web python manage.py populate_swapi_data --limit 10
```

## Running Tests

To run the test suite:
```
docker-compose exec web python manage.py test
```

## Project Structure

- `starwarsrest/` - Main Django application
  - `models.py` - Data models for Characters, Films, and Starships
  - `views.py` - API views and viewsets
  - `serializers.py` - Serialization logic
  - `dao.py` - Data Access Object patterns
  - `services.py` - Business logic and SWAPI integration
  - `management/commands/populate_swapi_data.py` - Management command to populate data from SWAPI

## Technologies Used

- Python 3.12
- Django 5.0
- Django REST Framework
- PostgreSQL
- Docker
- Gunicorn
- SWAPI (Star Wars API)