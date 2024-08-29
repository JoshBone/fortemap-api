import json
import os

from django.core.management import BaseCommand

from photos.address_guesser.fortepan_address_guesser_with_ner import FortepanAddressGuesserWithNER
from photos.models import Photo, Location

POSTAL_CODES = ['9019', '9011', '9012', '9000', '9021', '9022', '9023', '9024', '9025', '9026', '9027', '9028',
                '9029', '9030']

FILE = 'FortepanVker10000.json'
CITY = 'Budapest'
DISTRICT = ' V.'


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument("--in_file", type=str, default=FILE)

    def handle(self, *args, **options):
        filename = os.path.join(os.path.abspath(os.path.dirname(__file__)), options['in_file'])

        with open(filename, 'r') as json_file:
            results = json.load(json_file)
            #for idx, hit in enumerate(results['hits']['hits']):
            for idx, hit in enumerate(results):
                record = hit['_source']
                city = CITY

                photo, created = Photo.objects.get_or_create(
                    fortepan_id=record['mid'][0]
                )

                if 'description' in record:
                    description = ' '.join(record['description'])
                else:
                    description = ''

                fortepan_address_guesser = FortepanAddressGuesserWithNER(description, city, record['mid'][0], DISTRICT)
                fortepan_address_guesser.ner()

                obj = fortepan_address_guesser.address_object

                photo.description_original = obj['description']
                photo.description_geocoded = obj['tagged_text']
                photo.year = record['year'][0]
                photo.place = CITY
                photo.save()

                print("Processed record: %s" % photo.fortepan_id)

                geocoded_places = fortepan_address_guesser.geocode_nominatim(POSTAL_CODES)

                for place in geocoded_places:
                    if 'original_address' in place.keys():
                        location, created = Location.objects.get_or_create(
                            photo=photo,
                            geotag_provider='Nominatim',
                            original_address=place['original_address'],
                        )
                        location.geocoded_address = place['geocoded_address']
                        location.latitude = place['latitude']
                        location.longitude = place['longitude']
                        location.save()
                        print("Location managed: %s" % place['original_address'])