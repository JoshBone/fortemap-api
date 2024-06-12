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

    class Meta:
        model = Photo
        fields = ['id', 'fortepan_id', 'description_original', 'description_geocoded', 'locations']
