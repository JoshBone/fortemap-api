from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Count
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters import rest_framework as filters
from rest_framework.response import Response
from rest_framework.views import APIView

import photos
from photos.models import Photo
from photos.serializers import PhotoListSerializer, PhotoDetailSerializer, LocationListSerializer, \
    LocationBatchCreateSerializer
from photos.models import Location


class PhotoFilter(filters.FilterSet):
    locations_count = filters.NumberFilter(method='filter_locations_count')

    def filter_locations_count(self, queryset, name, value):
        return queryset.annotate(loc=Count('locations')).filter(loc=value)

    class Meta:
        model = Photo
        fields = ['status', 'place', 'editor']


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

    def get_serializer_context(self):
        context = super().get_serializer_context()
        print(self.kwargs)
        if 'photo_table_filter' in self.kwargs:
            context["photo_table_filter"] = self.kwargs['photo_table_filter']
        else:
            context["photo_table_filter"]=''
        return context

    def get_object(self):
        return get_object_or_404(Photo, fortepan_id=self.kwargs['pk'])

    '''
    UpdateAPIView automatically generate the PATCH handling, there is no need to implement it, unless,
    we need someting different than the default behaviour.
    '''


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


class LocationsBatchCreate(APIView):
    permission_classes = []
    serializer_class = LocationBatchCreateSerializer

    def post(self, request, format=None):
        photos = request.data.get('photos', [])
        location = request.data.get('location', None)

        for photo_id in photos:
            try:
                photo = Photo.objects.get(fortepan_id=photo_id)
                loc, created = Location.objects.get_or_create(
                    photo=photo,
                    original_address=location['original_address'],
                    geocoded_address=location['geocoded_address'],
                    latitude=location['latitude'],
                    longitude=location['longitude'],
                    geotag_provider=location['geotag_provider']
                )
            except ObjectDoesNotExist:
                continue
        return Response({'status': 'ok'})


class EditorList(APIView):
    permission_classes = []

    def get(self, request, format=None):
        editors = Photo.objects.exclude(editor__isnull=True).order_by().values_list('editor').distinct()
        return Response(editors)


class PlaceList(APIView):
    permission_classes = []

    def get(self, request, format=None):
        places = Photo.objects.exclude(place__isnull=True).order_by().values_list('place').distinct()
        return Response(places)

class StatisticsList(APIView):
    permission_classes = []

    def get(self, request, format=None):
        stats = []
        editors = Photo.objects.exclude(editor__isnull=True).order_by('editor').values_list('editor').distinct()
        for editor in editors:
            ok = Photo.objects.filter(editor=editor[0], status='OK').count()
            nk = Photo.objects.filter(editor=editor[0], status='NK').count()
            elh_var = Photo.objects.filter(editor=editor[0], status='ELH_VAR').count()
            total = Photo.objects.filter(editor=editor[0]).count()
            stats.append({'editor': editor[0], 'total': total, 'OK': ok, 'NK': nk, 'ELH_VAR': elh_var})
        return Response(stats)
