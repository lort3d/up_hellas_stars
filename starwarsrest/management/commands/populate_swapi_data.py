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
            
            with transaction.atomic():
                for film_data in all_films_data:
                    # Check if film already exists
                    swapi_id = int(film_data['url'].split('/')[-2])
                    if Film.objects.filter(swapi_id=swapi_id).exists():
                        self.stdout.write(
                            self.style.WARNING(f"Film '{film_data['title']}' already exists")
                        )
                        continue
                    
                    # Create film
                    film_dict = swapi_service.populate_film_from_swapi(film_data)
                    Film.objects.create(**film_dict)
                    self.stdout.write(
                        self.style.SUCCESS(f"Created film: {film_data['title']}")
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
            
            with transaction.atomic():
                for character_data in all_characters_data:
                    # Check if character already exists
                    swapi_id = int(character_data['url'].split('/')[-2])
                    if Character.objects.filter(swapi_id=swapi_id).exists():
                        self.stdout.write(
                            self.style.WARNING(f"Character '{character_data['name']}' already exists")
                        )
                        continue
                    
                    # Create character
                    character_dict = swapi_service.populate_character_from_swapi(character_data)
                    Character.objects.create(**character_dict)
                    self.stdout.write(
                        self.style.SUCCESS(f"Created character: {character_data['name']}")
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
            
            with transaction.atomic():
                for starship_data in all_starships_data:
                    # Check if starship already exists
                    swapi_id = int(starship_data['url'].split('/')[-2])
                    if Starship.objects.filter(swapi_id=swapi_id).exists():
                        self.stdout.write(
                            self.style.WARNING(f"Starship '{starship_data['name']}' already exists")
                        )
                        continue
                    
                    # Create starship
                    starship_dict = swapi_service.populate_starship_from_swapi(starship_data)
                    Starship.objects.create(**starship_dict)
                    self.stdout.write(
                        self.style.SUCCESS(f"Created starship: {starship_data['name']}")
                    )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"Error populating starships: {str(e)}")
            )