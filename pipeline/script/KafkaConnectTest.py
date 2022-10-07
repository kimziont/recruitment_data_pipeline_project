import configparser
from kafka import KafkaConsumer, KafkaProducer

parser = configparser.ConfigParser()
parser.read("/opt/pipeline/pipeline.ini")

kafka_host = parser.get("kafka_credentials", "host")
kafka_port = parser.get("kafka_credentials", "port")
topicName = parser.get("kafka_credentials", "topic")
brokers = [f'{kafka_host}:{kafka_port}']

for i in range(5):
    try:
        producer = KafkaProducer(bootstrap_servers = brokers)
        consumer = KafkaConsumer(topicName, bootstrap_servers=brokers, group_id='1')
        print(f'{i + 1}번 째 연결 성공')
        break
    except:
        print(f'{i + 1}번 째 연결 실패')
else:
    assert producer is not None
    assert consumer is not None
    print('Kafka를 연결할 수 없습니다')