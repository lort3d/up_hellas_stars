import requests
from django.core.management.base import BaseCommand
from django.db import transaction
from django.core.exceptions import ValidationError
from starwarsrest.models import Character, Film, Starship
from starwarsrest.services import SwapiService

try:
    from celery import shared_task, chain
    from celery.exceptions import CeleryError
    CELERY_AVAILABLE = True
except ImportError:
    CELERY_AVAILABLE = False


if CELERY_AVAILABLE:
    @shared_task
    def populate_films_task():
        """Celery task to populate films from SWAPI"""
        swapi_service = SwapiService()
        print('Populating films...')
        
        try:
            url = f"{SwapiService.BASE_URL}/films/"
            all_films_data = []
            
            # Fetch all pages of films
            while url:
                response = swapi_service._make_request(url)
                
                if not response or 'results' not in response:
                    print('No films data received from SWAPI')
                    break
                
                all_films_data.extend(response['results'])
                
                # Check if there's a next page
                url = response.get('next')
            
            # Filter out films that already exist
            existing_swapi_ids = set(Film.objects.filter(swapi_id__in=[
                int(film_data['url'].split('/')[-2]) for film_data in all_films_data
            ]).values_list('swapi_id', flat=True))
            
            films_to_create = []
            for film_data in all_films_data:
                swapi_id = int(film_data['url'].split('/')[-2])
                if swapi_id not in existing_swapi_ids:
                    film_dict = swapi_service.populate_film_from_swapi(film_data)
                    films_to_create.append(Film(**film_dict))
                else:
                    print(f"Film '{film_data['title']}' already exists")
            
            # Bulk create films
            if films_to_create:
                Film.objects.bulk_create(films_to_create)
                print(f"Created {len(films_to_create)} films")
                
            return f"Successfully populated {len(films_to_create)} films"
        except Exception as e:
            raise Exception(f"Error populating films: {str(e)}")


    @shared_task
    def populate_characters_task():
        """Celery task to populate characters from SWAPI"""
        swapi_service = SwapiService()
        print('Populating characters...')
        
        try:
            url = f"{SwapiService.BASE_URL}/people/"
            all_characters_data = []
            
            # Fetch all pages of characters
            while url:
                response = swapi_service._make_request(url)
                
                if not response or 'results' not in response:
                    print('No characters data received from SWAPI')
                    break
                
                all_characters_data.extend(response['results'])
                
                # Check if there's a next page
                url = response.get('next')
            
            # Filter out characters that already exist
            existing_swapi_ids = set(Character.objects.filter(swapi_id__in=[
                int(character_data['url'].split('/')[-2]) for character_data in all_characters_data
            ]).values_list('swapi_id', flat=True))
            
            characters_to_create = []
            character_films_map = {}  # Map character swapi_id to film swapi_ids
            
            for character_data in all_characters_data:
                swapi_id = int(character_data['url'].split('/')[-2])
                if swapi_id not in existing_swapi_ids:
                    character_dict = swapi_service.populate_character_from_swapi(character_data)
                    characters_to_create.append(Character(**character_dict))
                    
                    # Store film relationships
                    film_ids = []
                    for film_url in character_data.get('films', []):
                        film_id = int(film_url.split('/')[-2])
                        film_ids.append(film_id)
                    character_films_map[swapi_id] = film_ids
                else:
                    print(f"Character '{character_data['name']}' already exists")
            
            # Bulk create characters
            if characters_to_create:
                created_characters = Character.objects.bulk_create(characters_to_create)
                print(f"Created {len(created_characters)} characters")
                
                # Establish character-film relationships
                character_objects = {c.swapi_id: c for c in created_characters}
                film_objects = {f.swapi_id: f for f in Film.objects.all()}
                
                # Create relationships
                for char_swapi_id, film_swapi_ids in character_films_map.items():
                    character = character_objects.get(char_swapi_id)
                    if character:
                        films = [film_objects[film_id] for film_id in film_swapi_ids if film_id in film_objects]
                        if films:
                            character.films.set(films)
                print("Established character-film relationships")
                
            return f"Successfully populated {len(characters_to_create)} characters"
        except Exception as e:
            raise Exception(f"Error populating characters: {str(e)}")


    @shared_task
    def populate_starships_task():
        """Celery task to populate starships from SWAPI"""
        swapi_service = SwapiService()
        print('Populating starships...')
        
        try:
            url = f"{SwapiService.BASE_URL}/starships/"
            all_starships_data = []
            
            # Fetch all pages of starships
            while url:
                response = swapi_service._make_request(url)
                
                if not response or 'results' not in response:
                    print('No starships data received from SWAPI')
                    break
                
                all_starships_data.extend(response['results'])
                
                # Check if there's a next page
                url = response.get('next')
            
            # Filter out starships that already exist
            existing_swapi_ids = set(Starship.objects.filter(swapi_id__in=[
                int(starship_data['url'].split('/')[-2]) for starship_data in all_starships_data
            ]).values_list('swapi_id', flat=True))
            
            starships_to_create = []
            starship_relations_map = {}  # Map starship swapi_id to film and pilot swapi_ids
            
            for starship_data in all_starships_data:
                swapi_id = int(starship_data['url'].split('/')[-2])
                if swapi_id not in existing_swapi_ids:
                    starship_dict = swapi_service.populate_starship_from_swapi(starship_data)
                    starships_to_create.append(Starship(**starship_dict))
                    
                    # Store relationships
                    film_ids = []
                    for film_url in starship_data.get('films', []):
                        film_id = int(film_url.split('/')[-2])
                        film_ids.append(film_id)
                    
                    pilot_ids = []
                    for pilot_url in starship_data.get('pilots', []):
                        pilot_id = int(pilot_url.split('/')[-2])
                        pilot_ids.append(pilot_id)
                        
                    starship_relations_map[swapi_id] = {
                        'films': film_ids,
                        'pilots': pilot_ids
                    }
                else:
                    print(f"Starship '{starship_data['name']}' already exists")
            
            # Bulk create starships
            if starships_to_create:
                created_starships = Starship.objects.bulk_create(starships_to_create)
                print(f"Created {len(created_starships)} starships")
                
                # Establish starship relationships
                starship_objects = {s.swapi_id: s for s in created_starships}
                film_objects = {f.swapi_id: f for f in Film.objects.all()}
                character_objects = {c.swapi_id: c for c in Character.objects.all()}
                
                # Create relationships
                for starship_swapi_id, relations in starship_relations_map.items():
                    starship = starship_objects.get(starship_swapi_id)
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
                
            return f"Successfully populated {len(starships_to_create)} starships"
        except Exception as e:
            raise Exception(f"Error populating starships: {str(e)}")


class Command(BaseCommand):
    help = 'Populate the database with data from SWAPI'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--async',
            action='store_true',
            help='Run population tasks asynchronously with Celery'
        )
    
    def handle(self, *args, **options):
        use_async = options.get('async', False)
        
        if use_async and not CELERY_AVAILABLE:
            self.stdout.write(
                self.style.ERROR("Celery is not available. Please install it to use async mode.")
            )
            return
        
        if use_async:
            # Run tasks asynchronously with Celery
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
        else:
            # Run synchronously (original behavior)
            self.stdout.write(
                self.style.SUCCESS('Starting to populate database with SWAPI data')
            )
            
            swapi_service = SwapiService()
            
            # Populate films
            try:
                result = populate_films_task() if CELERY_AVAILABLE else self._populate_films_sync(swapi_service)
                self.stdout.write(self.style.SUCCESS(result))
            except Exception as e:
                self.stdout.write(self.style.ERROR(str(e)))
                return
            
            # Populate characters
            try:
                result = populate_characters_task() if CELERY_AVAILABLE else self._populate_characters_sync(swapi_service)
                self.stdout.write(self.style.SUCCESS(result))
            except Exception as e:
                self.stdout.write(self.style.ERROR(str(e)))
                return
            
            # Populate starships
            try:
                result = populate_starships_task() if CELERY_AVAILABLE else self._populate_starships_sync(swapi_service)
                self.stdout.write(self.style.SUCCESS(result))
            except Exception as e:
                self.stdout.write(self.style.ERROR(str(e)))
                return
            
            self.stdout.write(
                self.style.SUCCESS('Successfully populated database with SWAPI data')
            )
    
    def _populate_films_sync(self, swapi_service):
        """Synchronous version of film population"""
        print('Populating films...')
        
        try:
            url = f"{SwapiService.BASE_URL}/films/"
            all_films_data = []
            
            # Fetch all pages of films
            while url:
                response = swapi_service._make_request(url)
                
                if not response or 'results' not in response:
                    print('No films data received from SWAPI')
                    break
                
                all_films_data.extend(response['results'])
                
                # Check if there's a next page
                url = response.get('next')
            
            # Filter out films that already exist
            existing_swapi_ids = set(Film.objects.filter(swapi_id__in=[
                int(film_data['url'].split('/')[-2]) for film_data in all_films_data
            ]).values_list('swapi_id', flat=True))
            
            films_to_create = []
            for film_data in all_films_data:
                swapi_id = int(film_data['url'].split('/')[-2])
                if swapi_id not in existing_swapi_ids:
                    film_dict = swapi_service.populate_film_from_swapi(film_data)
                    films_to_create.append(Film(**film_dict))
                else:
                    print(f"Film '{film_data['title']}' already exists")
            
            # Bulk create films
            if films_to_create:
                Film.objects.bulk_create(films_to_create)
                print(f"Created {len(films_to_create)} films")
                
            return f"Successfully populated {len(films_to_create)} films"
        except Exception as e:
            raise Exception(f"Error populating films: {str(e)}")
    
    def _populate_characters_sync(self, swapi_service):
        """Synchronous version of character population"""
        print('Populating characters...')
        
        try:
            url = f"{SwapiService.BASE_URL}/people/"
            all_characters_data = []
            
            # Fetch all pages of characters
            while url:
                response = swapi_service._make_request(url)
                
                if not response or 'results' not in response:
                    print('No characters data received from SWAPI')
                    break
                
                all_characters_data.extend(response['results'])
                
                # Check if there's a next page
                url = response.get('next')
            
            # Filter out characters that already exist
            existing_swapi_ids = set(Character.objects.filter(swapi_id__in=[
                int(character_data['url'].split('/')[-2]) for character_data in all_characters_data
            ]).values_list('swapi_id', flat=True))
            
            characters_to_create = []
            character_films_map = {}  # Map character swapi_id to film swapi_ids
            
            for character_data in all_characters_data:
                swapi_id = int(character_data['url'].split('/')[-2])
                if swapi_id not in existing_swapi_ids:
                    character_dict = swapi_service.populate_character_from_swapi(character_data)
                    characters_to_create.append(Character(**character_dict))
                    
                    # Store film relationships
                    film_ids = []
                    for film_url in character_data.get('films', []):
                        film_id = int(film_url.split('/')[-2])
                        film_ids.append(film_id)
                    character_films_map[swapi_id] = film_ids
                else:
                    print(f"Character '{character_data['name']}' already exists")
            
            # Bulk create characters
            if characters_to_create:
                created_characters = Character.objects.bulk_create(characters_to_create)
                print(f"Created {len(created_characters)} characters")
                
                # Establish character-film relationships
                character_objects = {c.swapi_id: c for c in created_characters}
                film_objects = {f.swapi_id: f for f in Film.objects.all()}
                
                # Create relationships
                for char_swapi_id, film_swapi_ids in character_films_map.items():
                    character = character_objects.get(char_swapi_id)
                    if character:
                        films = [film_objects[film_id] for film_id in film_swapi_ids if film_id in film_objects]
                        if films:
                            character.films.set(films)
                print("Established character-film relationships")
                
            return f"Successfully populated {len(characters_to_create)} characters"
        except Exception as e:
            raise Exception(f"Error populating characters: {str(e)}")
    
    def _populate_starships_sync(self, swapi_service):
        """Synchronous version of starship population"""
        print('Populating starships...')
        
        try:
            url = f"{SwapiService.BASE_URL}/starships/"
            all_starships_data = []
            
            # Fetch all pages of starships
            while url:
                response = swapi_service._make_request(url)
                
                if not response or 'results' not in response:
                    print('No starships data received from SWAPI')
                    break
                
                all_starships_data.extend(response['results'])
                
                # Check if there's a next page
                url = response.get('next')
            
            # Filter out starships that already exist
            existing_swapi_ids = set(Starship.objects.filter(swapi_id__in=[
                int(starship_data['url'].split('/')[-2]) for starship_data in all_starships_data
            ]).values_list('swapi_id', flat=True))
            
            starships_to_create = []
            starship_relations_map = {}  # Map starship swapi_id to film and pilot swapi_ids
            
            for starship_data in all_starships_data:
                swapi_id = int(starship_data['url'].split('/')[-2])
                if swapi_id not in existing_swapi_ids:
                    starship_dict = swapi_service.populate_starship_from_swapi(starship_data)
                    starships_to_create.append(Starship(**starship_dict))
                    
                    # Store relationships
                    film_ids = []
                    for film_url in starship_data.get('films', []):
                        film_id = int(film_url.split('/')[-2])
                        film_ids.append(film_id)
                    
                    pilot_ids = []
                    for pilot_url in starship_data.get('pilots', []):
                        pilot_id = int(pilot_url.split('/')[-2])
                        pilot_ids.append(pilot_id)
                        
                    starship_relations_map[swapi_id] = {
                        'films': film_ids,
                        'pilots': pilot_ids
                    }
                else:
                    print(f"Starship '{starship_data['name']}' already exists")
            
            # Bulk create starships
            if starships_to_create:
                created_starships = Starship.objects.bulk_create(starships_to_create)
                print(f"Created {len(created_starships)} starships")
                
                # Establish starship relationships
                starship_objects = {s.swapi_id: s for s in created_starships}
                film_objects = {f.swapi_id: f for f in Film.objects.all()}
                character_objects = {c.swapi_id: c for c in Character.objects.all()}
                
                # Create relationships
                for starship_swapi_id, relations in starship_relations_map.items():
                    starship = starship_objects.get(starship_swapi_id)
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
                
            return f"Successfully populated {len(starships_to_create)} starships"
        except Exception as e:
            raise Exception(f"Error populating starships: {str(e)}")