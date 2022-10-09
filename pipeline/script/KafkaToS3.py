import json
import boto3
import configparser
from kafka import KafkaConsumer

parser = configparser.ConfigParser()
parser.read("/opt/pipeline/pipeline.ini")

access_key_id = parser.get("aws_boto_credentials", "access_key_id")
secret_access_key = parser.get("aws_boto_credentials", "secret_access_key")
bucket_name = parser.get("aws_boto_credentials", "bucket_name")
folder_name = parser.get("aws_boto_credentials", "folder_name")

s3 = boto3.resource('s3', aws_access_key_id=access_key_id, aws_secret_access_key=secret_access_key)

kafka_host = parser.get("kafka_credentials", "host")
kafka_port = parser.get("kafka_credentials", "port")
topicName = parser.get("kafka_credentials", "topic")
brokers = [f'{kafka_host}:{kafka_port}']

for i in range(5):
    try:
        consumer = KafkaConsumer(topicName, bootstrap_servers=brokers, group_id='1', auto_offset_reset='smallest', consumer_timeout_ms=30000)
        print(f'{i + 1}번 째 연결 성공')
        print(type(consumer))
        break
    except:
        print(f'{i + 1}번 째 연결 실패')
else:
    print('Kafka를 연결할 수 없습니다')

paginator = s3.meta.client.get_paginator('list_objects_v2')

response_iterator = paginator.paginate(
    Bucket=bucket_name,
    Prefix=folder_name
)

all_s3_objects = set()
for page in response_iterator:
    if 'Contents' in page:
        for content in page['Contents']:
            all_s3_objects.add(content['Key'])

for message in consumer:
    consumer.commit()
    row = json.loads(message.value.decode())
    # Kafka에서 S3로 저장
    row['Title'] = row['Title'].replace('/', '_')
    row['Company'] = row['Company'].replace('/', '_')
    file_name = folder_name + row['Company'] + row['Title'] + '.json'
    # 새로 크롤링된 데이터인 경우
    if file_name not in all_s3_objects:
        print(f"{file_name} is stored in S3")
        s3.meta.client.put_object(Body=json.dumps(row).encode("utf-8"),
                              Bucket=bucket_name,
                              Key=file_name)
    else:
        body = s3.meta.client.get_object(Bucket=bucket_name,
                                 Key=file_name)['Body']
        s3_data = json.loads(body.read().decode())
        # 수정/업데이트 된 경우
        if row['LastModifiedTime'] != s3_data['LastModifiedTime']:
            s3.meta.client.put_object(Body=json.dumps(row).encode("utf-8"),
                                  Bucket=bucket_name,
                                  Key=file_name)
consumer.close()
