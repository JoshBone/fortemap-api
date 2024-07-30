from django.db.models import Count
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics
from rest_framework.filters import SearchFilter, OrderingFilter

from photos.models import Photo
from photos.serializers import PhotoListSerializer, PhotoDetailSerializer


class PhotosList(generics.ListAPIView):
    permission_classes = []
    queryset = Photo.objects.all()
    serializer_class = PhotoListSerializer
    filter_backends = (SearchFilter, OrderingFilter, DjangoFilterBackend)
    ordering_fields = ('fortepan_id', 'locations_count')
    search_fields = ('description_original', 'place', 'year')

    def get_queryset(self):
        locations_count = self.request.GET.get('locations_count')

        queryset = Photo.objects.annotate(locations_count=Count('locations')).all()

        if locations_count:
            queryset = queryset.filter(locations_count=locations_count)

        return queryset


class PhotosDetail(generics.RetrieveAPIView):
    permission_classes = []
    queryset = Photo.objects.all()
    serializer_class = PhotoDetailSerializer

    def get_object(self):
        return get_object_or_404(Photo, fortepan_id=self.kwargs['pk'])
