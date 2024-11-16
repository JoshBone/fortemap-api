import json
import os

import meilisearch
from django.conf import settings


class FortepanLocationIndexer:
    """
    Class to index Location records.
    """

    def __init__(self, place='Budapest V.', input_file=''):
        self.place = place
        self.data_file = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'management', 'commands', input_file)
        self.data = json.load(open(self.data_file))
        self.fortepan_data = {}
        self.location = None
        self.doc = {}

        self.meilisearch_url = getattr(settings, "MEILISEARCH_URL", "")
        self.meilisearch_api_key = getattr(settings, "MEILISEARCH_API_KEY", "")
        self.meilisearch_index_name = getattr(settings, "MEILISEARCH_INDEX", "meilisearch")

        self.client = meilisearch.Client(self.meilisearch_url, self.meilisearch_api_key)
        self.meilisearch_index = self.client.index(self.meilisearch_index_name)

    def get_fortepan_data(self, fortepan_id):
        self.fortepan_data = list(filter(lambda d: d['_source']['mid'] == [fortepan_id], self.data))[0]

    def set_location(self, location):
        self.location = location

    def make_document(self):
        self.doc['id'] = self.location.id
        self.doc['fortepan_id'] = self.location.photo.fortepan_id
        self.doc['_geo'] = {
            'lat': self.location.latitude,
            'lng': self.location.longitude,
        }
        self.doc['cimke'] = self.fortepan_data['_source'].get('cimke_name', None)
        self.doc['adomanyozo'] = self.fortepan_data['_source'].get('adomanyozo_name', None)
        self.doc['leiras'] = self.fortepan_data['_source'].get('description', [''])[0]
        self.doc['kerulet'] = self.place
        self.doc['kerulet_geo'] = self.get_kerulet_geo(self.place)
        self.doc['varos'] = self.get_varos(self.place)
        self.doc['varos_geo'] = self.get_varos_geo(self.place)

    def get_varos(self, place):
        varos = {
            'Budapest V.': 'Budapest',
            'Győr': 'Győr'
        }
        return varos[place]

    def get_kerulet_geo(self, place):
        kerulet = {
            'Budapest V.': {'lat': 47.5002596, 'lng': 19.0314329},
            'Győr': {'lat': 47.6692398, 'lng': 17.3468638},
        }
        return kerulet[place]

    def get_varos_geo(self, place):
        kerulet = {
            'Budapest V.': {'lat': 47.4813274, 'lng': 18.9654951},
            'Győr': {'lat': 47.6692398, 'lng': 17.3468638},
        }
        return kerulet[place]

    def index(self):
        try:
            self.meilisearch_index.add_documents([self.doc])
            print("Document %s added" % self.doc['id'])
        except Exception as e:
            print('Error with Report No. %s! Error: %s' % (self.doc['id'], e))
