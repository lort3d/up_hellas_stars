from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django.core.exceptions import ValidationError
from django_filters.rest_framework import DjangoFilterBackend
from .models import Character, Film, Starship
from .serializers import (
    CharacterSerializer, CharacterCreateSerializer,
    FilmSerializer, FilmCreateSerializer,
    StarshipSerializer, StarshipCreateSerializer
)
from .dao import CharacterDAO, FilmDAO, StarshipDAO
from .services import SwapiService, ALLOW_UNOFFICIAL_RECORDS
from .permissions import IsAuthenticatedOrReadOnly


class CharacterViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Characters
    """
    queryset = Character.objects.all()
    serializer_class = CharacterSerializer
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    search_fields = ['name']
    filterset_fields = ['name']
    permission_classes = [IsAuthenticatedOrReadOnly]
    
    def get_serializer_class(self):
        if self.action == 'create' or self.action == 'update' or self.action == 'partial_update':
            return CharacterCreateSerializer
        return CharacterSerializer
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            # Validate against SWAPI if needed
            name = serializer.validated_data.get('name')
            swapi_id = serializer.validated_data.get('swapi_id', 0)
            
            try:
                swapi_service = SwapiService()
                is_valid = swapi_service.validate_character_data(name, swapi_id)
                
                if not is_valid:
                    return Response(
                        {"error": "Character not found in SWAPI and unofficial records are not allowed"},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                
                # If validation passes, create the character
                character = CharacterDAO.create_character(serializer.validated_data)
                response_serializer = CharacterSerializer(character)
                return Response(response_serializer.data, status=status.HTTP_201_CREATED)
            except ValidationError as e:
                return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def update(self, request, *args, **kwargs):
        character_id = kwargs.get('pk')
        serializer = self.get_serializer(data=request.data)
        
        if serializer.is_valid():
            try:
                character = CharacterDAO.update_character(character_id, serializer.validated_data)
                response_serializer = CharacterSerializer(character)
                return Response(response_serializer.data)
            except ValidationError as e:
                return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def partial_update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        if serializer.is_valid():
            try:
                character = CharacterDAO.update_character(instance.id, serializer.validated_data)
                response_serializer = CharacterSerializer(character)
                return Response(response_serializer.data)
            except ValidationError as e:
                return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def destroy(self, request, *args, **kwargs):
        character_id = kwargs.get('pk')
        deleted = CharacterDAO.delete_character(character_id)
        if deleted:
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            return Response(
                {"error": "Character not found"},
                status=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=False, methods=['get'])
    def search(self, request):
        name = request.query_params.get('name', '')
        if not name:
            return Response(
                {"error": "Please provide a 'name' parameter for search"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        characters = CharacterDAO.search_characters_by_name(name)
        serializer = CharacterSerializer(characters, many=True)
        return Response(serializer.data)


class FilmViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Films
    """
    queryset = Film.objects.all()
    serializer_class = FilmSerializer
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    search_fields = ['name']
    filterset_fields = ['name']
    permission_classes = [IsAuthenticatedOrReadOnly]
    
    def get_serializer_class(self):
        if self.action == 'create' or self.action == 'update' or self.action == 'partial_update':
            return FilmCreateSerializer
        return FilmSerializer
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            # Validate against SWAPI if needed
            name = serializer.validated_data.get('name')
            swapi_id = serializer.validated_data.get('swapi_id', 0)
            
            try:
                swapi_service = SwapiService()
                is_valid = swapi_service.validate_film_data(name, swapi_id)
                
                if not is_valid:
                    return Response(
                        {"error": "Film not found in SWAPI and unofficial records are not allowed"},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                
                # If validation passes, create the film
                film = FilmDAO.create_film(serializer.validated_data)
                response_serializer = FilmSerializer(film)
                return Response(response_serializer.data, status=status.HTTP_201_CREATED)
            except ValidationError as e:
                return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def update(self, request, *args, **kwargs):
        film_id = kwargs.get('pk')
        serializer = self.get_serializer(data=request.data)
        
        if serializer.is_valid():
            try:
                film = FilmDAO.update_film(film_id, serializer.validated_data)
                response_serializer = FilmSerializer(film)
                return Response(response_serializer.data)
            except ValidationError as e:
                return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def partial_update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        if serializer.is_valid():
            try:
                film = FilmDAO.update_film(instance.id, serializer.validated_data)
                response_serializer = FilmSerializer(film)
                return Response(response_serializer.data)
            except ValidationError as e:
                return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def destroy(self, request, *args, **kwargs):
        film_id = kwargs.get('pk')
        deleted = FilmDAO.delete_film(film_id)
        if deleted:
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            return Response(
                {"error": "Film not found"},
                status=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=False, methods=['get'])
    def search(self, request):
        name = request.query_params.get('name', '')
        if not name:
            return Response(
                {"error": "Please provide a 'name' parameter for search"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        films = FilmDAO.search_films_by_name(name)
        serializer = FilmSerializer(films, many=True)
        return Response(serializer.data)


class StarshipViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Starships
    """
    queryset = Starship.objects.all()
    serializer_class = StarshipSerializer
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    search_fields = ['name', 'model']
    filterset_fields = ['name', 'model']
    permission_classes = [IsAuthenticatedOrReadOnly]
    
    def get_serializer_class(self):
        if self.action == 'create' or self.action == 'update' or self.action == 'partial_update':
            return StarshipCreateSerializer
        return StarshipSerializer
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            # Validate against SWAPI if needed
            name = serializer.validated_data.get('name')
            model = serializer.validated_data.get('model')
            swapi_id = serializer.validated_data.get('swapi_id', 0)
            
            try:
                swapi_service = SwapiService()
                is_valid = swapi_service.validate_starship_data(name, model, swapi_id)
                
                if not is_valid:
                    return Response(
                        {"error": "Starship not found in SWAPI and unofficial records are not allowed"},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                
                # If validation passes, create the starship
                starship = StarshipDAO.create_starship(serializer.validated_data)
                response_serializer = StarshipSerializer(starship)
                return Response(response_serializer.data, status=status.HTTP_201_CREATED)
            except ValidationError as e:
                return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def update(self, request, *args, **kwargs):
        starship_id = kwargs.get('pk')
        serializer = self.get_serializer(data=request.data)
        
        if serializer.is_valid():
            try:
                starship = StarshipDAO.update_starship(starship_id, serializer.validated_data)
                response_serializer = StarshipSerializer(starship)
                return Response(response_serializer.data)
            except ValidationError as e:
                return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def partial_update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        if serializer.is_valid():
            try:
                starship = StarshipDAO.update_starship(instance.id, serializer.validated_data)
                response_serializer = StarshipSerializer(starship)
                return Response(response_serializer.data)
            except ValidationError as e:
                return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def destroy(self, request, *args, **kwargs):
        starship_id = kwargs.get('pk')
        deleted = StarshipDAO.delete_starship(starship_id)
        if deleted:
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            return Response(
                {"error": "Starship not found"},
                status=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=False, methods=['get'])
    def search(self, request):
        name = request.query_params.get('name', '')
        if not name:
            return Response(
                {"error": "Please provide a 'name' parameter for search"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        starships = StarshipDAO.search_starships_by_name(name)
        serializer = StarshipSerializer(starships, many=True)
        return Response(serializer.data)