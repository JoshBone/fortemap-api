from rest_framework import serializers

from photos.models import Photo, Location


class PhotoListSerializer(serializers.ModelSerializer):
    locations_count = serializers.SerializerMethodField()

    def get_locations_count(self, obj):
        return obj.locations.filter(geotag_provider='Nominatim').count()

    class Meta:
        model = Photo
        fields = ['id', 'fortepan_id', 'place', 'year', 'description_original', 'locations_count']


class LocationListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Location
        fields = '__all__'


class PhotoDetailSerializer(serializers.ModelSerializer):
    locations = LocationListSerializer(many=True)
    mapcenter_lat = serializers.SerializerMethodField()
    mapcenter_long = serializers.SerializerMethodField()

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
                  'mapcenter_lat', 'mapcenter_long']
