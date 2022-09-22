import json
import time
import pymongo
from kafka import KafkaProducer

brokers = ["kafka:29092"]

for i in range(5):
    try:
        producer = KafkaProducer(bootstrap_servers = brokers)
        print(f'{i + 1}번 째 연결 성공')
        print(type(producer))
        break
    except:
        print(f'{i + 1}번 째 연결 실패')
else:
    print('Kafka를 연결할 수 없습니다')

topicName = "recruitmentProgrammers"

client = pymongo.MongoClient('mongodb://root:root@mongodb:27017')

db = client.get_database('recruitment')
collection = db.get_collection('programmers')

documents = collection.find({},{'_id': False})

for document in documents:
    producer.send(topicName, json.dumps(document).encode("utf-8"))
    # 이상하게 sleep(1) 이런식으로 쉬어줘야 잘 보내진다..
    time.sleep(1)