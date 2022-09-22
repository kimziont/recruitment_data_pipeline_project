import json
import boto3
from kafka import KafkaConsumer

access_key_id = 'AKIAUKJSSORFOCZGKI5K'
secret_access_key = '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'
bucket_name = 'ziontkim-recruitment-1'
folder_name = 'programmers/'
s3 = boto3.resource('s3', aws_access_key_id=access_key_id, aws_secret_access_key=secret_access_key)

topicName = 'recruitmentProgrammers'
brokers = ['kafka:29092']

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
    Bucket='ziontkim-recruitment-1',
    Prefix='programmers/'
)

all_s3_objects = set()
for page in response_iterator:
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
