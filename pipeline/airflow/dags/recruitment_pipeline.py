import json
from datetime import datetime
from airflow import DAG
from airflow.operators.bash import BashOperator

default_args = {
    'start_date': datetime(2022, 7, 19)
}

with DAG(dag_id='recruitment-airflow',
        schedule_interval='@daily',
        default_args=default_args,
        tags=['recruitment'],
        catchup=False) as dag:
    crawling = BashOperator(
        task_id='crawling',
        bash_command='python /opt/pipeline/script/crawlingToMongo.py'
    )
    MongoDBToKafka = BashOperator(
        task_id='MongoDBToKafka',
        bash_command='python /opt/pipeline/script/MongoDBToKafka.py'
    )
    KafkaToS3 = BashOperator(
        task_id='KafkaToS3',
        bash_command='python /opt/pipeline/script/KafkaToS3.py'
    )
    S3ToElasticsearch = BashOperator(
        task_id='S3ToElasticsearch',
        bash_command='python /opt/pipeline/script/S3ToElasticsearch.py'
    )
    S3ToMySQL = BashOperator(
        task_id='S3ToMySQL',
        bash_command='python /opt/pipeline/script/S3ToMySQL.py'
    )

    crawling >> MongoDBToKafka >> KafkaToS3 >> [S3ToElasticsearch, S3ToMySQL]