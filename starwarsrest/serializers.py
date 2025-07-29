from rest_framework import serializers
from .models import Character, Film, Starship


class FilmSerializer(serializers.ModelSerializer):
    class Meta:
        model = Film
        fields = '__all__'


class CharacterSerializer(serializers.ModelSerializer):
    films = FilmSerializer(many=True, required=False)

    class Meta:
        model = Character
        fields = '__all__'


class StarshipSerializer(serializers.ModelSerializer):
    films = FilmSerializer(many=True, required=False)
    pilots = CharacterSerializer(many=True, required=False)

    class Meta:
        model = Starship
        fields = '__all__'


class CreateCharacterSerializer(serializers.ModelSerializer):
    films = serializers.PrimaryKeyRelatedField(queryset=Film.objects.all(), many=True, required=False)

    class Meta:
        model = Character
        fields = '__all__'


class CreateStarshipSerializer(serializers.ModelSerializer):
    films = serializers.PrimaryKeyRelatedField(queryset=Film.objects.all(), many=True, required=False)
    pilots = serializers.PrimaryKeyRelatedField(queryset=Character.objects.all(), many=True, required=False)

    class Meta:
        model = Starship
        fields = '__all__'
