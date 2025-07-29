from io import StringIO
from unittest.mock import patch, Mock
from django.test import TestCase
from django.core.management import call_command
from starwarsrest.models import Character, Film, Starship
from starwarsrest.management.commands.populate_swapi_data import (
    populate_films_task, 
    populate_characters_task, 
    populate_starships_task,
    _populate_entities
)


class PopulateSwapiDataTest(TestCase):
    """Test cases for the populate_swapi_data management command"""

    def setUp(self):
        """Set up test data"""
        # Sample SWAPI data for mocking
        self.sample_films_data = {
            "count": 2,
            "results": [
                {
                    "title": "A New Hope",
                    "episode_id": 4,
                    "opening_crawl": "It is a period of civil war...",
                    "director": "George Lucas",
                    "producer": "Gary Kurtz",
                    "release_date": "1977-05-25",
                    "url": "https://swapi.dev/api/films/1/"
                },
                {
                    "title": "The Empire Strikes Back",
                    "episode_id": 5,
                    "opening_crawl": "It is a dark time for the Rebellion...",
                    "director": "Irvin Kershner",
                    "producer": "Gary Kurtz",
                    "release_date": "1980-05-17",
                    "url": "https://swapi.dev/api/films/2/"
                }
            ]
        }

        self.sample_characters_data = {
            "count": 2,
            "results": [
                {
                    "name": "Luke Skywalker",
                    "birth_year": "19BBY",
                    "eye_color": "blue",
                    "gender": "male",
                    "hair_color": "blond",
                    "height": "172",
                    "mass": "77",
                    "skin_color": "fair",
                    "homeworld": "https://swapi.dev/api/planets/1/",
                    "url": "https://swapi.dev/api/people/1/"
                },
                {
                    "name": "C-3PO",
                    "birth_year": "112BBY",
                    "eye_color": "yellow",
                    "gender": "n/a",
                    "hair_color": "n/a",
                    "height": "167",
                    "mass": "75",
                    "skin_color": "gold",
                    "homeworld": "https://swapi.dev/api/planets/1/",
                    "url": "https://swapi.dev/api/people/2/"
                }
            ]
        }

        self.sample_starships_data = {
            "count": 2,
            "results": [
                {
                    "name": "CR90 corvette",
                    "model": "CR90 corvette",
                    "starship_class": "corvette",
                    "manufacturer": "Corellian Engineering Corporation",
                    "cost_in_credits": "3500000",
                    "length": "150",
                    "crew": "165",
                    "passengers": "600",
                    "max_atmosphering_speed": "950",
                    "hyperdrive_rating": "2.0",
                    "MGLT": "60",
                    "cargo_capacity": "3000000",
                    "consumables": "1 year",
                    "url": "https://swapi.dev/api/starships/2/"
                },
                {
                    "name": "Star Destroyer",
                    "model": "Imperial I-class Star Destroyer",
                    "starship_class": "Star Destroyer",
                    "manufacturer": "Kuat Drive Yards",
                    "cost_in_credits": "150000000",
                    "length": "1600",
                    "crew": "47060",
                    "passengers": "0",
                    "max_atmosphering_speed": "975",
                    "hyperdrive_rating": "2.0",
                    "MGLT": "60",
                    "cargo_capacity": "36000000",
                    "consumables": "2 years",
                    "url": "https://swapi.dev/api/starships/3/"
                }
            ]
        }

    @patch('starwarsrest.services.SwapiService._make_request')
    def test_populate_films_task(self, mock_make_request):
        """Test the populate_films_task Celery task"""
        # Configure mock to return film data
        mock_make_request.return_value = self.sample_films_data

        # Run the task directly
        result = populate_films_task()
        
        # Check that the task was successful
        self.assertIn('Successfully populated', result)
        
        # Check that records were created in the database
        self.assertEqual(Film.objects.count(), 2)
        
        # Check specific records exist
        film = Film.objects.get(name='A New Hope')
        self.assertEqual(film.episode_id, 4)
        self.assertEqual(film.director, 'George Lucas')

    @patch('starwarsrest.services.SwapiService._make_request')
    def test_populate_characters_task(self, mock_make_request):
        """Test the populate_characters_task Celery task"""
        # First populate films as characters reference films
        with patch('starwarsrest.services.SwapiService._make_request') as mock_films_request:
            mock_films_request.return_value = self.sample_films_data
            populate_films_task()
            
        # Configure mock to return character data
        mock_make_request.return_value = self.sample_characters_data

        # Run the task directly
        result = populate_characters_task()
        
        # Check that the task was successful
        self.assertIn('Successfully populated', result)
        
        # Check that records were created in the database
        self.assertEqual(Character.objects.count(), 2)
        
        # Check specific records exist
        character = Character.objects.get(name='Luke Skywalker')
        self.assertEqual(character.eye_color, 'blue')
        self.assertEqual(character.gender, 'male')

    @patch('starwarsrest.services.SwapiService._make_request')
    def test_populate_starships_task(self, mock_make_request):
        """Test the populate_starships_task Celery task"""
        # First populate films and characters as starships reference them
        with patch('starwarsrest.services.SwapiService._make_request') as mock_films_request:
            mock_films_request.return_value = self.sample_films_data
            populate_films_task()
            
        with patch('starwarsrest.services.SwapiService._make_request') as mock_characters_request:
            mock_characters_request.return_value = self.sample_characters_data
            populate_characters_task()
            
        # Configure mock to return starship data
        mock_make_request.return_value = self.sample_starships_data

        # Run the task directly
        result = populate_starships_task()
        
        # Check that the task was successful
        self.assertIn('Successfully populated', result)
        
        # Check that records were created in the database
        self.assertEqual(Starship.objects.count(), 2)
        
        # Check specific records exist
        starship = Starship.objects.get(name='CR90 corvette')
        self.assertEqual(starship.starship_class, 'corvette')
        self.assertEqual(starship.manufacturer, 'Corellian Engineering Corporation')

    @patch('starwarsrest.services.SwapiService._make_request')
    def test_populate_entities_with_existing_records(self, mock_make_request):
        """Test that _populate_entities handles existing records correctly"""
        # Configure mock to return data
        mock_make_request.return_value = self.sample_films_data

        # Create a film that already exists
        Film.objects.create(
            name='A New Hope',
            swapi_id=1,
            episode_id=4,
            director='George Lucas',
            producer='Gary Kurtz',
            release_date='1977-05-25'
        )
        
        # Run the function directly
        result = _populate_entities(
            'films',
            Film,
        )
        
        # Check that only one film was created (the other already existed)
        self.assertEqual(Film.objects.count(), 2)
        
        # Check that the result mentions the existing record
        self.assertIn('Successfully populated 1 films', result)

    @patch('starwarsrest.services.SwapiService._make_request')
    def test_populate_entities_with_no_data(self, mock_make_request):
        """Test that _populate_entities handles empty data responses correctly"""
        # Configure mock to return empty data
        mock_make_request.return_value = None
        
        # Run the function directly
        result = _populate_entities(
            'films',
            Film,
        )
        
        # Check that no records were created
        self.assertEqual(Film.objects.count(), 0)
        
        # Check that the result mentions no data
        self.assertIn('Successfully populated 0 films', result)

    @patch('starwarsrest.services.SwapiService._make_request')
    def test_populate_entities_with_request_exception(self, mock_make_request):
        """Test that _populate_entities handles request exceptions correctly"""
        # Configure mock to raise an exception
        mock_make_request.side_effect = Exception('Network error')
        
        # Run the function directly
        with self.assertRaises(Exception) as context:
            _populate_entities(
                'films',
                Film,
            )
        
        # Check that the exception message is correct
        self.assertIn('Error populating films', str(context.exception))
        
        # Check that no records were created
        self.assertEqual(Film.objects.count(), 0)