from lib2to3.pgen2.parse import Parser
import re
import time
import configparser
from pytz import timezone
from datetime import datetime
import pymongo
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup


chrome_options = Options()
chrome_options.add_argument('--headless')
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--disable-dev-shm-usage')

path = '/usr/local/lib/python3.8/site-packages/chromedriver/usr/bin/chromedriver'
driver = webdriver.Chrome(executable_path=path, chrome_options=chrome_options)
driver.get('https://programmers.co.kr/job')


parser = configparser.ConfigParser()
parser.read("/opt/pipeline/pipeline.ini")

host = parser["mongodb_credentials"]["host"]
port = parser.get("mongodb_credentials", "port")
user = parser.get("mongodb_credentials", "user")
passwd = parser.get("mongodb_credentials", "passwd")
database = parser.get("mongodb_credentials", "database")
collection = parser.get("mongodb_credentials", "collection")

client = pymongo.MongoClient(f'mongodb://{user}:{passwd}@{host}:{port}')

db = client.get_database(database)
collection = db.get_collection(collection)


crawling_set = set()
for i in range(8, 9):

    
    # 직무 클릭  /html/body/div[3]/div/section[1]/div/div[2]/div[1]/button
    job_category_button = driver.find_element(by=By.XPATH,value="/html/body/div[3]/div/section[1]/div/div[2]/div[1]/button")
    job_category_button.click()
    time.sleep(1)
    
    # 포지션 선택 /html/body/div[2]/div/section[1]/div/div[2]/div[1]/div/ul/li[8]/label
    i_th_job_category_xpath = f'/html/body/div[3]/div/section[1]/div/div[2]/div[1]/div/ul/li[{i}]/label'
    i_th_job_category = driver.find_element(by=By.XPATH, value=i_th_job_category_xpath)
    i_th_job_category.click()
    time.sleep(1)
    position_text = i_th_job_category.text
    
    # 경력 클릭
    career_xpath = '/html/body/div[3]/div/section[1]/div/div[3]/div[1]/div[1]/button'
    driver.find_element(by=By.XPATH, value=career_xpath).click()
    time.sleep(1)
    
    # 신입 선택
    newbie_xpath = '/html/body/div[3]/div/section[1]/div/div[3]/div[1]/div[1]/div/div/div/div[2]/label'
    driver.find_element(by=By.XPATH, value=newbie_xpath).click()
    time.sleep(1)

    # 페이지 돈다
    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')
    
    
    page = 1
    last_page_num = int(soup.find_all(class_='page-link')[-2].text.strip())
    
    

    print(last_page_num)
    for cur_page in range(last_page_num):
        print(f'-----{cur_page + 1}번 째 페이지 크롤링중----------------------------')
        # 현재 페이지 저장해두기
        prev_url = driver.current_url
        
        html = driver.page_source
        soup = BeautifulSoup(html, 'html.parser')
        

        position_list = [p.text.strip() for p in soup.find_all(class_='position-link')]
        company_list = [c.text.strip() for c in soup.find_all(class_='company-link')]
        company_list = list(filter(lambda x: len(x), company_list))
        
        post_id_list = [c + "_" + p for c,p in zip(company_list, position_list)]
        
        for post_id in  post_id_list:
            crawling_set.add(post_id)

        print(post_id_list)
        
        # 아래 회사 리스트 for문 돌면서 크롤링 len(position_list) + 1
        for j in range(1, len(position_list) + 1):
            row_data = dict()
            row_data['Category'] = position_text
            try:
                j_th_position_xpath = f'/html/body/div[3]/div/section[2]/div/ul/li[{j}]/div[2]/div[1]/h5/a'
                driver.find_element(by=By.XPATH, value=j_th_position_xpath).click()
            except:
                print(f"{page}페이지, {j}번째 글을 읽어오지 못했습니다")
                continue
            time.sleep(2)


            html = driver.page_source
            soup = BeautifulSoup(html, 'html.parser')
            
            if title := soup.select_one(".position-show").select_one(".title").text.strip():
                row_data['Title'] = title
            
            if company := soup.select_one(".position-show").select_one(".sub-title").text.strip():
                row_data['Company'] = company
            
            row_data['URL'] = driver.current_url
            row_data['Source'] = 'programmers'
            
            row_data['_id'] = row_data['Company'] + '_' + row_data['Title']
            crawling_set.add(row_data['_id'])
        
            if summary := soup.select_one(".position-show").select_one(".section-summary"):
                label_list = summary.find_all(class_='t-label')
                value_list = summary.find_all(class_='t-content')
                for label, value in zip(label_list, value_list):
                    if label.text.strip() == "사원수":
                        row_data['EmployeeNumber'] = value.text.strip()[:-1].strip()
                    else:
                        label = label.text.split(" ")
                        label = "".join(list(map(lambda x: x.capitalize(), label))).strip()
                        row_data[label] = value.text.strip()
        
            if stacks := soup.select_one(".position-show").select_one(".section-stacks"):
                stack_list = stacks.find_all(class_='_3w5q5pj0-cKLdyuMSZY5ES _1rWv2ZoV6KRiA6VmGgEqZd')
                row_data['Stacks'] = ",".join([stack.get_text(strip=True).replace("\xa0", "") for stack in stack_list])
            
            if description:= soup.select_one(".content-body.col-item.col-xs-12.col-sm-12.col-md-12.col-lg-8")\
                                            .select_one(".section-position")\
                                            .select_one(".markdown.github.markdown-viewer").text:

                d = re.sub(r'[^\w\d\n,.!/()[\]{} ]', "", description)
                d = re.split(r'[\n]', d)

                row_data['Description'] = list(filter(lambda x: len(x), d))
            
            if requirements := soup.select_one(".content-body.col-item.col-xs-12.col-sm-12.col-md-12.col-lg-8")\
                                .select_one(".section-requirements")\
                                .select_one(".markdown.github.markdown-viewer").text:

                r = re.sub(r'[^\w\d\n,.!/()[\]{} ]', "", requirements)
                r = re.split(r'[\n]', r)

                row_data['Requirements'] = list(filter(lambda x: len(x), r))

            if preference := soup.select_one(".content-body.col-item.col-xs-12.col-sm-12.col-md-12.col-lg-8")\
                                            .select_one(".section-preference")\
                                            .select_one(".markdown.github.markdown-viewer").text:

                p = re.sub(r'[^\w\d\n,.!/()[\]{} ]', "", preference)
                p = re.split(r'[\n]', p)

                row_data['Preference'] = list(filter(lambda x: len(x), p))
                
                row_data['Status'] = 'In progress'
            
            # Insert
            if not collection.find_one({'_id': row_data['_id']}):
                row_data['CreatedTime'] = datetime.now(timezone('Asia/Seoul')).strftime("%y/%m/%d %H:%M:%S")
                row_data['LastModifiedTime'] = row_data['CreatedTime']
                collection.insert_one(row_data)
            # Replace (값의 일부(Requirements)를 확인하여 변경사항 있다면 아예 새로운 데이터로 바꾼다
            # Update 쓰면 $set 이런식으로 해줘야 해서 불편하다
            else:
                db_data = collection.find_one({'_id': row_data['_id']})
                if row_data['Requirements'] != db_data['Requirements']:
                    row_data['CreatedTime'] = db_data['CreatedTime']
                    row_data['LastModifiedTime'] = datetime.now(timezone('Asia/Seoul')).strftime("%y/%m/%d %H:%M:%S")
                    collection.replace_one({'_id': row_data['_id']}, row_data)
            
            
             
            # 뒤로가기
            driver.get(prev_url)
            time.sleep(1)
            
        
        if last_page_num >= 7:
            pagination = 9
        else:
            pagination = last_page_num + 2
        
        if next_page := driver.find_element(by=By.XPATH, value=f'/html/body/div[3]/div/div[3]/ul/li[{pagination}]/span'):
            page += 1
            try:
                next_page.click()
                print(f'{page}페이지로 이동합니다')
                time.sleep(1)
            except:
                break
        else:
            print("다음 페이지가 없습니다")
            break
# 마갑된 채용 공고 Status 변경하기 (In progree -> Closed)
for doc in collection.find():
    if doc['_id'] not in crawling_set:
        collection.find_one_and_update({'_id': doc['_id']}, {'$set' :{'Status': 'Closed'}})