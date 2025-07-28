# This file is needed to make Celery discover tasks in this app
from .management.commands.populate_swapi_data import populate_films_task, populate_characters_task, populate_starships_task