import json
import os

from django.core.management import BaseCommand
import requests


DEFAULT_CITY = 'Budapest'
DEFAULT_DISTRICT = ' V.'
DEFAULT_MAX_RESULTS = 1000
MAX_RESULTS_PER_QERY = 1000

REQUEST_HEADERS = {
    #'content-type': 'application/json',
    #'Accept-Charset': 'UTF-8',
    #'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:130.0) Gecko/20100101 Firefox/130.0',
    #'Accept': '*/*',
    #'Accept-Language': 'en-US,en;q=0.5',
    'Accept-Encoding': 'gzip, deflate, br, zstd',
    'Referer': 'https://fortepan.hu/',
    'Authorization': 'Basic cmVhZGVyOnIzYWRtMzEwMjRyZWFk',
    'Content-Type': 'application/json;charset=UTF-8',
    'Origin': 'https://fortepan.hu',
    #'DNT': '1',
    #'Sec-GPC': '1',
    #'Connection': 'keep-alive',
    #'Sec-Fetch-Dest': 'empty',
    #'Sec-Fetch-Mode': 'cors',
    #'Sec-Fetch-Site': 'same-site',
    #'Priority': 'u=4',
    'Pragma': 'no-cache',
    'Cache-Control': 'no-cache',
    #'TE': 'trailers',
    }


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument("-m", "--max_results", type=int, default=DEFAULT_MAX_RESULTS)
        parser.add_argument("--city", type=str, default=DEFAULT_CITY + DEFAULT_DISTRICT)
        parser.add_argument("--out_file", type=str)

    
    def handle(self, *args, **options):
        if not options["out_file"]:
            filename = "FORTEPAN%s%d.json" % (options["city"], options["max_results"]) #TODO: Not safe!!
            options["out_file"] = filename
        
        print("getting " + str(options["max_results"]) + " entries for city: " + options["city"] + " into file: " + options["out_file"])

        results = self.get_fortepan_data(options["max_results"], options["city"])
        print( "Downloaded %d records" % len(results) )

        target_file = os.path.join(os.path.abspath(os.path.dirname(__file__)), options["out_file"])
        with open(target_file, "w", encoding='utf-8') as outfile:
            outfile.write(json.dumps(results, indent=4, ensure_ascii=False))
    
    def get_fortepan_data(self, max_results, city ):
        results = []

        while len(results) < max_results or max_results == 0:
            size_to_get = MAX_RESULTS_PER_QERY if max_results-len(results)>=MAX_RESULTS_PER_QERY else max_results-len(results)
            if max_results == 0:
                size_to_get = MAX_RESULTS_PER_QERY

            query = {
                "size": size_to_get,
                "sort": [
                    {
                        "mid": {
                            "order": "asc"
                        }
                    },
                    {
                        "_script": {
                            "type": "string",
                            "script": {
                                "lang": "painless",
                                "source": "DateTimeFormatter df = DateTimeFormatter.ofPattern(\'yyyy-MM-dd\'); return doc[\'created\'].size()==0 ? \'1970-01-01\' : df.format(doc[\'created\'].value);"
                            },
                            "order":"desc"
                        }
                    },
                    {
                        "mid": {
                            "order":"asc"
                        }
                    }
                ],
                "track_total_hits":True,
                "query": {
                    "bool": {
                        "must": [
                            {
                                "term": {
                                    "varos_search": city
                                }
                            },
                            {
                                "range": {
                                    "year": {
                                        "gt": 0
                                    }
                                }
                            }
                        ],
                        "should": [],
                        "must_not": []
                    }
                },
            }

            if len(results)>0:
                query["search_after"]=results[-1]['sort']

            url = 'https://elastic.fortepan.hu/elasticsearch_index_fortepandrupalmain_hd64t_media/_search?pretty'

            r = requests.post(url, json=query, headers=REQUEST_HEADERS)

            if 'hits' in r.json() and 'hits' in r.json()['hits']:
                results_count = len(r.json()['hits']['hits'])
                #print(results_count)
                results += r.json()['hits']['hits']
            else:
                break
            
            if results_count < MAX_RESULTS_PER_QERY:
                break

        return results


