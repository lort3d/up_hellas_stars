import json
from unittest.mock import patch, Mock
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from .models import Character, Film, Starship
from .dao import CharacterDAO, FilmDAO, StarshipDAO
from .services import SwapiService


class ModelTestCase(TestCase):
    """Test cases for the models"""
    
    def setUp(self):
        """Set up test data"""
        self.film = Film.objects.create(
            name="A New Hope",
            swapi_id=1,
            episode_id=4,
            director="George Lucas",
            producer="Gary Kurtz"
        )
        
        self.character = Character.objects.create(
            name="Luke Skywalker",
            swapi_id=1,
            gender="male",
            birth_year="19BBY"
        )
        self.character.films.add(self.film)
        
        self.starship = Starship.objects.create(
            name="X-wing",
            model="T-65 X-wing",
            swapi_id=1,
            starship_class="Starfighter",
            manufacturer="Incom Corporation"
        )
        self.starship.films.add(self.film)
        self.starship.pilots.add(self.character)
    
    def test_film_creation(self):
        """Test film creation"""
        film = Film.objects.get(name="A New Hope")
        self.assertEqual(film.episode_id, 4)
        self.assertEqual(film.director, "George Lucas")
    
    def test_character_creation(self):
        """Test character creation"""
        character = Character.objects.get(name="Luke Skywalker")
        self.assertEqual(character.gender, "male")
        self.assertEqual(character.birth_year, "19BBY")
        self.assertIn(self.film, character.films.all())
    
    def test_starship_creation(self):
        """Test starship creation"""
        starship = Starship.objects.get(name="X-wing")
        self.assertEqual(starship.model, "T-65 X-wing")
        self.assertEqual(starship.starship_class, "Starfighter")
        self.assertIn(self.film, starship.films.all())
        self.assertIn(self.character, starship.pilots.all())
    
    def test_unique_constraints(self):
        """Test unique constraints"""
        # Test unique film name
        with self.assertRaises(Exception):
            Film.objects.create(name="A New Hope", swapi_id=2)
        
        # Test unique character name
        with self.assertRaises(Exception):
            Character.objects.create(name="Luke Skywalker", swapi_id=2)
        
        # Test unique starship name-model pair
        with self.assertRaises(Exception):
            Starship.objects.create(name="X-wing", model="T-65 X-wing", swapi_id=2)
        
        # Same name, different model should be allowed
        starship2 = Starship.objects.create(
            name="X-wing",
            model="T-70 X-wing",
            swapi_id=2
        )
        self.assertEqual(starship2.model, "T-70 X-wing")


class DAOTestCase(TestCase):
    """Test cases for the DAO classes"""
    
    def setUp(self):
        """Set up test data"""
        self.film = FilmDAO.create_film({
            'name': 'The Empire Strikes Back',
            'swapi_id': 2,
            'episode_id': 5
        })
        
        self.character = CharacterDAO.create_character({
            'name': 'Darth Vader',
            'swapi_id': 4,
            'gender': 'male'
        })
        
        self.starship = StarshipDAO.create_starship({
            'name': 'TIE Advanced x1',
            'model': 'TIE Advanced x1',
            'swapi_id': 10
        })
    
    def test_character_dao(self):
        """Test CharacterDAO methods"""
        # Test get by id
        character = CharacterDAO.get_character_by_id(self.character.id)
        self.assertEqual(character.name, 'Darth Vader')
        
        # Test get by name
        character = CharacterDAO.get_character_by_name('Darth Vader')
        self.assertEqual(character.swapi_id, 4)
        
        # Test search by name
        characters = CharacterDAO.search_characters_by_name('Darth')
        self.assertEqual(len(characters), 1)
        self.assertEqual(characters[0].name, 'Darth Vader')
        
        # Test update
        updated_character = CharacterDAO.update_character(
            self.character.id,
            {'gender': 'male', 'eye_color': 'yellow'}
        )
        self.assertEqual(updated_character.eye_color, 'yellow')
        
        # Test delete
        result = CharacterDAO.delete_character(self.character.id)
        self.assertTrue(result)
        self.assertIsNone(CharacterDAO.get_character_by_id(self.character.id))
    
    def test_film_dao(self):
        """Test FilmDAO methods"""
        # Test get by id
        film = FilmDAO.get_film_by_id(self.film.id)
        self.assertEqual(film.name, 'The Empire Strikes Back')
        
        # Test get by name
        film = FilmDAO.get_film_by_name('The Empire Strikes Back')
        self.assertEqual(film.episode_id, 5)
        
        # Test search by name
        films = FilmDAO.search_films_by_name('Empire')
        self.assertEqual(len(films), 1)
        self.assertEqual(films[0].episode_id, 5)
        
        # Test update
        updated_film = FilmDAO.update_film(
            self.film.id,
            {'director': 'Irvin Kershner', 'producer': 'Gary Kurtz'}
        )
        self.assertEqual(updated_film.director, 'Irvin Kershner')
        
        # Test delete
        result = FilmDAO.delete_film(self.film.id)
        self.assertTrue(result)
        self.assertIsNone(FilmDAO.get_film_by_id(self.film.id))
    
    def test_starship_dao(self):
        """Test StarshipDAO methods"""
        # Test get by id
        starship = StarshipDAO.get_starship_by_id(self.starship.id)
        self.assertEqual(starship.name, 'TIE Advanced x1')
        
        # Test get by name and model
        starship = StarshipDAO.get_starship_by_name_and_model('TIE Advanced x1', 'TIE Advanced x1')
        self.assertEqual(starship.swapi_id, 10)
        
        # Test search by name
        starships = StarshipDAO.search_starships_by_name('TIE')
        self.assertEqual(len(starships), 1)
        self.assertEqual(starships[0].model, 'TIE Advanced x1')
        
        # Test update
        updated_starship = StarshipDAO.update_starship(
            self.starship.id,
            {'manufacturer': 'Sienar Fleet Systems', 'crew': '1'}
        )
        self.assertEqual(updated_starship.manufacturer, 'Sienar Fleet Systems')
        
        # Test delete
        result = StarshipDAO.delete_starship(self.starship.id)
        self.assertTrue(result)
        self.assertIsNone(StarshipDAO.get_starship_by_id(self.starship.id))


class SwapiServiceTestCase(TestCase):
    """Test cases for the SWAPI service"""
    
    def setUp(self):
        """Set up test service"""
        self.service = SwapiService()
    
    @patch('starwarsrest.services.requests.Session.get')
    def test_make_request_success(self, mock_get):
        """Test successful request to SWAPI"""
        # Mock successful response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'name': 'Luke Skywalker'}
        mock_get.return_value = mock_response
        
        result = self.service._make_request('https://swapi.dev/api/people/1/')
        self.assertEqual(result['name'], 'Luke Skywalker')
    
    @patch('starwarsrest.services.requests.Session.get')
    def test_make_request_timeout(self, mock_get):
        """Test timeout handling"""
        # Mock timeout exception
        mock_get.side_effect = SwapiServiceTestCase.TimeoutException()
        
        with self.assertRaises(Exception) as context:
            self.service._make_request('https://swapi.dev/api/people/1/')
        
        self.assertIn('timed out', str(context.exception))
    
    @patch('starwarsrest.services.requests.Session.get')
    def test_search_character(self, mock_get):
        """Test character search"""
        # Mock search response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'count': 1,
            'results': [{'name': 'Luke Skywalker', 'url': 'https://swapi.dev/api/people/1/'}]
        }
        mock_get.return_value = mock_response
        
        result = self.service.search_character('Luke Skywalker')
        self.assertEqual(result['name'], 'Luke Skywalker')
    
    @patch('starwarsrest.services.requests.Session.get')
    def test_search_character_not_found(self, mock_get):
        """Test character search with no results"""
        # Mock empty search response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'count': 0, 'results': []}
        mock_get.return_value = mock_response
        
        result = self.service.search_character('Nonexistent Character')
        self.assertIsNone(result)
    
    class TimeoutException(requests.exceptions.Timeout):
        pass


class APITestCase(APITestCase):
    """Test cases for the API endpoints"""
    
    def setUp(self):
        """Set up test data"""
        self.film = Film.objects.create(
            name="Return of the Jedi",
            swapi_id=3,
            episode_id=6,
            director="Richard Marquand"
        )
        
        self.character = Character.objects.create(
            name="Yoda",
            swapi_id=20,
            gender="male",
            species="Yoda's species"
        )
        
        self.starship = Starship.objects.create(
            name="Millennium Falcon",
            model="YT-1300 light freighter",
            swapi_id=12,
            starship_class="Light freighter"
        )
    
    @patch('starwarsrest.services.SwapiService.validate_character_data')
    def test_create_character(self, mock_validate):
        """Test creating a character"""
        mock_validate.return_value = True
        
        url = reverse('character-list')
        data = {
            'name': 'Han Solo',
            'swapi_id': 14,
            'gender': 'male'
        }
        
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Character.objects.count(), 2)
        self.assertEqual(Character.objects.get(name='Han Solo').gender, 'male')
    
    def test_get_characters(self):
        """Test retrieving characters"""
        url = reverse('character-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
    
    def test_get_character_detail(self):
        """Test retrieving a specific character"""
        url = reverse('character-detail', kwargs={'pk': self.character.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Yoda')
    
    def test_search_characters(self):
        """Test searching characters by name"""
        url = reverse('character-search')
        response = self.client.get(f'{url}?name=Yoda')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['name'], 'Yoda')
    
    @patch('starwarsrest.services.SwapiService.validate_film_data')
    def test_create_film(self, mock_validate):
        """Test creating a film"""
        mock_validate.return_value = True
        
        url = reverse('film-list')
        data = {
            'name': 'The Phantom Menace',
            'swapi_id': 4,
            'episode_id': 1,
            'director': 'George Lucas'
        }
        
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Film.objects.count(), 2)
        self.assertEqual(Film.objects.get(name='The Phantom Menace').episode_id, 1)
    
    def test_get_films(self):
        """Test retrieving films"""
        url = reverse('film-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
    
    def test_search_films(self):
        """Test searching films by name"""
        url = reverse('film-search')
        response = self.client.get(f'{url}?name=Jedi')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['name'], 'Return of the Jedi')
    
    @patch('starwarsrest.services.SwapiService.validate_starship_data')
    def test_create_starship(self, mock_validate):
        """Test creating a starship"""
        mock_validate.return_value = True
        
        url = reverse('starship-list')
        data = {
            'name': 'Executor',
            'model': 'Executor-class star dreadnought',
            'swapi_id': 15,
            'starship_class': 'Star dreadnought'
        }
        
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Starship.objects.count(), 2)
        self.assertEqual(
            Starship.objects.get(name='Executor').starship_class,
            'Star dreadnought'
        )
    
    def test_get_starships(self):
        """Test retrieving starships"""
        url = reverse('starship-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
    
    def test_search_starships(self):
        """Test searching starships by name"""
        url = reverse('starship-search')
        response = self.client.get(f'{url}?name=Falcon')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['name'], 'Millennium Falcon')