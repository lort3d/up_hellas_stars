from django.db import transaction
from django.core.exceptions import ValidationError
from .models import Character, Film, Starship


class CharacterDAO:
    """Data Access Object for Character model"""
    
    @staticmethod
    def get_character_by_id(character_id):
        """Get a character by ID"""
        try:
            return Character.objects.get(id=character_id)
        except Character.DoesNotExist:
            return None
    
    @staticmethod
    def get_character_by_name(name):
        """Get a character by name"""
        try:
            return Character.objects.get(name=name)
        except Character.DoesNotExist:
            return None
    
    @staticmethod
    def get_character_by_swapi_id(swapi_id):
        """Get a character by SWAPI ID"""
        try:
            return Character.objects.get(swapi_id=swapi_id)
        except Character.DoesNotExist:
            return None
    
    @staticmethod
    def list_characters():
        """List all characters"""
        return Character.objects.all()
    
    @staticmethod
    def search_characters_by_name(name):
        """Search characters by name (case-insensitive partial match)"""
        return Character.objects.filter(name__icontains=name)
    
    @staticmethod
    @transaction.atomic
    def create_character(data):
        """Create a new character"""
        try:
            films_data = data.pop('films', [])
            character = Character.objects.create(**data)
            if films_data:
                character.films.set(films_data)
            return character
        except ValidationError as e:
            raise e
        except Exception as e:
            raise ValidationError(f"Error creating character: {str(e)}")
    
    @staticmethod
    @transaction.atomic
    def update_character(character_id, data):
        """Update an existing character"""
        try:
            character = Character.objects.get(id=character_id)
            for key, value in data.items():
                setattr(character, key, value)
            character.save()
            return character
        except Character.DoesNotExist:
            raise ValidationError("Character not found")
        except ValidationError as e:
            raise e
        except Exception as e:
            raise ValidationError(f"Error updating character: {str(e)}")
    
    @staticmethod
    @transaction.atomic
    def delete_character(character_id):
        """Delete a character"""
        try:
            character = Character.objects.get(id=character_id)
            character.delete()
            return True
        except Character.DoesNotExist:
            return False


class FilmDAO:
    """Data Access Object for Film model"""
    
    @staticmethod
    def get_film_by_id(film_id):
        """Get a film by ID"""
        try:
            return Film.objects.get(id=film_id)
        except Film.DoesNotExist:
            return None
    
    @staticmethod
    def get_film_by_name(name):
        """Get a film by name"""
        try:
            return Film.objects.get(name=name)
        except Film.DoesNotExist:
            return None
    
    @staticmethod
    def get_film_by_swapi_id(swapi_id):
        """Get a film by SWAPI ID"""
        try:
            return Film.objects.get(swapi_id=swapi_id)
        except Film.DoesNotExist:
            return None
    
    @staticmethod
    def list_films():
        """List all films"""
        return Film.objects.all()
    
    @staticmethod
    def search_films_by_name(name):
        """Search films by name (case-insensitive partial match)"""
        return Film.objects.filter(name__icontains=name)
    
    @staticmethod
    @transaction.atomic
    def create_film(data):
        """Create a new film"""
        try:
            film = Film.objects.create(**data)
            return film
        except ValidationError as e:
            raise e
        except Exception as e:
            raise ValidationError(f"Error creating film: {str(e)}")
    
    @staticmethod
    @transaction.atomic
    def update_film(film_id, data):
        """Update an existing film"""
        try:
            film = Film.objects.get(id=film_id)
            for key, value in data.items():
                setattr(film, key, value)
            film.save()
            return film
        except Film.DoesNotExist:
            raise ValidationError("Film not found")
        except ValidationError as e:
            raise e
        except Exception as e:
            raise ValidationError(f"Error updating film: {str(e)}")
    
    @staticmethod
    @transaction.atomic
    def delete_film(film_id):
        """Delete a film"""
        try:
            film = Film.objects.get(id=film_id)
            film.delete()
            return True
        except Film.DoesNotExist:
            return False


class StarshipDAO:
    """Data Access Object for Starship model"""
    
    @staticmethod
    def get_starship_by_id(starship_id):
        """Get a starship by ID"""
        try:
            return Starship.objects.get(id=starship_id)
        except Starship.DoesNotExist:
            return None
    
    @staticmethod
    def get_starship_by_name_and_model(name, model):
        """Get a starship by name and model"""
        try:
            return Starship.objects.get(name=name, model=model)
        except Starship.DoesNotExist:
            return None
    
    @staticmethod
    def get_starship_by_swapi_id(swapi_id):
        """Get a starship by SWAPI ID"""
        try:
            return Starship.objects.get(swapi_id=swapi_id)
        except Starship.DoesNotExist:
            return None
    
    @staticmethod
    def list_starships():
        """List all starships"""
        return Starship.objects.all()
    
    @staticmethod
    def search_starships_by_name(name):
        """Search starships by name (case-insensitive partial match)"""
        return Starship.objects.filter(name__icontains=name)
    
    @staticmethod
    @transaction.atomic
    def create_starship(data):
        """Create a new starship"""
        try:
            starship = Starship.objects.create(**data)
            return starship
        except ValidationError as e:
            raise e
        except Exception as e:
            raise ValidationError(f"Error creating starship: {str(e)}")
    
    @staticmethod
    @transaction.atomic
    def update_starship(starship_id, data):
        """Update an existing starship"""
        try:
            starship = Starship.objects.get(id=starship_id)
            for key, value in data.items():
                setattr(starship, key, value)
            starship.save()
            return starship
        except Starship.DoesNotExist:
            raise ValidationError("Starship not found")
        except ValidationError as e:
            raise e
        except Exception as e:
            raise ValidationError(f"Error updating starship: {str(e)}")
    
    @staticmethod
    @transaction.atomic
    def delete_starship(starship_id):
        """Delete a starship"""
        try:
            starship = Starship.objects.get(id=starship_id)
            starship.delete()
            return True
        except Starship.DoesNotExist:
            return False