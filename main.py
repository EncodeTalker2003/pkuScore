import requests
import random
import json
from email.mime.text import MIMEText
from email.header import Header
import time
import yaml
import urllib.parse
import urllib.request

with open('config.yaml', 'r', encoding='utf-8') as f:
    config = yaml.safe_load(f)
    key = config['sendkey']

def get_score(xnd, xq):
    print("[INFO] 正在获取成绩信息")
    s = requests.Session()
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',  
        'Referer': 'https://portal.pku.edu.cn/', 
    }
    login_url = 'https://iaaa.pku.edu.cn/iaaa/oauthlogin.do'
    form_data = {
        'appid': 'portal2017',
        'userName': str(config['user']['userName']),
        'password': str(config['user']['password']),
        'redirUrl': 'https://portal.pku.edu.cn/portal2017/ssoLogin.do'
    }
    res = s.post(login_url, headers=headers, data=form_data)
    try:
        token = res.json()["token"]
    except:
        print(res.text)
    res = s.get(f"https://portal.pku.edu.cn/portal2017/ssoLogin.do?_rand={random.random()}&token={token}")
    url = 'https://portal.pku.edu.cn/portal2017/bizcenter/score/retrScores.do'
    response = s.get(url, headers=headers).content
    res_dict = json.loads(response)
    term_course_list = list(filter(lambda x: x["xnd"] == xnd and x["xq"] == xq, res_dict["cjxx"]))
    print("[INFO] 成绩信息获取成功")
    if not term_course_list:
        print("[INFO] No course in this term.")
        return []
    return term_course_list[0]["list"]

def inform(course):
    title = f"新成绩通知: {course['kcmc']}"
    text = f"课程分数: {course['xqcj']}"
    if course['jd']:
        text += f", 绩点: {course['jd']}"
    print("[INFO] 消息标题: ", title)
    print("[INFO] 消息内容: ", text)
    postdata = urllib.parse.urlencode({'text': title, 'desp': text}).encode('utf-8')
    url = f'https://sctapi.ftqq.com/{key}.send'
    req = urllib.request.Request(url, data=postdata, method='POST')
    with urllib.request.urlopen(req) as response:
        result = response.read().decode('utf-8')
    return result

def main():
    konwn_courses_id = []
    cnt = 0
    year = config['year']
    term = str(config['term'])
    
    while True:
        cnt += 1
        print(f"[INFO] 进行第{cnt}次轮询")
        cur_courses = get_score(year, term)
        new_courses = []
        for course in cur_courses:
            if course["kch"] not in konwn_courses_id:
                new_courses.append(course)
                konwn_courses_id.append(course["kch"])
        
        if new_courses:
            for course in new_courses:
                inform(course)
        else:
            print("No new courses.")

        print(f"[INFO] 等待{config['interval']}秒后进行下一次轮询")
        time.sleep(config['interval'])
        
if __name__ == '__main__':
    main()