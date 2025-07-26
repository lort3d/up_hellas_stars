from django.db import models


class Film(models.Model):
    """
    Model representing a Star Wars film.
    """
    name = models.CharField(max_length=200, unique=True)
    swapi_id = models.IntegerField(default=0, help_text="0 for custom/unofficial records")
    
    # Additional fields from SWAPI
    episode_id = models.IntegerField(null=True, blank=True)
    opening_crawl = models.TextField(null=True, blank=True)
    director = models.CharField(max_length=100, null=True, blank=True)
    producer = models.CharField(max_length=200, null=True, blank=True)
    release_date = models.DateField(null=True, blank=True)
    
    created = models.DateTimeField(auto_now_add=True)
    edited = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name


class Character(models.Model):
    """
    Model representing a Star Wars character.
    """
    name = models.CharField(max_length=200, unique=True)
    swapi_id = models.IntegerField(default=0, help_text="0 for custom/unofficial records")
    
    # Additional fields from SWAPI
    birth_year = models.CharField(max_length=20, null=True, blank=True)
    eye_color = models.CharField(max_length=50, null=True, blank=True)
    gender = models.CharField(max_length=50, null=True, blank=True)
    hair_color = models.CharField(max_length=50, null=True, blank=True)
    height = models.IntegerField(null=True, blank=True)
    mass = models.CharField(max_length=50, null=True, blank=True)
    skin_color = models.CharField(max_length=50, null=True, blank=True)
    homeworld = models.CharField(max_length=200, null=True, blank=True)
    
    films = models.ManyToManyField(Film, blank=True, related_name='characters')
    
    created = models.DateTimeField(auto_now_add=True)
    edited = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name


class Starship(models.Model):
    """
    Model representing a Star Wars starship.
    """
    name = models.CharField(max_length=200)
    model = models.CharField(max_length=200)
    
    # Unique constraint on name and model pair
    class Meta:
        unique_together = ('name', 'model')
        
    swapi_id = models.IntegerField(default=0, help_text="0 for custom/unofficial records")
    
    # Additional fields from SWAPI
    starship_class = models.CharField(max_length=100, null=True, blank=True)
    manufacturer = models.CharField(max_length=200, null=True, blank=True)
    cost_in_credits = models.CharField(max_length=50, null=True, blank=True)
    length = models.CharField(max_length=50, null=True, blank=True)
    crew = models.CharField(max_length=50, null=True, blank=True)
    passengers = models.CharField(max_length=50, null=True, blank=True)
    max_atmosphering_speed = models.CharField(max_length=50, null=True, blank=True)
    hyperdrive_rating = models.CharField(max_length=50, null=True, blank=True)
    mglt = models.CharField(max_length=50, null=True, blank=True)
    cargo_capacity = models.CharField(max_length=50, null=True, blank=True)
    consumables = models.CharField(max_length=100, null=True, blank=True)
    
    films = models.ManyToManyField(Film, blank=True, related_name='starships')
    pilots = models.ManyToManyField(Character, blank=True, related_name='starships')
    
    created = models.DateTimeField(auto_now_add=True)
    edited = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.name} ({self.model})"