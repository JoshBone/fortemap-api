from urllib.parse import urlparse, parse_qs

from django.db.models import Count, Q
from rest_framework import serializers

from photos.models import Photo, Location

PHOTO_STATUSES = [
    ('ELL_VAR', 'Ellenőrzésre vár'),
    ('ELH_VAR', 'Elhelyezésre vár'),
    ('OK', 'Elhelyezve'),
    ('NK', 'Nincs Koordináta')
]

class PhotoListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Photo
        fields = ['id', 'fortepan_id', 'place', 'year', 'description_original', 'status', 'editor', 'locations_count']


class LocationListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Location
        fields = '__all__'


class LocationBatchCreateSerializer(serializers.ModelSerializer):
    photos = serializers.ListSerializer(child=serializers.IntegerField())
    location = LocationListSerializer(many=False)


class PhotoBatchStatusModifySerializer(serializers.ModelSerializer):
    photos = serializers.ListSerializer(child=serializers.IntegerField())
    status = serializers.ChoiceField(choices=PHOTO_STATUSES)


class PhotoUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Photo
        fields = ['status']

class PhotoDetailSerializer(serializers.ModelSerializer):
    locations = LocationListSerializer(many=True)
    mapcenter_lat = serializers.SerializerMethodField()
    mapcenter_long = serializers.SerializerMethodField()
    
    next_photo_id = serializers.SerializerMethodField()
    original_filter_params = serializers.SerializerMethodField()

    def get_original_filter_params(self, obj):
        return self.context["photo_table_filter"]

    def get_next_photo_id(self, obj):
        length = obj.fortepan_id

        parsed_url_params = urlparse(self.context["photo_table_filter"])
        url_params = parse_qs(parsed_url_params.query)

        filter_params = dict((k.replace('filter_',''), url_params[k][0]) for k in ['filter_place', 'filter_locations_count', 'filter_status', 'filter_editor']
                if k in url_params)

        if 'locations_count' in filter_params:
            filter_params['location_count'] = filter_params.pop('locations_count')
        
        search_query = ~Q(pk__in=[])
        if 'search' in filter_params:
            search_str = filter_params.pop('search')
            search_query = (Q( description_original__icontains=search_str) | Q(place__icontains=search_str) |  Q(year__icontains=search_str) | Q(fortepan_id__icontains=search_str))
        ##ha nincs kereses, nincs kovetkezo foto. 
        # if not filter_params:
        #     return None

        filter_params['fortepan_id__gt']=obj.fortepan_id

        photos = Photo.objects.annotate(location_count=Count('locations')).filter(Q(**filter_params) & search_query).order_by('fortepan_id')[:1]

        if photos.count() > 0:
            next_photo = photos[0]
            return next_photo.fortepan_id
        return None

    def get_mapcenter_lat(self, obj):
        lat_sum = 0
        for loc in obj.locations.all():
            lat_sum += loc.latitude
        if obj.locations.count() > 0:
            return lat_sum / obj.locations.count()

    def get_mapcenter_long(self, obj):
        long_sum = 0
        for loc in obj.locations.all():
            long_sum += loc.longitude
        if obj.locations.count() > 0:
            return long_sum / obj.locations.count()

    class Meta:
        model = Photo
        fields = ['id', 'fortepan_id', 'description_original', 'description_geocoded', 'locations',
                  'mapcenter_lat', 'mapcenter_long', 'editor', 'comment', 'status', 'date_created', 'next_photo_id', 'original_filter_params']
