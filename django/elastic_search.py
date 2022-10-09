import sys
import subprocess

try:
    from elasticsearch import Elasticsearch
except:
    subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'elasticsearch'])
    from elasticsearch import Elasticsearch

ES_URL = 'http://elasticsearch:9200'
ES_INDEX = 'recruitment_programmers'
DOC_TYPE = '_doc'

es = Elasticsearch(ES_URL)

def search(all_search, category, region, salary):
    company_list = []
    # query = {"query": { "match": { "my_all_field": all_search } }
    if all_search:
        request_body = {
            "size": 1000,
            "query": {
                "bool": {
                    "filter": [
                        {"match": {"my_all_field": all_search}},
                        {"match": {"Category": category}},
                        {"match": {"WorkLocation": region}},
                        {"range": { "Salary": {"gte": salary}},
                        }
                        ]},

            }
        }
    else:
        request_body = {
            "size": 1000,
            "query": {
                "bool": {
                    "filter": [
                        {"match": {"Category": category}},
                        {"match": {"WorkLocation": region}},
                        {"range": { "Salary": {"gte": salary}},
                        }
                        ]},

            }
        }
    res = es.search(body=request_body, index=ES_INDEX)

    for i in range(len(res.body['hits']['hits'])):
        record = res.body['hits']['hits'][i]['_source']
        print(record['Company'])
        company_list.append(record)
    
    
    return company_list