from django.shortcuts import render
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
    ordering_fields = ('fortepan_id',)
    search_fields = ('description_original',)


class PhotosDetail(generics.RetrieveAPIView):
    permission_classes = []
    queryset = Photo.objects.all()
    serializer_class = PhotoDetailSerializer
