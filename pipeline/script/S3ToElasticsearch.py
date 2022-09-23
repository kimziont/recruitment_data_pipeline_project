import json
import boto3
from datetime import datetime
from elasticsearch import Elasticsearch

access_key_id = 'AKIAUKJSSORFOCZGKI5K'
secret_access_key = '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'
bucket_name = 'ziontkim-recruitment-1'

s3 = boto3.resource('s3', aws_access_key_id=access_key_id, aws_secret_access_key=secret_access_key)
client = s3.meta.client
ES_URL = 'http://elasticsearch:9200'
ES_INDEX = 'recruitment_programmers'
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
            'Category': {'type': 'text'},
            'Title': {'type': 'text'},
            'Company': {'type': 'text'},
            'Position': {'type': 'text'},
            'EmploymentType': {'type': 'text'},
            'Experiences': {'type': 'text'},
            'Salary': {'type': 'long'},
            'Stacks': {'type': 'text', 'copy_to': 'my_all_field'},
            'Period': {'type': 'text'},
            'EmployeeNumber': {'type': 'long'},
            'WorkLocation': {'type': 'text'},
            'PrincipalServices': {'type': 'text'},
            'Description': {'type': 'text', 'copy_to': 'my_all_field'},
            'Requirements': {'type': 'text', 'copy_to': 'my_all_field'},
            'Preference': {'type': 'text', 'copy_to': 'my_all_field'},
            'Status': {'type': 'text'},
            'URL': {'type': 'text'},
            'Source': {'type': 'text'},
            'CreatedTime': {'type': 'date'},
            'LastModifiedTime': {'type': 'date'},
            'my_all_field': {'type': 'text'}
        }
        
    }
}

# 인덱스 생성
# es.indices.create(index=ES_INDEX, **index_settings)

# 인덱스 삭제
# es.indices.delete(index=ES_INDEX)
#  https://gonigoni.kr/posts/list-over-1000-files-from-s3/
paginator = client.get_paginator('list_objects_v2')

response_iterator = paginator.paginate(
    Bucket='ziontkim-recruitment-1',
    Prefix='programmers/'
)
# upsert되는지 테스트 해보고 싶을 때
# dict_data = {'Category': '데이터터터터터터터 엔지니어', 'Title': 'Data Scientist (데이터 사이언티스트)', 'Company': 'AB180', 'Position': '머신러닝, 인공지능(AI), 데이터 엔지니어', 'EmploymentType': 'Full-time', 'Experiences': 'All Backgrounds Welcome', 'EmployeeNumber': '101', 'PrincipalServices': '에어브릿지(Airbridge)', 'Period': 'Without deadline', 'WorkLocation': '서울 서초구 강남대로61길 17, (서초동, 밀라텔 쉐르빌)', 'Stacks': 'Python,R,Tensorflow,PyTorch,Scikit-Learn,SQL', 'Description': ['1억 대의 디바이스. 100만 RPM.', '하루 10억 건 이상의 이벤트 데이터.', '방대한 데이터로 비즈니스 문제를 함께 해결할', 'Data Scientist를 찾고 있어요!', 'AB180은 세계 각국에서하루 10억 건이 넘는 데이터를 받아 실시간으로 분석하고 있어요. Data Scientist는 이 데이터를 활용하여 광고 성과를 가장 정확하게 측정하고 극대화하기 위한 리서치를 진행하고, 광고 도메인에 적용하여 문제를 해결해요.', 'Airbridge Data Science Team이 개발한 Incrementality 분석 솔루션 더 알아보기 ', ' Key Experience', '기술적 경험', '하루에 수십 억 건 이상의 방대한 데이터를 활용한 머신러닝닝닝닝니인이닝닝니인잉닌인이니니ㅣ니ㅣ잉ㄴ 모델 및 인과추론 모델 개발 경험', '시계열 데이터를 활용한 머신러닝 알고리즘 개발 경험', 'AutoML을 이용하여 자동으로 최적의 모델을 찾는 알고리즘 개발 경험', '모델 배포, 모니터링, 개선 등 MLOps 경험', '데이터 웨어하우스 및 클라우드 인프라 등을 활용한 대규모 데이터 조작 경험', '비즈니스적 경험', '데이터 분석과 머신러닝 알고리즘을 통해 다양한 고객사의 광고 성과 개선에 실제로 기여하는 유의미한 프로덕트를 만드는 경험', '가장 가파르게 성장, 팽창하는 온라인 광고 시장에서의 도메인 지식 습득, 광고 성과 분석 경험', 'Meta, Google 등 글로벌 광고 파트너사들과의 협업 경험', ' 주요 업무', '광고의 인과적 효과를 추론하고 증분효과를 계산하는 인과추론 (Causal Inference) 모델 개발', '시계열 데이터 분석을 통한 광고 효과 측정 및 미래 광고 성과 예측 모델 개발', '최적 광고 예산 분배 알고리즘 개발', 'AutoML을 이용한 최적의 모델 설계 자동화', ' 팀의 기술', 'Tensorflow, Pytorch 등 딥러닝 프레임워크를 활용한 모델 개발', 'AWS, Snowflake, Airflow 등을 활용한 실서비스 운영', 'PySpark 를 활용한 대용량 데이터 분산 처리'], 'Requirements': ['통계, 머신러닝, 딥러닝 관련 전공자 또는 그에 준하는 배경 지식을 가지신 분', '영어 논문을 읽고 필요한 지식을 습득하여 서비스 개발에 적용하는 것이 가능하신 분', 'Python, R 등 데이터분석/모델 개발을 위한 프로그래밍 언어를 1개 이상 자유롭게 사용 가능하신 분', 'Tensorflow, PyTorch, scikitlearn 등 머신러닝 모델링 프레임워크를 사용한 서비스 구축 경험이 있으신 분', 'SQL을 활용한 필요한 데이터 추출 및 가공 작업이 가능하신 분'], 'Preference': ['통계, 머신러닝 기반의 인과추론 또는 Martech 관련 분야 모델링 경험이 있으신 분', 'Hadoop, Spark 등 빅데이터 분석 플랫폼을 활용한 대용량 데이터 분산 처리 경험이 있으신 분', 'Airflow, TFX 등을 활용한 머신러닝 모델 서빙 파이프라인 구축 경험이 있으신 분', 'AWS EMR, SageMaker 등 클라우드 서비스를 활용한 모델링 경험이 있으신 분', 'Snowflake, Databricks 등 데이터 웨어하우스 사용 경험이 있으신 분'], 'Status': 'In progress', 'CreatedTime': '22/7/8 14:15:16', 'LastModifiedTime': '22/7/8 14:15:16'}
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