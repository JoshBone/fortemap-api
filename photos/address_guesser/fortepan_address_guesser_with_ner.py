import re
import time

from geopy import Nominatim, MapBox
from transformers import pipeline
from photos.address_guesser.address_manipulations import AddressManipulations

PLACES = ['sarok', 'sarkán', 'szemben', 'torkolat', 'torkolatánál', 'torkolata', 'távolban',
          'háttérben', 'hátul', 'balra', 'jobbra', 'felől', 'felé', 'környékén', 'között']

RAGOK = ['nál', 'nél', 'tól', 'től', 'ból', 'ből', 'ban', 'ben', 'on', 'en', 'én', 'ön', 'ról', 'ről', 'i']

BLACKLIST = ['Budapest', 'Duna', 'Győr', 'Rába']

SUPPORTED_TAGS = ['FAC', 'LOC', 'GPE', 'CARDINAL']

class FortepanAddressGuesserWithNER:
    def __init__(self, description, city, id, district=None):
        self.pipeline = pipeline(
            task="ner",
            model="novakat/nerkor-cars-onpp-hubert"
        )
        self.description = self.remove_parentheses(description).replace("  ", " ")
        self.city = city
        self.district = district
        self.recognized_parts = []
        self.address_object = {
            'id': id,
            'fortepan_url': 'https://fortepan.hu/hu/photos/?id=%s' % id,
            'fortepan_photo_url': 'https://fortepan.download/file/fortepan-eu/1600/fortepan_%s.jpg' % id,
            'description': self.remove_parentheses(description).replace("  ", " "),
            'tagged_text': self.remove_parentheses(description).replace("  ", " "),
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

    def ner(self, address_maniplatior:AddressManipulations=None):
        tagged_text = self.pipeline(self.description, aggregation_strategy="simple")
        for idx, tag in enumerate(tagged_text):
            finding = {}
            skip = False
            # print( "idx: %s" % idx)
            # print( "tag: %s" % tag)
            
            # Handle the '##' case
            if len(self.recognized_parts) > 0:
                if self.recognized_parts[-1]['end'] == tag['start']: #or tag['word'].startswith("##"):
                    self.recognized_parts[-1]['text'] += tag['word'].replace('##', '').replace(' - ', '-')
                    self.recognized_parts[-1]['end'] = tag['end']
                    skip = True

            # Handle house number
            if tag['entity_group'] == 'CARDINAL':
                if len(self.recognized_parts) > 0:
                    if self.recognized_parts[-1]['end'] == tag['start'] - 1:
                        # Check for the - solution
                        if self.description[int(tag['start']) - 1] == '-':
                            self.recognized_parts[-1]['text'] += '-%s' % tag['word']
                        else:
                            self.recognized_parts[-1]['text'] += ' %s' % tag['word']
                        self.recognized_parts[-1]['end'] = tag['end']
                skip = True

            ## Handle - cases
            if tag['entity_group'] != 'CARDINAL':
                if len(self.recognized_parts) > 0:
                    if self.recognized_parts[-1]['end'] == tag['start'] - 1:
                        if self.description[int(tag['start']) - 1] == '-':
                            self.recognized_parts[-1]['text'] += '-%s' % tag['word']
                            skip = True

            if not skip:
                finding['type'] = tag['entity_group']
                #finding['text'] = tag['word'].replace('##', '').replace(' - ', '-')
                finding['text'] = tag['word'].replace(' - ', '-')
                finding['start'] = tag['start']
                finding['end'] = tag['end']
                self.recognized_parts.append(finding)

        # Do the tagging
        for idx, part in enumerate(self.recognized_parts):
            supported_tag = part['type'] in SUPPORTED_TAGS
            # First part of the tags
            if idx == 0:
                self.address_object['tagged_text'] = self.description[0:part['start']]
                if supported_tag:
                    self.address_object['tagged_text'] += "[LOC-B]%s[LOC-E]" % part['text']
                else:
                    self.address_object['tagged_text'] += part['text']

            # Rest of the stuff
            if idx > 0 and idx + 1 <= len(self.recognized_parts):
                self.address_object['tagged_text'] += self.description[self.recognized_parts[idx-1]['end']:part['start']]
                if supported_tag:
                    self.address_object['tagged_text'] += "[LOC-B]%s[LOC-E]" % part['text']
                else:
                    self.address_object['tagged_text'] += part['text']

            # Last part of the tags
            if idx + 1 == len(self.recognized_parts):
                self.address_object['tagged_text'] += self.description[part['end']:]

            # Add part to the pages array
            if supported_tag:
                #move out from loop.
                #self.address_object['places'].append(part['text'])
                pass
            else:
                print("Not supported tag: %s %s" % (part['type'], part['text']))
        
        if address_maniplatior:
            self.address_object['tagged_text'] = address_maniplatior.fix_NER_errors(self.address_object['tagged_text'])
        #geather found locations from string to incorporate manipulations
        regex=re.compile(r"B\](.*?)\[L")
        self.address_object['places'] = regex.findall( self.address_object['tagged_text'] )


    def geocode_nominatim(self, preferred_postal_codes, address_maniplatior:AddressManipulations=None):
        geolocator = Nominatim(user_agent="Fortepan Photo GeoCoding Test")
        places = []

        for place in self.address_object['places']:
            location_object = {}
            
            full_address = place

            print("Processing address: ", full_address)
            # közterület név variációk eltávolítása
            if address_maniplatior:
                full_address = address_maniplatior.replace_public_places_variants(full_address)

            full_address = full_address.replace('utca', 'u.')

            # Ragtalanítás
            for rag in RAGOK:
                if full_address[-len(rag):] == rag:
                    full_address = full_address[:-len(rag)]

            if full_address.strip() not in BLACKLIST:
                # Try to locate
                try:
                    if self.district:
                        query = "%s%s, %s" % (self.city, self.district, full_address)
                    else:
                        query = "%s, %s" % (self.city, full_address)

                    location = geolocator.geocode(
                        query=query,
                        exactly_one=False,
                        limit=3,
                        addressdetails=True
                    )
                    time.sleep(0.5)
                except Exception:
                    print("Geocoder Error")
                    location = None

                if location:
                    add = False
                    for loc in location:
                        if 'postcode' in loc.raw['address']:
                            if loc.raw['address']['postcode'] in preferred_postal_codes:
                                add = True
                                loc_obj = loc
                                break
                        if 'city' in loc.raw['address']:
                            if loc.raw['address']['city'] == self.city:
                                add = True
                                loc_obj = loc
                                break
                        if 'town' in loc.raw['address']:
                            if loc.raw['address']['town'] == self.city:
                                add = True
                                loc_obj = loc
                                break
                        if 'village' in loc.raw['address']:
                            if loc.raw['address']['village'] == self.city:
                                add = True
                                loc_obj = loc
                                break

                    if add:
                        #location_object['original_address'] = "%s, %s" % (self.city, full_address)
                        location_object['original_address'] = query
                        location_object['geocoded_address'] = loc_obj.address
                        location_object['latitude'] = loc_obj.latitude
                        location_object['longitude'] = loc_obj.longitude
                        print("The Location is: ", location_object)
                else:
                    print("The Location not found: ", query)

            places.append(location_object)
        return places
