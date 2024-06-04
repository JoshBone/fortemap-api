from django.db import models


# Create your models here.
class Photo(models.Model):
    id = models.AutoField(primary_key=True)
    fortepan_id = models.IntegerField()
    place = models.CharField(max_length=500, blank=True, null=True)
    description_original = models.TextField()
    description_geocoded = models.TextField()
    year = models.IntegerField(blank=True, null=True)

    class Meta:
        db_table = 'photos'
        indexes = [
            models.Index(fields=['fortepan_id']),
        ]


class Location(models.Model):
    id = models.AutoField(primary_key=True)
    photo = models.ForeignKey('Photo', on_delete=models.CASCADE, related_name='locations')
    original_address = models.CharField(max_length=500)
    geocoded_address = models.TextField()
    latitude = models.FloatField()
    longitude = models.FloatField()
    geotag_provider = models.CharField(max_length=50)

    class Meta:
        db_table = 'locations'
        indexes = [
            models.Index(fields=['latitude']),
            models.Index(fields=['longitude']),
            models.Index(fields=['geotag_provider']),
        ]
