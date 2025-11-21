import time
from pprint import pprint
from elasticsearch import Elasticsearch

def get_es_client(max_retries: int=5, sleep_time: int=5) ->  Elasticsearch:
    i=0
    while i<max_retries:
        try:
            es = Elasticsearch("http://localhost:9200")
            client_info = es.info()
            pprint('Connected to Elasticsearch')
            pprint(f'Cluster info:\n{client_info}')
            return es
        except Exception:
            pprint('Could not connect to ElasticSearch, retrying...')
            time.sleep(sleep_time)
            i+=1
    raise ConnectionError('Failed to connect to elastic search after multiple times')

 
