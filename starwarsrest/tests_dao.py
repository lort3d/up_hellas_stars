from django.test import TestCase
from django.core.exceptions import ValidationError
from .models import Character, Film, Starship
from .dao import CharacterDAO, FilmDAO, StarshipDAO


class CharacterDAOTest(TestCase):
    """Test cases for CharacterDAO"""

    def setUp(self):
        """Create test data"""
        self.film_data = {
            'name': 'A New Hope',
            'swapi_id': 1,
            'episode_id': 4,
            'director': 'George Lucas',
            'producer': 'Gary Kurtz',
            'release_date': '1977-05-25'
        }
        self.film = FilmDAO.create_film(self.film_data)

        self.character_data = {
            'name': 'Luke Skywalker',
            'swapi_id': 1,
            'birth_year': '19BBY',
            'eye_color': 'blue',
            'gender': 'male',
            'hair_color': 'blond',
            'height': 172,
            'mass': '77',
            'skin_color': 'fair',
            'homeworld': 'Tatooine'
        }
        self.character = CharacterDAO.create_character(self.character_data)
        # Associate character with film
        self.character.films.add(self.film)

    def test_get_character_by_id(self):
        """Test getting character by ID"""
        character = CharacterDAO.get_character_by_id(self.character.id)
        self.assertIsNotNone(character)
        self.assertEqual(character.name, 'Luke Skywalker')

    def test_get_character_by_name(self):
        """Test getting character by name"""
        character = CharacterDAO.get_character_by_name('Luke Skywalker')
        self.assertIsNotNone(character)
        self.assertEqual(character.id, self.character.id)

    def test_get_character_by_swapi_id(self):
        """Test getting character by SWAPI ID"""
        character = CharacterDAO.get_character_by_swapi_id(1)
        self.assertIsNotNone(character)
        self.assertEqual(character.name, 'Luke Skywalker')

    def test_list_characters(self):
        """Test listing all characters"""
        characters = CharacterDAO.list_characters()
        self.assertEqual(len(characters), 1)
        self.assertEqual(characters[0].name, 'Luke Skywalker')

    def test_search_characters_by_name(self):
        """Test searching characters by name"""
        # Create another character for testing search
        another_character = CharacterDAO.create_character({
            'name': 'Leia Organa',
            'swapi_id': 5,
            'birth_year': '19BBY',
            'eye_color': 'brown',
            'gender': 'female',
            'hair_color': 'brown',
            'height': 150,
            'mass': '49',
            'skin_color': 'light',
            'homeworld': 'Alderaan'
        })
        
        # Search for characters with 'Luke' in name
        results = CharacterDAO.search_characters_by_name('Luke')
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].name, 'Luke Skywalker')
        
        # Search for characters with 'Organa' in name
        results = CharacterDAO.search_characters_by_name('Organa')
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].name, 'Leia Organa')
        
        # Search for characters with 'Sky' in name
        results = CharacterDAO.search_characters_by_name('Sky')
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].name, 'Luke Skywalker')

    def test_create_character(self):
        """Test creating a character"""
        new_character_data = {
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
        character = CharacterDAO.create_character(new_character_data)
        self.assertIsNotNone(character)
        self.assertEqual(character.name, 'Han Solo')

    def test_create_character_duplicate_name(self):
        """Test creating a character with duplicate name should fail"""
        with self.assertRaises(ValidationError):
            CharacterDAO.create_character(self.character_data)

    def test_update_character(self):
        """Test updating a character"""
        updated_data = {
            'name': 'Luke Skywalker Updated',
            'eye_color': 'green'
        }
        character = CharacterDAO.update_character(self.character.id, updated_data)
        self.assertEqual(character.name, 'Luke Skywalker Updated')
        self.assertEqual(character.eye_color, 'green')
        # Other fields should remain unchanged
        self.assertEqual(character.birth_year, '19BBY')

    def test_update_character_not_found(self):
        """Test updating a non-existent character"""
        with self.assertRaises(ValidationError):
            CharacterDAO.update_character(99999, {'name': 'Non-existent'})

    def test_delete_character(self):
        """Test deleting a character"""
        result = CharacterDAO.delete_character(self.character.id)
        self.assertTrue(result)
        # Verify character is deleted
        character = CharacterDAO.get_character_by_id(self.character.id)
        self.assertIsNone(character)

    def test_delete_character_not_found(self):
        """Test deleting a non-existent character"""
        result = CharacterDAO.delete_character(99999)
        self.assertFalse(result)


class FilmDAOTest(TestCase):
    """Test cases for FilmDAO"""

    def setUp(self):
        """Create test data"""
        self.film_data = {
            'name': 'The Empire Strikes Back',
            'swapi_id': 2,
            'episode_id': 5,
            'director': 'Irvin Kershner',
            'producer': 'Gary Kurtz',
            'release_date': '1980-05-17'
        }
        self.film = FilmDAO.create_film(self.film_data)

    def test_get_film_by_id(self):
        """Test getting film by ID"""
        film = FilmDAO.get_film_by_id(self.film.id)
        self.assertIsNotNone(film)
        self.assertEqual(film.name, 'The Empire Strikes Back')

    def test_get_film_by_name(self):
        """Test getting film by name"""
        film = FilmDAO.get_film_by_name('The Empire Strikes Back')
        self.assertIsNotNone(film)
        self.assertEqual(film.id, self.film.id)

    def test_get_film_by_swapi_id(self):
        """Test getting film by SWAPI ID"""
        film = FilmDAO.get_film_by_swapi_id(2)
        self.assertIsNotNone(film)
        self.assertEqual(film.name, 'The Empire Strikes Back')

    def test_list_films(self):
        """Test listing all films"""
        films = FilmDAO.list_films()
        self.assertEqual(len(films), 1)
        self.assertEqual(films[0].name, 'The Empire Strikes Back')

    def test_search_films_by_name(self):
        """Test searching films by name"""
        # Create another film for testing search
        another_film = FilmDAO.create_film({
            'name': 'Return of the Jedi',
            'swapi_id': 3,
            'episode_id': 6,
            'director': 'Richard Marquand',
            'producer': 'Howard G. Kazanjian',
            'release_date': '1983-05-25'
        })
        
        # Search for films with 'Empire' in name
        results = FilmDAO.search_films_by_name('Empire')
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].name, 'The Empire Strikes Back')
        
        # Search for films with 'Jedi' in name
        results = FilmDAO.search_films_by_name('Jedi')
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].name, 'Return of the Jedi')

    def test_create_film(self):
        """Test creating a film"""
        new_film_data = {
            'name': 'A New Hope',
            'swapi_id': 1,
            'episode_id': 4,
            'director': 'George Lucas',
            'producer': 'Gary Kurtz',
            'release_date': '1977-05-25'
        }
        film = FilmDAO.create_film(new_film_data)
        self.assertIsNotNone(film)
        self.assertEqual(film.name, 'A New Hope')

    def test_create_film_duplicate_name(self):
        """Test creating a film with duplicate name should fail"""
        with self.assertRaises(ValidationError):
            FilmDAO.create_film(self.film_data)

    def test_update_film(self):
        """Test updating a film"""
        updated_data = {
            'name': 'The Empire Strikes Back Updated',
            'director': 'Irvin Updated'
        }
        film = FilmDAO.update_film(self.film.id, updated_data)
        self.assertEqual(film.name, 'The Empire Strikes Back Updated')
        self.assertEqual(film.director, 'Irvin Updated')
        # Other fields should remain unchanged
        self.assertEqual(film.episode_id, 5)

    def test_update_film_not_found(self):
        """Test updating a non-existent film"""
        with self.assertRaises(ValidationError):
            FilmDAO.update_film(99999, {'name': 'Non-existent'})

    def test_delete_film(self):
        """Test deleting a film"""
        result = FilmDAO.delete_film(self.film.id)
        self.assertTrue(result)
        # Verify film is deleted
        film = FilmDAO.get_film_by_id(self.film.id)
        self.assertIsNone(film)

    def test_delete_film_not_found(self):
        """Test deleting a non-existent film"""
        result = FilmDAO.delete_film(99999)
        self.assertFalse(result)


class StarshipDAOTest(TestCase):
    """Test cases for StarshipDAO"""

    def setUp(self):
        """Create test data"""
        self.starship_data = {
            'name': 'X-wing',
            'model': 'T-65 X-wing',
            'swapi_id': 12,
            'starship_class': 'Starfighter',
            'manufacturer': 'Incom Corporation',
            'cost_in_credits': '149999',
            'length': '12.5',
            'crew': '1',
            'passengers': '0',
            'max_atmosphering_speed': '1050',
            'hyperdrive_rating': '1.0',
            'mglt': '100',
            'cargo_capacity': '110',
            'consumables': '1 week'
        }
        self.starship = StarshipDAO.create_starship(self.starship_data)

    def test_get_starship_by_id(self):
        """Test getting starship by ID"""
        starship = StarshipDAO.get_starship_by_id(self.starship.id)
        self.assertIsNotNone(starship)
        self.assertEqual(starship.name, 'X-wing')

    def test_get_starship_by_name_and_model(self):
        """Test getting starship by name and model"""
        starship = StarshipDAO.get_starship_by_name_and_model('X-wing', 'T-65 X-wing')
        self.assertIsNotNone(starship)
        self.assertEqual(starship.id, self.starship.id)

    def test_get_starship_by_swapi_id(self):
        """Test getting starship by SWAPI ID"""
        starship = StarshipDAO.get_starship_by_swapi_id(12)
        self.assertIsNotNone(starship)
        self.assertEqual(starship.name, 'X-wing')

    def test_list_starships(self):
        """Test listing all starships"""
        starships = StarshipDAO.list_starships()
        self.assertEqual(len(starships), 1)
        self.assertEqual(starships[0].name, 'X-wing')

    def test_search_starships_by_name(self):
        """Test searching starships by name"""
        # Create another starship for testing search
        another_starship = StarshipDAO.create_starship({
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
        })
        
        # Search for starships with 'X-wing' in name
        results = StarshipDAO.search_starships_by_name('X-wing')
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].name, 'X-wing')
        
        # Search for starships with 'Falcon' in name
        results = StarshipDAO.search_starships_by_name('Falcon')
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].name, 'Millennium Falcon')

    def test_create_starship(self):
        """Test creating a starship"""
        new_starship_data = {
            'name': 'TIE Advanced x1',
            'model': 'TIE Advanced x1',
            'swapi_id': 13,
            'starship_class': 'Starfighter',
            'manufacturer': 'Sienar Fleet Systems',
            'cost_in_credits': '0',
            'length': '9.2',
            'crew': '1',
            'passengers': '0',
            'max_atmosphering_speed': '1200',
            'hyperdrive_rating': '1.0',
            'mglt': '105',
            'cargo_capacity': '150',
            'consumables': '5 days'
        }
        starship = StarshipDAO.create_starship(new_starship_data)
        self.assertIsNotNone(starship)
        self.assertEqual(starship.name, 'TIE Advanced x1')

    def test_create_starship_duplicate_name_model(self):
        """Test creating a starship with duplicate name-model pair should fail"""
        with self.assertRaises(ValidationError):
            StarshipDAO.create_starship(self.starship_data)

    def test_update_starship(self):
        """Test updating a starship"""
        updated_data = {
            'name': 'X-wing Updated',
            'manufacturer': 'Updated Corporation'
        }
        starship = StarshipDAO.update_starship(self.starship.id, updated_data)
        self.assertEqual(starship.name, 'X-wing Updated')
        self.assertEqual(starship.manufacturer, 'Updated Corporation')
        # Other fields should remain unchanged
        self.assertEqual(starship.model, 'T-65 X-wing')

    def test_update_starship_not_found(self):
        """Test updating a non-existent starship"""
        with self.assertRaises(ValidationError):
            StarshipDAO.update_starship(99999, {'name': 'Non-existent'})

    def test_delete_starship(self):
        """Test deleting a starship"""
        result = StarshipDAO.delete_starship(self.starship.id)
        self.assertTrue(result)
        # Verify starship is deleted
        starship = StarshipDAO.get_starship_by_id(self.starship.id)
        self.assertIsNone(starship)

    def test_delete_starship_not_found(self):
        """Test deleting a non-existent starship"""
        result = StarshipDAO.delete_starship(99999)
        self.assertFalse(result)