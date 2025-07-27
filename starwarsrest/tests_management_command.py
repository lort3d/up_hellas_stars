from io import StringIO
from unittest.mock import patch, Mock
from django.test import TestCase
from django.core.management import call_command
from starwarsrest.models import Character, Film, Starship


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
    def test_populate_swapi_data_command(self, mock_make_request):
        """Test the populate_swapi_data management command"""
        # Configure mock to return different data based on the URL
        def side_effect(url):
            if '/films/' in url:
                return self.sample_films_data
            elif '/people/' in url:
                return self.sample_characters_data
            elif '/starships/' in url:
                return self.sample_starships_data
            return None

        mock_make_request.side_effect = side_effect

        # Capture command output
        out = StringIO()
        
        # Run the management command
        call_command('populate_swapi_data', limit=2, stdout=out)
        
        # Check that the command output contains success messages
        output = out.getvalue()
        self.assertIn('Starting to populate database', output)
        self.assertIn('Successfully populated database', output)
        
        # Check that records were created in the database
        self.assertEqual(Film.objects.count(), 2)
        self.assertEqual(Character.objects.count(), 2)
        self.assertEqual(Starship.objects.count(), 2)
        
        # Check specific records exist
        film = Film.objects.get(name='A New Hope')
        self.assertEqual(film.episode_id, 4)
        self.assertEqual(film.director, 'George Lucas')
        
        character = Character.objects.get(name='Luke Skywalker')
        self.assertEqual(character.eye_color, 'blue')
        self.assertEqual(character.gender, 'male')
        
        starship = Starship.objects.get(name='CR90 corvette')
        self.assertEqual(starship.starship_class, 'corvette')
        self.assertEqual(starship.manufacturer, 'Corellian Engineering Corporation')

    @patch('starwarsrest.services.SwapiService._make_request')
    def test_populate_swapi_data_with_existing_records(self, mock_make_request):
        """Test the command handles existing records correctly"""
        # Configure mock to return data
        def side_effect(url):
            if '/films/' in url:
                return self.sample_films_data
            elif '/people/' in url:
                return self.sample_characters_data
            elif '/starships/' in url:
                return self.sample_starships_data
            return None

        mock_make_request.side_effect = side_effect

        # Create a film that already exists
        Film.objects.create(
            name='A New Hope',
            swapi_id=1,
            episode_id=4,
            director='George Lucas',
            producer='Gary Kurtz',
            release_date='1977-05-25'
        )
        
        # Capture command output
        out = StringIO()
        
        # Run the management command
        call_command('populate_swapi_data', limit=2, stdout=out)
        
        # Check that only one film was created (the other already existed)
        self.assertEqual(Film.objects.count(), 2)
        self.assertEqual(Character.objects.count(), 2)
        self.assertEqual(Starship.objects.count(), 2)
        
        # Check that the output contains the warning about existing film
        output = out.getvalue()
        self.assertIn("Film 'A New Hope' already exists", output)

    @patch('starwarsrest.services.SwapiService._make_request')
    def test_populate_swapi_data_with_no_data(self, mock_make_request):
        """Test the command handles empty data responses correctly"""
        # Configure mock to return empty data
        mock_make_request.return_value = None
        
        # Capture command output
        out = StringIO()
        
        # Run the management command
        call_command('populate_swapi_data', limit=5, stdout=out)
        
        # Check that the command output contains warning messages
        output = out.getvalue()
        self.assertIn('No films data received from SWAPI', output)
        self.assertIn('No characters data received from SWAPI', output)
        self.assertIn('No starships data received from SWAPI', output)
        
        # Check that no records were created
        self.assertEqual(Film.objects.count(), 0)
        self.assertEqual(Character.objects.count(), 0)
        self.assertEqual(Starship.objects.count(), 0)

    @patch('starwarsrest.services.SwapiService._make_request')
    def test_populate_swapi_data_with_request_exception(self, mock_make_request):
        """Test the command handles request exceptions correctly"""
        # Configure mock to raise an exception
        mock_make_request.side_effect = Exception('Network error')
        
        # Capture command output
        out = StringIO()
        
        # Run the management command
        call_command('populate_swapi_data', limit=5, stdout=out)
        
        # Check that the command output contains error messages
        output = out.getvalue()
        self.assertIn('Error populating films', output)
        self.assertIn('Error populating characters', output)
        self.assertIn('Error populating starships', output)
        
        # Check that no records were created
        self.assertEqual(Film.objects.count(), 0)
        self.assertEqual(Character.objects.count(), 0)
        self.assertEqual(Starship.objects.count(), 0)