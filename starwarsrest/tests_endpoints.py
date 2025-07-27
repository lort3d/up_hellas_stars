from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from django.contrib.auth import get_user_model
from .models import Character, Film, Starship

User = get_user_model()


class CharacterEndpointTest(TestCase):
    """Test cases for Character endpoints"""

    def setUp(self):
        """Set up test data and client"""
        self.client = APIClient()
        
        # Create users
        self.admin_user = User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='adminpass'
        )
        self.regular_user = User.objects.create_user(
            username='user',
            email='user@example.com',
            password='userpass'
        )
        
        # Create test data
        self.film = Film.objects.create(
            name='A New Hope',
            swapi_id=1,
            episode_id=4,
            director='George Lucas',
            producer='Gary Kurtz',
            release_date='1977-05-25'
        )
        
        self.character = Character.objects.create(
            name='Luke Skywalker',
            swapi_id=1,
            birth_year='19BBY',
            eye_color='blue',
            gender='male',
            hair_color='blond',
            height=172,
            mass='77',
            skin_color='fair',
            homeworld='Tatooine'
        )
        self.character.films.add(self.film)
        
        # Character data for creation
        self.character_data = {
            'name': 'Han Solo',
            'swapi_id': 14,
            'birth_year': '29BBY',
            'eye_color': 'brown',
            'gender': 'male',
            'hair_color': 'brown',
            'height': 180,
            'mass': '80',
            'skin_color': 'fair',
            'homeworld': 'Corellia'
        }

    def test_list_characters(self):
        """Test listing all characters"""
        response = self.client.get(reverse('character-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['name'], 'Luke Skywalker')

    def test_get_character(self):
        """Test getting a specific character"""
        response = self.client.get(reverse('character-detail', kwargs={'pk': self.character.id}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Luke Skywalker')
        self.assertIn('films', response.data)
        self.assertEqual(len(response.data['films']), 1)
        self.assertEqual(response.data['films'][0]['name'], 'A New Hope')

    def test_search_characters(self):
        """Test searching characters by name"""
        # Create another character for testing search
        Character.objects.create(
            name='Leia Organa',
            swapi_id=5,
            birth_year='19BBY',
            eye_color='brown',
            gender='female',
            hair_color='brown',
            height=150,
            mass='49',
            skin_color='light',
            homeworld='Alderaan'
        )
        
        # Search for characters with 'Luke' in name
        response = self.client.get(reverse('character-search'), {'name': 'Luke'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['name'], 'Luke Skywalker')
        
        # Search for characters with 'Organa' in name
        response = self.client.get(reverse('character-search'), {'name': 'Organa'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['name'], 'Leia Organa')

    def test_create_character_unauthorized(self):
        """Test creating a character without authentication"""
        response = self.client.post(reverse('character-list'), self.character_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_character_regular_user(self):
        """Test creating a character with regular user (should be allowed for read-only)"""
        self.client.force_authenticate(user=self.regular_user)
        response = self.client.post(reverse('character-list'), self.character_data, format='json')
        # With current permission settings, regular users should be able to create
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_update_character_unauthorized(self):
        """Test updating a character without authentication"""
        updated_data = {'name': 'Luke Updated'}
        response = self.client.patch(
            reverse('character-detail', kwargs={'pk': self.character.id}),
            updated_data,
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_character_regular_user(self):
        """Test updating a character with regular user"""
        self.client.force_authenticate(user=self.regular_user)
        updated_data = {'name': 'Luke Updated'}
        response = self.client.patch(
            reverse('character-detail', kwargs={'pk': self.character.id}),
            updated_data,
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Luke Updated')

    def test_delete_character_unauthorized(self):
        """Test deleting a character without authentication"""
        response = self.client.delete(reverse('character-detail', kwargs={'pk': self.character.id}))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_character_regular_user(self):
        """Test deleting a character with regular user"""
        self.client.force_authenticate(user=self.regular_user)
        response = self.client.delete(reverse('character-detail', kwargs={'pk': self.character.id}))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)


class FilmEndpointTest(TestCase):
    """Test cases for Film endpoints"""

    def setUp(self):
        """Set up test data and client"""
        self.client = APIClient()
        
        # Create users
        self.admin_user = User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='adminpass'
        )
        self.regular_user = User.objects.create_user(
            username='user',
            email='user@example.com',
            password='userpass'
        )
        
        # Create test data
        self.film = Film.objects.create(
            name='The Empire Strikes Back',
            swapi_id=2,
            episode_id=5,
            director='Irvin Kershner',
            producer='Gary Kurtz',
            release_date='1980-05-17'
        )
        
        # Film data for creation
        self.film_data = {
            'name': 'Return of the Jedi',
            'swapi_id': 3,
            'episode_id': 6,
            'director': 'Richard Marquand',
            'producer': 'Howard G. Kazanjian',
            'release_date': '1983-05-25'
        }

    def test_list_films(self):
        """Test listing all films"""
        response = self.client.get(reverse('film-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['name'], 'The Empire Strikes Back')

    def test_get_film(self):
        """Test getting a specific film"""
        response = self.client.get(reverse('film-detail', kwargs={'pk': self.film.id}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'The Empire Strikes Back')

    def test_search_films(self):
        """Test searching films by name"""
        # Create another film for testing search
        Film.objects.create(
            name='Return of the Jedi',
            swapi_id=3,
            episode_id=6,
            director='Richard Marquand',
            producer='Howard G. Kazanjian',
            release_date='1983-05-25'
        )
        
        # Search for films with 'Empire' in name
        response = self.client.get(reverse('film-search'), {'name': 'Empire'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['name'], 'The Empire Strikes Back')
        
        # Search for films with 'Jedi' in name
        response = self.client.get(reverse('film-search'), {'name': 'Jedi'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['name'], 'Return of the Jedi')

    def test_create_film_unauthorized(self):
        """Test creating a film without authentication"""
        response = self.client.post(reverse('film-list'), self.film_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_film_regular_user(self):
        """Test creating a film with regular user"""
        self.client.force_authenticate(user=self.regular_user)
        response = self.client.post(reverse('film-list'), self.film_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_film_admin(self):
        """Test creating a film with admin user"""
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.post(reverse('film-list'), self.film_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['name'], 'Return of the Jedi')

    def test_update_film_regular_user(self):
        """Test updating a film with regular user"""
        self.client.force_authenticate(user=self.regular_user)
        updated_data = {'name': 'Empire Updated'}
        response = self.client.patch(
            reverse('film-detail', kwargs={'pk': self.film.id}),
            updated_data,
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Empire Updated')

    def test_update_film_admin(self):
        """Test updating a film with admin user"""
        self.client.force_authenticate(user=self.admin_user)
        updated_data = {'name': 'Empire Updated by Admin'}
        response = self.client.patch(
            reverse('film-detail', kwargs={'pk': self.film.id}),
            updated_data,
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Empire Updated by Admin')

    def test_delete_film_regular_user(self):
        """Test deleting a film with regular user"""
        self.client.force_authenticate(user=self.regular_user)
        response = self.client.delete(reverse('film-detail', kwargs={'pk': self.film.id}))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_delete_film_admin(self):
        """Test deleting a film with admin user"""
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.delete(reverse('film-detail', kwargs={'pk': self.film.id}))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)


class StarshipEndpointTest(TestCase):
    """Test cases for Starship endpoints"""

    def setUp(self):
        """Set up test data and client"""
        self.client = APIClient()
        
        # Create users
        self.admin_user = User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='adminpass'
        )
        self.regular_user = User.objects.create_user(
            username='user',
            email='user@example.com',
            password='userpass'
        )
        
        # Create test data
        self.starship = Starship.objects.create(
            name='X-wing',
            model='T-65 X-wing',
            swapi_id=12,
            starship_class='Starfighter',
            manufacturer='Incom Corporation',
            cost_in_credits='149999',
            length='12.5',
            crew='1',
            passengers='0',
            max_atmosphering_speed='1050',
            hyperdrive_rating='1.0',
            mglt='100',
            cargo_capacity='110',
            consumables='1 week'
        )
        
        # Starship data for creation
        self.starship_data = {
            'name': 'Millennium Falcon',
            'model': 'YT-1300 light freighter',
            'swapi_id': 10,
            'starship_class': 'Light freighter',
            'manufacturer': 'Corellian Engineering Corporation',
            'cost_in_credits': '100000',
            'length': '34.37',
            'crew': '4',
            'passengers': '6',
            'max_atmosphering_speed': '1050',
            'hyperdrive_rating': '0.5',
            'mglt': '75',
            'cargo_capacity': '100000',
            'consumables': '2 months'
        }

    def test_list_starships(self):
        """Test listing all starships"""
        response = self.client.get(reverse('starship-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['name'], 'X-wing')

    def test_get_starship(self):
        """Test getting a specific starship"""
        response = self.client.get(reverse('starship-detail', kwargs={'pk': self.starship.id}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'X-wing')

    def test_search_starships(self):
        """Test searching starships by name"""
        # Create another starship for testing search
        Starship.objects.create(
            name='Millennium Falcon',
            model='YT-1300 light freighter',
            swapi_id=10,
            starship_class='Light freighter',
            manufacturer='Corellian Engineering Corporation',
            cost_in_credits='100000',
            length='34.37',
            crew='4',
            passengers='6',
            max_atmosphering_speed='1050',
            hyperdrive_rating='0.5',
            mglt='75',
            cargo_capacity='100000',
            consumables='2 months'
        )
        
        # Search for starships with 'X-wing' in name
        response = self.client.get(reverse('starship-search'), {'name': 'X-wing'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['name'], 'X-wing')
        
        # Search for starships with 'Falcon' in name
        response = self.client.get(reverse('starship-search'), {'name': 'Falcon'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['name'], 'Millennium Falcon')

    def test_create_starship_unauthorized(self):
        """Test creating a starship without authentication"""
        response = self.client.post(reverse('starship-list'), self.starship_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_starship_regular_user(self):
        """Test creating a starship with regular user"""
        self.client.force_authenticate(user=self.regular_user)
        response = self.client.post(reverse('starship-list'), self.starship_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_starship_admin(self):
        """Test creating a starship with admin user"""
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.post(reverse('starship-list'), self.starship_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['name'], 'Millennium Falcon')

    def test_update_starship_regular_user(self):
        """Test updating a starship with regular user"""
        self.client.force_authenticate(user=self.regular_user)
        updated_data = {'name': 'X-wing Updated', 'model': 'by user'}
        response = self.client.patch(
            reverse('starship-detail', kwargs={'pk': self.starship.id}),
            updated_data,
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'X-wing Updated')

    def test_update_starship_admin(self):
        """Test updating a starship with admin user"""
        self.client.force_authenticate(user=self.admin_user)
        updated_data = {'name': 'X-wing Updated by Admin', 'model': 'by Admin'}
        response = self.client.patch(
            reverse('starship-detail', kwargs={'pk': self.starship.id}),
            updated_data,
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'X-wing Updated by Admin')

    def test_delete_starship_regular_user(self):
        """Test deleting a starship with regular user"""
        self.client.force_authenticate(user=self.regular_user)
        response = self.client.delete(reverse('starship-detail', kwargs={'pk': self.starship.id}))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_delete_starship_admin(self):
        """Test deleting a starship with admin user"""
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.delete(reverse('starship-detail', kwargs={'pk': self.starship.id}))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)