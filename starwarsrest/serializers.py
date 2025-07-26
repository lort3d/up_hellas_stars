from rest_framework import serializers
from .models import Character, Film, Starship


class FilmSerializer(serializers.ModelSerializer):
    class Meta:
        model = Film
        fields = '__all__'
        read_only_fields = ('created', 'edited')


class CharacterSerializer(serializers.ModelSerializer):
    films = FilmSerializer(many=True, read_only=True)
    
    class Meta:
        model = Character
        fields = '__all__'
        read_only_fields = ('created', 'edited')


class StarshipSerializer(serializers.ModelSerializer):
    films = FilmSerializer(many=True, read_only=True)
    pilots = CharacterSerializer(many=True, read_only=True)
    
    class Meta:
        model = Starship
        fields = '__all__'
        read_only_fields = ('created', 'edited')


class CharacterCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Character
        fields = '__all__'
        read_only_fields = ('created', 'edited')


class FilmCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Film
        fields = '__all__'
        read_only_fields = ('created', 'edited')


class StarshipCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Starship
        fields = '__all__'
        read_only_fields = ('created', 'edited')