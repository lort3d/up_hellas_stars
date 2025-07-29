import requests
from django.core.management.base import BaseCommand
from django.core.exceptions import ValidationError
from starwarsrest.models import Character, Film, Starship
from starwarsrest.services import SwapiService
from starwarsrest.dao import CharacterDAO, FilmDAO, StarshipDAO

from celery import shared_task, chain
from celery.exceptions import CeleryError


def _populate_entities(entity_type):
    """Common function to populate entities from SWAPI using DAO objects
    
    Args:
        entity_type: Type of entity ('films', 'people', 'starships')
    """
    print(f'Populating {entity_type}...')
    
    swapi_service = SwapiService()
    if entity_type == 'films':
        populate_method = swapi_service.populate_film_from_swapi
    elif entity_type == 'people':
        populate_method = swapi_service.populate_character_from_swapi
    elif entity_type == 'starships':
        populate_method = swapi_service.populate_starship_from_swapi
    
    try:
        url = f"{SwapiService.BASE_URL}/{entity_type}/"
        all_entities_data = []
        
        # Fetch all pages of entities
        while url:
            response = swapi_service._make_request(url)
            
            if not response or 'results' not in response:
                print(f'No {entity_type} data received from SWAPI')
                break
            
            all_entities_data.extend(response['results'])
            
            # Check if there's a next page
            url = response.get('next')
        
        # Filter out entities that already exist
        entity_swapi_ids = [int(entity_data['url'].split('/')[-2]) for entity_data in all_entities_data]
        
        # Get existing swapi_ids from the database using DAOs
        if entity_type == 'films':
            existing_objects = FilmDAO.list_films()
        elif entity_type == 'people':
            existing_objects = CharacterDAO.list_characters()
        elif entity_type == 'starships':
            existing_objects = StarshipDAO.list_starships()
            
        existing_swapi_ids = set(obj.swapi_id for obj in existing_objects if obj.swapi_id in entity_swapi_ids)
        
        entities_to_create = []
        relations_map = {}  # Map entity swapi_id to related swapi_ids
        
        for entity_data in all_entities_data:
            swapi_id = int(entity_data['url'].split('/')[-2])
            if swapi_id not in existing_swapi_ids:
                entity_dict = populate_method(entity_data)
                entities_to_create.append(entity_dict)
                
                # Store relationships based on entity type
                if entity_type == 'people':  # Characters
                    film_ids = []
                    for film_url in entity_data.get('films', []):
                        film_id = int(film_url.split('/')[-2])
                        film_ids.append(film_id)
                    relations_map[swapi_id] = film_ids
                elif entity_type == 'starships':
                    film_ids = []
                    for film_url in entity_data.get('films', []):
                        film_id = int(film_url.split('/')[-2])
                        film_ids.append(film_id)
                    
                    pilot_ids = []
                    for pilot_url in entity_data.get('pilots', []):
                        pilot_id = int(pilot_url.split('/')[-2])
                        pilot_ids.append(pilot_id)
                        
                    relations_map[swapi_id] = {
                        'films': film_ids,
                        'pilots': pilot_ids
                    }
            else:
                name = entity_data.get('title') or entity_data.get('name', 'Unknown')
                print(f"{entity_type[:-1].capitalize()} '{name}' already exists")
        
        # Bulk create entities using DAO
        created_entities = []
        for entity_dict in entities_to_create:
            try:
                # For characters and starships, we need to handle relationships separately
                # Remove relationship fields for now - we'll set them later
                entity = None
                if entity_type == 'films':
                    entity = FilmDAO.create_film(entity_dict)
                elif entity_type == 'people':
                    entity = CharacterDAO.create_character(entity_dict)
                elif entity_type == 'starships':
                    entity = StarshipDAO.create_starship(entity_dict)
                created_entities.append(entity)
            except ValidationError as e:
                print(f"Validation error creating entity: {str(e)}")
            except Exception as e:
                print(f"Error creating entity: {str(e)}")
            
        print(f"Created {len(created_entities)} {entity_type}")
        
        # Establish relationships if needed using DAO methods
        if relations_map and created_entities:
            entity_objects = {e.swapi_id: e for e in created_entities}
            
            if entity_type == 'people':  # Characters
                film_objects = {f.swapi_id: f for f in FilmDAO.list_films()}
                
                # Create character-film relationships using DAO
                for char_swapi_id, film_swapi_ids in relations_map.items():
                    character = entity_objects.get(char_swapi_id)
                    if character:
                        films = [film_objects[film_id] for film_id in film_swapi_ids if film_id in film_objects]
                        if films:
                            # Use DAO method to set character films
                            CharacterDAO.set_character_films(character.id, films)
                print("Established character-film relationships")
            
            elif entity_type == 'starships':
                film_objects = {f.swapi_id: f for f in FilmDAO.list_films()}
                character_objects = {c.swapi_id: c for c in CharacterDAO.list_characters()}
                
                # Create starship relationships using DAO
                for starship_swapi_id, relations in relations_map.items():
                    starship = entity_objects.get(starship_swapi_id)
                    if starship:
                        # Films relationship
                        film_ids = relations.get('films', [])
                        films = [film_objects[film_id] for film_id in film_ids if film_id in film_objects]
                        
                        # Pilots relationship
                        pilot_ids = relations.get('pilots', [])
                        pilots = [character_objects[pilot_id] for pilot_id in pilot_ids if pilot_id in character_objects]
                        
                        # Use DAO methods to set starship relationships
                        if films:
                            StarshipDAO.set_starship_films(starship.id, films)
                        if pilots:
                            StarshipDAO.set_starship_pilots(starship.id, pilots)
                
                print("Established starship relationships")
        
        entity_count = len(created_entities)
        return f"Successfully populated {entity_count} {entity_type}"
    except Exception as e:
        raise Exception(f"Error populating {entity_type}: {str(e)}")


@shared_task
def populate_films_task(*args, **kwargs):
    """Celery task to populate films from SWAPI"""
    return _populate_entities(
        'films',
    )


@shared_task
def populate_characters_task(*args, **kwargs):
    """Celery task to populate characters from SWAPI"""
    return _populate_entities(
        'people',
    )


@shared_task
def populate_starships_task(*args, **kwargs):
    """Celery task to populate starships from SWAPI"""
    return _populate_entities(
        'starships',
    )


class Command(BaseCommand):
    help = 'Populate the database with data from SWAPI'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            help='Forces the population update',
            default=False
        )
    
    def handle(self, *args, **options):
        # Check if any films exist using the DAO
        films_exist = FilmDAO.list_films().exists()
        
        if not films_exist and options['force']:
            self.stdout.write(
                self.style.SUCCESS('Starting asynchronous population of SWAPI data with Celery')
            )
            
            try:
                # Chain tasks to run sequentially
                task_chain = chain(
                    populate_films_task.s(),
                    populate_characters_task.s(),
                    populate_starships_task.s()
                )
                result = task_chain.apply_async()
                
                self.stdout.write(
                    self.style.SUCCESS(f'Created task chain with ID: {result.id}')
                )
            except CeleryError as e:
                self.stdout.write(
                    self.style.ERROR(f"Celery error: {str(e)}")
                )
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f"Error creating Celery tasks: {str(e)}")
                )