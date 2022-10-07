import re
import json
import configparser
import boto3
import mysql.connector


parser = configparser.ConfigParser()
parser.read("/opt/pipeline/pipeline.ini")

access_key_id = parser.get("aws_boto_credentials", "access_key_id")
secret_access_key = parser.get("aws_boto_credentials", "secret_access_key")
bucket_name = parser.get("aws_boto_credentials", "bucket_name")
folder_name = parser.get("aws_boto_credentials", "folder_name")

s3 = boto3.resource('s3', aws_access_key_id=access_key_id, aws_secret_access_key=secret_access_key)
client = s3.meta.client
# S3에 저장된 파일 목록 읽어오기 (최대 1000개) -> 한계점 있음
# s3.meta.client.list_objects(Bucket=bucket_name)['Contents']

# 저장된 오브젝트 하나 가져오기
# target_object = s3.meta.client.list_objects(Bucket=bucket_name)['Contents'][0]
connector = mysql.connector.connect(
  host = parser.get("mysql_credentials", "host"),
  user = parser.get("mysql_credentials", "user"),
  passwd = parser.get("mysql_credentials", "passwd")
)

# preparing a cursor object
cursorObject = connector.cursor()

# 데이터베이스 생성
cursorObject.execute(f"CREATE DATABASE IF NOT EXISTS {parser.get('mysql_credentials', 'database')}")

cursorObject.execute(f"USE {parser.get('mysql_credentials', 'database')}")

# 테이블 생성
create_table = 'CREATE TABLE IF NOT EXISTS programmers (\
id VARCHAR(100) NOT NULL PRIMARY KEY,\
Category VARCHAR(20) NOT NULL,\
Company VARCHAR(20) NOT NULL,\
Source VARCHAR(20) NOT NULL,\
EmployeeNumber INT NULL,\
WorkLocation VARCHAR(100) NULL,\
Stacks VARCHAR(300) NULL,\
Status VARCHAR(10) NOT NULL,\
Salary INT NULL,\
CreatedTime DATETIME NOT NULL,\
LastModifiedTime DATETIME NOT NULL\
)'
cursorObject.execute(create_table)

create_table = 'CREATE TABLE IF NOT EXISTS skills (\
id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,\
post_id VARCHAR(100) NOT NULL,\
Skill VARCHAR(20) NOT NULL,\
FOREIGN KEY(post_id) REFERENCES programmers(id)\
)'
cursorObject.execute(create_table)


wish_attr_list = ['id', 'Category', 'Company', 'Source', 'EmployeeNumber', 'WorkLocation', 'Status', 'Salary', 'CreatedTime',  'LastModifiedTime']

def get_addr(x):
    x = x.replace("대한민국", "")
    x.strip()
    x = x.split()
    x = " ".join([x[0][:2]] + x[1:])
    try:
        if res := re.match('.*로|.*길|.*동', x).group():
            return res.strip()
    except:
        return x

cursorObject.execute("SELECT id FROM programmers")

id_set = set()
for d in cursorObject:
    id_set.add(d[0])


#  https://gonigoni.kr/posts/list-over-1000-files-from-s3/
paginator = client.get_paginator('list_objects_v2')

response_iterator = paginator.paginate(
    Bucket=bucket_name,
    Prefix=folder_name
)


for page in response_iterator:
    for content in page['Contents']:
        try:
            if content['Key'][-1] == "/":
                continue
            body = client.get_object(Bucket=bucket_name,
                                     Key=content['Key'])['Body']
            dict_data = json.loads(body.read().decode())
            dict_data['id'] = dict_data['Company'] + '_' + dict_data['Title']

            if 'Salary' in dict_data.keys():
                dict_data['Salary'] = int(dict_data['Salary'].split(" ")[0])

            if 'WorkLocation' in dict_data.keys():
                dict_data['WorkLocation'] = get_addr(dict_data['WorkLocation'])

            column_list = []
            for attr in wish_attr_list:
                if attr in dict_data.keys():
                    column_list.append(attr)

            table = 'programmers'
            columns = ", ".join(column_list)
            placeholders = ', '.join(['%s'] * len(column_list))


            # key는 회사이름_공고제목 으로 하고,
            # key값이 다르면 그냥 삽입,
            # key값이 같으면 LastModified 값 비교해서,
            # 그대로면 삽입X, 변했으면 업데이트
            if dict_data['id'] not in id_set:
                sql = "INSERT INTO %s ( %s ) VALUES ( %s )" % (table, columns, placeholders)
                cursorObject.execute(sql, [dict_data[col] for col in column_list])

                if 'Stacks' in dict_data and dict_data['Stacks'] is not None:
                    stack_list = dict_data['Stacks'].split(",")
                    for stack in stack_list:
                        cursorObject.execute(f"INSERT INTO skills ( post_id, Skill ) VALUES ( '{dict_data['id']}', '{stack}' )")
            else:
                cursorObject.execute(f"SELECT LastModifiedTime FROM programmers WHERE id={dict_data['id']}")
                last_modified_time = cursorObject.next()[0]
                if last_modified_time != dict_data['LastModifiedTime']:
                    sql = "INSERT INTO %s ( %s ) VALUES ( %s ) ON DUPLCATE KEY UPDATE" % (table, columns, placeholders)
                    cursorObject.execute(sql, [dict_data[col] for col in column_list])
        except:
            continue

connector.commit()
