import requests
from django.core.management.base import BaseCommand
from django.db import transaction
from django.core.exceptions import ValidationError
from starwarsrest.models import Character, Film, Starship
from starwarsrest.services import SwapiService

from celery import shared_task, chain
from celery.exceptions import CeleryError


def _populate_entities(swapi_service, entity_type, model_class, populate_method):
    """Common function to populate entities from SWAPI
    
    Args:
        swapi_service: Instance of SwapiService
        entity_type: Type of entity ('films', 'people', 'starships')
        model_class: Django model class (Film, Character, Starship)
        populate_method: Method to convert SWAPI data to model dict
    """
    print(f'Populating {entity_type}...')
    
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
        existing_swapi_ids = set(model_class.objects.filter(swapi_id__in=[
            int(entity_data['url'].split('/')[-2]) for entity_data in all_entities_data
        ]).values_list('swapi_id', flat=True))
        
        entities_to_create = []
        relations_map = {}  # Map entity swapi_id to related swapi_ids
        
        for entity_data in all_entities_data:
            swapi_id = int(entity_data['url'].split('/')[-2])
            if swapi_id not in existing_swapi_ids:
                entity_dict = populate_method(entity_data)
                entities_to_create.append(model_class(**entity_dict))
                
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
        
        # Bulk create entities
        if entities_to_create:
            created_entities = model_class.objects.bulk_create(entities_to_create)
            print(f"Created {len(created_entities)} {entity_type}")
            
            # Establish relationships if needed
            if relations_map:
                entity_objects = {e.swapi_id: e for e in created_entities}
                
                if entity_type == 'people':  # Characters
                    film_objects = {f.swapi_id: f for f in Film.objects.all()}
                    
                    # Create character-film relationships
                    for char_swapi_id, film_swapi_ids in relations_map.items():
                        character = entity_objects.get(char_swapi_id)
                        if character:
                            films = [film_objects[film_id] for film_id in film_swapi_ids if film_id in film_objects]
                            if films:
                                character.films.set(films)
                    print("Established character-film relationships")
                
                elif entity_type == 'starships':
                    film_objects = {f.swapi_id: f for f in Film.objects.all()}
                    character_objects = {c.swapi_id: c for c in Character.objects.all()}
                    
                    # Create starship relationships
                    for starship_swapi_id, relations in relations_map.items():
                        starship = entity_objects.get(starship_swapi_id)
                        if starship:
                            # Films relationship
                            film_ids = relations['films']
                            films = [film_objects[film_id] for film_id in film_ids if film_id in film_objects]
                            if films:
                                starship.films.set(films)
                            
                            # Pilots relationship
                            pilot_ids = relations['pilots']
                            pilots = [character_objects[pilot_id] for pilot_id in pilot_ids if pilot_id in character_objects]
                            if pilots:
                                starship.pilots.set(pilots)
                    
                    print("Established starship relationships")
            
            entity_count = len(created_entities)
        else:
            entity_count = 0
            
        return f"Successfully populated {entity_count} {entity_type}"
    except Exception as e:
        raise Exception(f"Error populating {entity_type}: {str(e)}")


@shared_task
def populate_films_task(*args, **kwargs):
    """Celery task to populate films from SWAPI"""
    swapi_service = SwapiService()
    return _populate_entities(
        swapi_service,
        'films',
        Film,
        swapi_service.populate_film_from_swapi
    )


@shared_task
def populate_characters_task(*args, **kwargs):
    """Celery task to populate characters from SWAPI"""
    swapi_service = SwapiService()
    return _populate_entities(
        swapi_service,
        'people',
        Character,
        swapi_service.populate_character_from_swapi
    )


@shared_task
def populate_starships_task(*args, **kwargs):
    """Celery task to populate starships from SWAPI"""
    swapi_service = SwapiService()
    return _populate_entities(
        swapi_service,
        'starships',
        Starship,
        swapi_service.populate_starship_from_swapi
    )


class Command(BaseCommand):
    help = 'Populate the database with data from SWAPI'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--async',
            action='store_true',
            help='Run population tasks asynchronously with Celery',
            default=True  # Make async the default behavior
        )
    
    def handle(self, *args, **options):
        # Always run asynchronously with Celery
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