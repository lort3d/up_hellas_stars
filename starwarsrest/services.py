import requests
from django.conf import settings
from decouple import config
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from django.core.exceptions import ValidationError
from .models import Character, Film, Starship


# Get the setting for allowing unofficial records
ALLOW_UNOFFICIAL_RECORDS = config('ALLOW_UNOFFICIAL_RECORDS', default=True, cast=bool)


class SwapiService:
    """Service for interacting with the Star Wars API (SWAPI)"""
    
    BASE_URL = "https://swapi.dev/api"
    
    def __init__(self):
        # Create a session with retry strategy for resilience
        self.session = requests.Session()
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
    
    def _make_request(self, url, timeout=10):
        """Make a request to SWAPI with proper error handling"""
        try:
            response = self.session.get(url, timeout=timeout)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.Timeout:
            raise ValidationError("Request to SWAPI timed out")
        except requests.exceptions.ConnectionError:
            raise ValidationError("Could not connect to SWAPI")
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 404:
                return None
            raise ValidationError(f"SWAPI returned an error: {e.response.status_code}")
        except requests.exceptions.RequestException as e:
            raise ValidationError(f"Error communicating with SWAPI: {str(e)}")
        except ValueError:  # JSON decode error
            raise ValidationError("Invalid response from SWAPI")
    
    def search_character(self, name):
        """Search for a character by name in SWAPI"""
        url = f"{self.BASE_URL}/people/?search={name}"
        data = self._make_request(url)
        if data and data.get('results'):
            # Return the first match
            return data['results'][0]
        return None
    
    def get_character_by_id(self, swapi_id):
        """Get a character by ID from SWAPI"""
        url = f"{self.BASE_URL}/people/{swapi_id}/"
        return self._make_request(url)
    
    def search_film(self, title):
        """Search for a film by title in SWAPI"""
        url = f"{self.BASE_URL}/films/?search={title}"
        data = self._make_request(url)
        if data and data.get('results'):
            # Return the first match
            return data['results'][0]
        return None
    
    def get_film_by_id(self, swapi_id):
        """Get a film by ID from SWAPI"""
        url = f"{self.BASE_URL}/films/{swapi_id}/"
        return self._make_request(url)
    
    def search_starship(self, name):
        """Search for a starship by name in SWAPI"""
        url = f"{self.BASE_URL}/starships/?search={name}"
        data = self._make_request(url)
        if data and data.get('results'):
            # Return the first match
            return data['results'][0]
        return None
    
    def get_starship_by_id(self, swapi_id):
        """Get a starship by ID from SWAPI"""
        url = f"{self.BASE_URL}/starships/{swapi_id}/"
        return self._make_request(url)
    
    def validate_character_data(self, name, swapi_id=0):
        """
        Validate character data against SWAPI.
        Returns True if valid or if unofficial records are allowed.
        """
        # If swapi_id is 0, it's a custom record
        if swapi_id == 0:
            return ALLOW_UNOFFICIAL_RECORDS
        
        # Try to get character by ID first
        if swapi_id:
            swapi_character = self.get_character_by_id(swapi_id)
            if swapi_character:
                # Verify the name matches if provided
                if name and swapi_character['name'].lower() != name.lower():
                    raise ValidationError(
                        f"Character name '{name}' does not match SWAPI record with ID {swapi_id}"
                    )
                return True
            else:
                raise ValidationError(f"No character found in SWAPI with ID {swapi_id}")
        
        # If we have a name, search for it
        if name:
            swapi_character = self.search_character(name)
            if swapi_character:
                return True
            else:
                # No match found in SWAPI
                return ALLOW_UNOFFICIAL_RECORDS
        
        # If we get here, we have neither name nor swapi_id
        return ALLOW_UNOFFICIAL_RECORDS
    
    def validate_film_data(self, name, swapi_id=0):
        """
        Validate film data against SWAPI.
        Returns True if valid or if unofficial records are allowed.
        """
        # If swapi_id is 0, it's a custom record
        if swapi_id == 0:
            return ALLOW_UNOFFICIAL_RECORDS
        
        # Try to get film by ID first
        if swapi_id:
            swapi_film = self.get_film_by_id(swapi_id)
            if swapi_film:
                # Verify the title matches if provided
                if name and swapi_film['title'].lower() != name.lower():
                    raise ValidationError(
                        f"Film title '{name}' does not match SWAPI record with ID {swapi_id}"
                    )
                return True
            else:
                raise ValidationError(f"No film found in SWAPI with ID {swapi_id}")
        
        # If we have a title, search for it
        if name:
            swapi_film = self.search_film(name)
            if swapi_film:
                return True
            else:
                # No match found in SWAPI
                return ALLOW_UNOFFICIAL_RECORDS
        
        # If we get here, we have neither title nor swapi_id
        return ALLOW_UNOFFICIAL_RECORDS
    
    def validate_starship_data(self, name, model, swapi_id=0):
        """
        Validate starship data against SWAPI.
        Returns True if valid or if unofficial records are allowed.
        """
        # If swapi_id is 0, it's a custom record
        if swapi_id == 0:
            return ALLOW_UNOFFICIAL_RECORDS
        
        # Try to get starship by ID first
        if swapi_id:
            swapi_starship = self.get_starship_by_id(swapi_id)
            if swapi_starship:
                # Verify the name and model match if provided
                if name and swapi_starship['name'].lower() != name.lower():
                    raise ValidationError(
                        f"Starship name '{name}' does not match SWAPI record with ID {swapi_id}"
                    )
                if model and swapi_starship['model'].lower() != model.lower():
                    raise ValidationError(
                        f"Starship model '{model}' does not match SWAPI record with ID {swapi_id}"
                    )
                return True
            else:
                raise ValidationError(f"No starship found in SWAPI with ID {swapi_id}")
        
        # If we have a name, search for it
        if name:
            swapi_starship = self.search_starship(name)
            if swapi_starship:
                # If we also have a model, verify it matches
                if model and swapi_starship['model'].lower() != model.lower():
                    # Model doesn't match, but name does - this might be allowed
                    return ALLOW_UNOFFICIAL_RECORDS
                return True
            else:
                # No match found in SWAPI
                return ALLOW_UNOFFICIAL_RECORDS
        
        # If we get here, we have insufficient data
        return ALLOW_UNOFFICIAL_RECORDS
    
    def populate_character_from_swapi(self, swapi_data):
        """Convert SWAPI character data to our model format"""
        return {
            'name': swapi_data['name'],
            'swapi_id': int(swapi_data['url'].split('/')[-2]),  # Extract ID from URL
            'birth_year': swapi_data.get('birth_year'),
            'eye_color': swapi_data.get('eye_color'),
            'gender': swapi_data.get('gender'),
            'hair_color': swapi_data.get('hair_color'),
            'height': int(swapi_data['height']) if swapi_data.get('height', '').isdigit() else None,
            'mass': swapi_data.get('mass'),
            'skin_color': swapi_data.get('skin_color'),
            'homeworld': swapi_data.get('homeworld'),
        }
    
    def populate_film_from_swapi(self, swapi_data):
        """Convert SWAPI film data to our model format"""
        return {
            'name': swapi_data['title'],
            'swapi_id': int(swapi_data['url'].split('/')[-2]),  # Extract ID from URL
            'episode_id': swapi_data.get('episode_id'),
            'opening_crawl': swapi_data.get('opening_crawl'),
            'director': swapi_data.get('director'),
            'producer': swapi_data.get('producer'),
            'release_date': swapi_data.get('release_date'),
        }
    
    def populate_starship_from_swapi(self, swapi_data):
        """Convert SWAPI starship data to our model format"""
        return {
            'name': swapi_data['name'],
            'model': swapi_data['model'],
            'swapi_id': int(swapi_data['url'].split('/')[-2]),  # Extract ID from URL
            'starship_class': swapi_data.get('starship_class'),
            'manufacturer': swapi_data.get('manufacturer'),
            'cost_in_credits': swapi_data.get('cost_in_credits'),
            'length': swapi_data.get('length'),
            'crew': swapi_data.get('crew'),
            'passengers': swapi_data.get('passengers'),
            'max_atmosphering_speed': swapi_data.get('max_atmosphering_speed'),
            'hyperdrive_rating': swapi_data.get('hyperdrive_rating'),
            'mglt': swapi_data.get('MGLT'),
            'cargo_capacity': swapi_data.get('cargo_capacity'),
            'consumables': swapi_data.get('consumables'),
        }