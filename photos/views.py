from django.db.models import Count
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters import rest_framework as filters
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status

from photos.models import Photo
from photos.serializers import PhotoListSerializer, PhotoDetailSerializer, LocationListSerializer, PhotoUpdateSerializer
from photos.models import Location


class PhotoFilter(filters.FilterSet):
    locations_count = filters.NumberFilter(method='filter_locations_count')

    def filter_locations_count(self, queryset, name, value):
        return queryset.annotate(loc=Count('locations')).filter(loc=value)

    class Meta:
        model = Photo
        fields = ['status', 'place']


class PhotosList(generics.ListAPIView):
    permission_classes = []
    queryset = Photo.objects.all()
    serializer_class = PhotoListSerializer
    filter_backends = (SearchFilter, OrderingFilter, DjangoFilterBackend)
    filterset_class = PhotoFilter
    ordering_fields = ('fortepan_id', 'locations_count')
    search_fields = ('description_original', 'place', 'year', 'fortepan_id')


class PhotosDetail(generics.RetrieveUpdateAPIView):
    permission_classes = []
    http_method_names = ['get', 'patch']
    queryset = Photo.objects.all()
    serializer_class = PhotoDetailSerializer

    def get_object(self):
        return get_object_or_404(Photo, fortepan_id=self.kwargs['pk'])
    
    def partial_update(self, request, pk=None):
        instance = self.get_object()
        serializer = PhotoUpdateSerializer(
            instance,
            data=request.data,
            partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        response_serializer = PhotoDetailSerializer(instance)
        return Response(data=response_serializer.data, status=status.HTTP_202_ACCEPTED)


class PlacesList(APIView):
    permission_classes = []

    def get(self, request, format=None):
        places = Photo.objects.values('place').distinct()
        return Response(places)


class LocationsFilter(filters.FilterSet):
    class Meta:
        model = Location
        fields = ['photo_id']


class LocationsList(generics.ListAPIView):
    permission_classes = []
    queryset = Location.objects.all()
    serializer_class = LocationListSerializer
    filter_backends = (SearchFilter, OrderingFilter, DjangoFilterBackend)
    filterset_class = LocationsFilter


class LocationsDetail(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = []
    queryset = Location.objects.all()
    serializer_class = LocationListSerializer

    def get_object(self):
        return get_object_or_404(Location, id=self.kwargs['pk'])
    
class LocationsCreate(generics.CreateAPIView):
    permission_classes = []
    queryset = Location.objects.all()
    serializer_class = LocationListSerializer