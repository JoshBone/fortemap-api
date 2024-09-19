from django.db import models


PHOTO_STATUSES = [
    ('ELL_VAR', 'Ellenőrzésre vár'),
    ('ELH_VAR', 'Elhelyezésre vár'),
    ('OK', 'Elhelyezve'),
    ('NK', 'Nincs Koordináta')
]


# Create your models here.
class Photo(models.Model):
    id = models.AutoField(primary_key=True)
    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)
    fortepan_id = models.IntegerField()
    place = models.CharField(max_length=500, blank=True, null=True)
    description_original = models.TextField()
    description_geocoded = models.TextField()
    year = models.IntegerField(blank=True, null=True)
    editor = models.CharField(max_length=100, blank=True, null=True)
    comment = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=8, choices=PHOTO_STATUSES, default='ELL_VAR', db_index=True)

    @property
    def locations_count(self):
        return self.locations.count()

    class Meta:
        db_table = 'photos'
        indexes = [
            models.Index(fields=['fortepan_id']),
            models.Index(fields=['place']),
            models.Index(fields=['status']),
            models.Index(fields=['editor']),
        ]


class Location(models.Model):
    id = models.AutoField(primary_key=True)
    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)
    photo = models.ForeignKey('Photo', on_delete=models.CASCADE, related_name='locations')
    shooting_location = models.BooleanField(default=False)
    original_address = models.CharField(max_length=500)
    geocoded_address = models.TextField()
    latitude = models.FloatField(blank=True, null=True)
    longitude = models.FloatField(blank=True, null=True)
    geotag_provider = models.CharField(max_length=50)

    class Meta:
        db_table = 'locations'
        indexes = [
            models.Index(fields=['latitude']),
            models.Index(fields=['longitude']),
            models.Index(fields=['geotag_provider']),
        ]
