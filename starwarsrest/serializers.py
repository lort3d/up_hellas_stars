from rest_framework import serializers
from .models import Character, Film, Starship


class FilmSerializer(serializers.ModelSerializer):
    class Meta:
        model = Film
        fields = '__all__'
        read_only_fields = ('created', 'edited')


class CharacterSerializer(serializers.ModelSerializer):
    films = FilmSerializer(many=True, required=False)

    class Meta:
        model = Character
        fields = '__all__'
        read_only_fields = ('created', 'edited')

    def create(self, validated_data):
        films_data = validated_data.pop('films', [])
        character = Character.objects.create(**validated_data)
        character.films.set(films_data)
        return character

    def update(self, instance, validated_data):
        films_data = validated_data.pop('films', None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        if films_data is not None:
            instance.films.set(films_data)

        return instance


class StarshipSerializer(serializers.ModelSerializer):
    films = FilmSerializer(many=True, required=False)
    pilots = CharacterSerializer(many=True, required=False)

    class Meta:
        model = Starship
        fields = '__all__'
        read_only_fields = ('created', 'edited')

    def create(self, validated_data):
        films_data = validated_data.pop('films', [])
        pilots_data = validated_data.pop('pilots', [])
        starship = Starship.objects.create(**validated_data)
        starship.films.set(films_data)
        starship.pilots.set(pilots_data)
        return starship

    def update(self, instance, validated_data):
        films_data = validated_data.pop('films', None)
        pilots_data = validated_data.pop('pilots', None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        if films_data is not None:
            instance.films.set(films_data)
        if pilots_data is not None:
            instance.pilots.set(pilots_data)

        return instance
