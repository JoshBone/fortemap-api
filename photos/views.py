from django.db.models import Count
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters import rest_framework as filters
from rest_framework.response import Response
from rest_framework.views import APIView

from photos.models import Photo
from photos.serializers import PhotoListSerializer, PhotoDetailSerializer


class PhotoFilter(filters.FilterSet):
    locations_count = filters.NumberFilter(method='filter_locations_count')

    def filter_locations_count(self, queryset, name, value):
        if value:
            queryset = queryset.annotate(loc=Count('locations')).filter(loc=value)
        return queryset

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


class PhotosDetail(generics.RetrieveAPIView):
    permission_classes = []
    queryset = Photo.objects.all()
    serializer_class = PhotoDetailSerializer

    def get_object(self):
        return get_object_or_404(Photo, fortepan_id=self.kwargs['pk'])


class PlacesList(APIView):
    permission_classes = []

    def get(self, request, format=None):
        places = Photo.objects.values('place').distinct()
        return Response(places)

