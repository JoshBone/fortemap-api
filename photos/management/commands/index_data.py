from django.core.management import BaseCommand

from photos.indexer import FortepanLocationIndexer
from photos.models import Photo, Location


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument("--place", type=str, default='Budapest V.')
        parser.add_argument("--input_file", type=str)

    def handle(self, *args, **options):
        indexer = FortepanLocationIndexer(place=options['place'], input_file=options['input_file'])
        for location in Location.objects.filter(photo__status='OK', photo__place=options['place']).all():
            indexer.get_fortepan_data(location.photo.fortepan_id)
            indexer.set_location(location)
            indexer.make_document()
            indexer.index()
            pass