import json
import re

import requests
from django.conf import settings
from geopy import Nominatim, MapBox

PLACES = ['sarok', 'sarkán', 'szemben', 'torkolat', 'torkolatánál', 'torkolata', 'távolban',
          'háttérben', 'hátul', 'balra', 'jobbra', 'felől', 'felé', 'környékén', 'között']

RAGOK = ['nál', 'nél', 'tól', 'től', 'ból', 'ből', 'ban', 'ben', 'on', 'en', 'ön', 'ról', 'ről']

BLACKLIST = ['Budapest', 'Duna']

class FortepanAddressGuesserWithNER:
    def __init__(self, description, city, id):
        self.description = self.remove_parentheses(description).replace("  ", " ")
        self.city = city
        self.address_object = {
            'id': id,
            'fortepan_url': 'https://fortepan.hu/hu/photos/?id=%s' % id,
            'fortepan_photo_url': 'https://fortepan.download/file/fortepan-eu/1600/fortepan_%s.jpg' % id,
            'description': description,
            'tagged_text': '',
            'places': []
        }

    def is_between_parentheses(self, sentence, part):
        pattern = r'\(.*?\)'
        matches = re.findall(pattern, sentence)
        for match in matches:
            if part in match:
                return True
        return False

    def remove_parentheses(self, text):
        return re.sub(r'\([^)]*\)', '', text)

    def ner(self):
        url = "https://juniper.nytud.hu/demo/nlp/ner"
        r = requests.post(
            url,
            json={"data": self.description}
        )
        if r.status_code == 200:
            response = json.loads(r.text)
            tagged_text = response['ner']
            self.address_object['tagged_text'] = tagged_text

    def geocode_nominatim(self, tagged_text):
        list = []
        pattern = r'\[LOC-B\](.*?)\[LOC-E\]'
        geolocator = Nominatim(user_agent="Fortepan Photo GeoCoding Test")
        matches = re.findall(pattern, tagged_text)

        for match in matches:
            if not self.is_between_parentheses(self.description, match):
                location_object = {}

                # Try to get the house number
                pattern = r' (\d+)'
                regex_pattern = re.compile(re.escape(match) + pattern)
                number_group = re.search(regex_pattern, self.description)
                if number_group:
                    number = number_group.group(1)
                    full_address = "%s %s" % (match, number)
                else:
                    full_address = match

                # Changes
                full_address = full_address.replace('utca', 'u.')

                # Ragtalanítás
                for rag in RAGOK:
                    if full_address[-len(rag):] == rag:
                        full_address = full_address[:-len(rag)]

                if full_address.strip() not in BLACKLIST:
                    # Try to locate
                    address = '%s %s' % (self.city, full_address)
                    try:
                        location = geolocator.geocode(address)
                        if location:
                            location_object['original_address'] = address
                            location_object['geocoded_address'] = location.address
                            location_object['latitude'] = location.latitude
                            location_object['longitude'] = location.longitude
                    except Exception:
                        print("Error locating address: %s" % address)

                    list.append(location_object)
        return list

    def geocode_mapbox(self, tagged_text):
        lst = []
        pattern = r'\[LOC-B\](.*?)\[LOC-E\]'
        geolocator = MapBox(api_key=getattr(settings, 'MAPBOX_API_KEY', None))
        matches = re.findall(pattern, tagged_text)

        for match in matches:
            if not self.is_between_parentheses(self.description, match):
                location_object = {}

                # Try to get the house number
                pattern = r' (\d+)'
                regex_pattern = re.compile(re.escape(match) + pattern)
                number_group = re.search(regex_pattern, self.description)
                if number_group:
                    number = number_group.group(1)
                    full_address = "%s %s" % (match, number)
                else:
                    full_address = match

                # Changes
                full_address = full_address.replace('utca', 'u.')

                if full_address.strip() not in BLACKLIST:
                    # Try to locate
                    address = '%s %s' % (self.city, full_address)
                    try:
                        location = geolocator.geocode(query=address, exactly_one=True)
                        if location:
                            location_object['original_address'] = address
                            location_object['geocoded_address'] = location.address
                            location_object['latitude'] = location.latitude
                            location_object['longitude'] = location.longitude
                    except Exception:
                        print("Error locating address: %s" % address)

                    lst.append(location_object)
        return lst