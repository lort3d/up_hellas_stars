import requests
from django.core.management.base import BaseCommand
from django.db import transaction
from django.core.exceptions import ValidationError
from starwarsrest.models import Character, Film, Starship
from starwarsrest.services import SwapiService


class Command(BaseCommand):
    help = 'Populate the database with data from SWAPI'
    
    def add_arguments(self, parser):
        pass
    
    def handle(self, *args, **options):
        swapi_service = SwapiService()
        
        self.stdout.write(
            self.style.SUCCESS('Starting to populate database with SWAPI data')
        )
        
        # Populate films
        self.populate_films(swapi_service)
        
        # Populate characters
        self.populate_characters(swapi_service)
        
        # Populate starships
        self.populate_starships(swapi_service)
        
        self.stdout.write(
            self.style.SUCCESS('Successfully populated database with SWAPI data')
        )
    
    def populate_films(self, swapi_service):
        """Populate films from SWAPI"""
        self.stdout.write('Populating films...')
        
        try:
            url = f"{SwapiService.BASE_URL}/films/"
            all_films_data = []
            
            # Fetch all pages of films
            while url:
                response = swapi_service._make_request(url)
                
                if not response or 'results' not in response:
                    self.stdout.write(
                        self.style.WARNING('No films data received from SWAPI')
                    )
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
                    self.stdout.write(
                        self.style.WARNING(f"Film '{film_data['title']}' already exists")
                    )
            
            # Bulk create films
            if films_to_create:
                Film.objects.bulk_create(films_to_create)
                self.stdout.write(
                    self.style.SUCCESS(f"Created {len(films_to_create)} films")
                )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"Error populating films: {str(e)}")
            )
    
    def populate_characters(self, swapi_service):
        """Populate characters from SWAPI"""
        self.stdout.write('Populating characters...')
        
        try:
            url = f"{SwapiService.BASE_URL}/people/"
            all_characters_data = []
            
            # Fetch all pages of characters
            while url:
                response = swapi_service._make_request(url)
                
                if not response or 'results' not in response:
                    self.stdout.write(
                        self.style.WARNING('No characters data received from SWAPI')
                    )
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
                    self.stdout.write(
                        self.style.WARNING(f"Character '{character_data['name']}' already exists")
                    )
            
            # Bulk create characters
            if characters_to_create:
                created_characters = Character.objects.bulk_create(characters_to_create)
                self.stdout.write(
                    self.style.SUCCESS(f"Created {len(created_characters)} characters")
                )
                
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
                self.stdout.write(
                    self.style.SUCCESS("Established character-film relationships")
                )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"Error populating characters: {str(e)}")
            )
    
    def populate_starships(self, swapi_service):
        """Populate starships from SWAPI"""
        self.stdout.write('Populating starships...')
        
        try:
            url = f"{SwapiService.BASE_URL}/starships/"
            all_starships_data = []
            
            # Fetch all pages of starships
            while url:
                response = swapi_service._make_request(url)
                
                if not response or 'results' not in response:
                    self.stdout.write(
                        self.style.WARNING('No starships data received from SWAPI')
                    )
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
                    self.stdout.write(
                        self.style.WARNING(f"Starship '{starship_data['name']}' already exists")
                    )
            
            # Bulk create starships
            if starships_to_create:
                created_starships = Starship.objects.bulk_create(starships_to_create)
                self.stdout.write(
                    self.style.SUCCESS(f"Created {len(created_starships)} starships")
                )
                
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
                
                self.stdout.write(
                    self.style.SUCCESS("Established starship relationships")
                )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"Error populating starships: {str(e)}")
            )