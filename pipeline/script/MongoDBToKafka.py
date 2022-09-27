import json
import time
import configparser
import pymongo
from kafka import KafkaProducer

parser = configparser.ConfigParser()
parser.read("/opt/pipeline/pipeline.ini")

kafka_host = parser.get("kafka_credentials", "host")
kafka_port = parser.get("kafka_credentials", "port")
topicName = parser.get("kafka_credentials", "topic")
brokers = [f'{kafka_host}:{kafka_port}']

for i in range(5):
    try:
        producer = KafkaProducer(bootstrap_servers = brokers)
        print(f'{i + 1}번 째 연결 성공')
        break
    except:
        print(f'{i + 1}번 째 연결 실패')
else:
    print('Kafka를 연결할 수 없습니다')

host = parser.get("mongodb_credentials", "host")
port = parser.get("mongodb_credentials", "port")
user = parser.get("mongodb_credentials", "user")
passwd = parser.get("mongodb_credentials", "passwd")
database = parser.get("mongodb_credentials", "database")
collection = parser.get("mongodb_credentials", "collection")

client = pymongo.MongoClient(f'mongodb://{user}:{passwd}@{host}:{port}')

db = client.get_database(database)
collection = db.get_collection(collection)

documents = collection.find({},{'_id': False})

for document in documents:
    producer.send(topicName, json.dumps(document).encode("utf-8"))
    # 이상하게 sleep(1) 이런식으로 쉬어줘야 잘 보내진다..
    time.sleep(1)