import json
import configparser
import boto3
from datetime import datetime
import elasticsearch
from elasticsearch import Elasticsearch

parser = configparser.ConfigParser()
parser.read("/opt/pipeline/pipeline.ini")

access_key_id = parser.get("aws_boto_credentials", "access_key_id")
secret_access_key = parser.get("aws_boto_credentials", "secret_access_key")
bucket_name = parser.get("aws_boto_credentials", "bucket_name")
folder_name = parser.get("aws_boto_credentials", "folder_name")

s3 = boto3.resource('s3', aws_access_key_id=access_key_id, aws_secret_access_key=secret_access_key)
client = s3.meta.client

es_host = parser.get("elasticsearch_credentials", "es_host")
es_port = parser.get("elasticsearch_credentials", "es_port")
es_index = parser.get("elasticsearch_credentials", "es_index")

ES_URL = f'http://{es_host}:{es_port}'
ES_INDEX = es_index
DOC_TYPE = '_doc'

es = Elasticsearch(ES_URL)
# es.indices.delete(index=ES_INDEX)
index_settings = {
    'settings': {
        'number_of_shards': 2,
        'number_of_replicas': 1
    },
    'mappings': { 
        'properties': {
            'Category': {'type': 'text', 'copy_to': 'my_all_field'},
            'Title': {'type': 'text', 'copy_to': 'my_all_field'},
            'Company': {'type': 'text', 'copy_to': 'my_all_field'},
            'Position': {'type': 'text'},
            'EmploymentType': {'type': 'text', 'copy_to': 'my_all_field'},
            'Experiences': {'type': 'text', 'copy_to': 'my_all_field'},
            'Salary': {'type': 'long'},
            'Stacks': {'type': 'text', 'copy_to': 'my_all_field'},
            'Period': {'type': 'text'},
            'EmployeeNumber': {'type': 'long'},
            'WorkLocation': {'type': 'text', 'copy_to': 'my_all_field'},
            'PrincipalServices': {'type': 'text', 'copy_to': 'my_all_field'},
            'Description': {'type': 'text', 'copy_to': 'my_all_field'},
            'Requirements': {'type': 'text', 'copy_to': 'my_all_field'},
            'Preference': {'type': 'text', 'copy_to': 'my_all_field'},
            'Status': {'type': 'text', 'copy_to': 'my_all_field'},
            'URL': {'type': 'text'},
            'Source': {'type': 'text', 'copy_to': 'my_all_field'},
            'CreatedTime': {'type': 'date'},
            'LastModifiedTime': {'type': 'date'},
            'my_all_field': {'type': 'text'}
        }
        
    }
}

# 인덱스 생성
def es_create_index_if_not_exists(es, index, index_settings):
    """Create the given ElasticSearch index and ignore error if it already exists"""
    try:
        es.indices.create(index=index, **index_settings)
    except elasticsearch.exceptions.RequestError as ex:
        if ex.error == 'resource_already_exists_exception':
            pass # Index already exists. Ignore.
        else: # Other exception - raise it
            raise ex

es_create_index_if_not_exists(es, ES_INDEX, index_settings)


# 인덱스 삭제
# es.indices.delete(index=ES_INDEX)
#  https://gonigoni.kr/posts/list-over-1000-files-from-s3/
paginator = client.get_paginator('list_objects_v2')

response_iterator = paginator.paginate(
    Bucket=bucket_name,
    Prefix=folder_name
)

# https://elasticsearch-py.readthedocs.io/en/v8.3.2/api.html#elasticsearch.Elasticsearch.update
for page in response_iterator:
    for content in page['Contents']:
        print(f"{content['Key']}")
        try:
            if content['Key'][-1] == "/":
                continue
            body = client.get_object(Bucket=bucket_name,
                                     Key=content['Key'])['Body']
            dict_data = json.loads(body.read().decode())
            if 'Salary' in dict_data.keys():
                dict_data['Salary'] = int(dict_data['Salary'].split(" ")[0])
            else:
                dict_data['Salary'] = 0
            if 'Description' in dict_data.keys():
                dict_data['Description'] = " ".join(dict_data['Description'])
            if 'Requirements' in dict_data.keys():
                dict_data['Requirements'] = " ".join(dict_data['Requirements'])
            if 'Preference' in dict_data.keys():
                dict_data['Preference'] = " ".join(dict_data['Preference'])
            dict_data['CreatedTime'] = datetime.strptime(dict_data['CreatedTime'], '%y/%m/%d %H:%M:%S')
            dict_data['LastModifiedTime'] = datetime.strptime(dict_data['LastModifiedTime'], '%y/%m/%d %H:%M:%S')
            doc_id = dict_data['Company'] + '_' + dict_data['Title']
            es.update(index=ES_INDEX, id=doc_id, doc=dict_data, doc_as_upsert=True)
        except Exception as e:
            print(e)
            print(dict_data)
            break