from collections import deque
import requests
import bs4
from bs4 import BeautifulSoup
import json
import time
from selenium import webdriver
import pymysql
import numpy as np


def getPage(mid, href, n=1):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:76.0) Gecko/20100101 Firefox/76.0',
        'Accept': '*/*',
        'Accept-Language': 'zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2',
        'Connection': 'keep-alive',
        'Referer': href+'/fans/fans',
    }
    params = (
        ('vmid', str(mid)),
        ('pn', str(n)),
        ('ps', '50'),
        ('order', 'desc'),
    )
    
    my = []

    response = requests.get(
        'https://api.bilibili.com/x/relation/followers', headers=headers, params=params)
    json_obj = json.loads(response.text)  # 返回json格式
    try:
        for entry in json_obj['data']['list']:
            fans_mid = entry['mid']
            insertUser(mid, fans_mid)
            my.append(fans_mid)
    except:
        print("插入失败")
            

    # time.sleep(5)  # 防封ip

    response = requests.get('https://api.bilibili.com/x/relation/followings', headers=headers, params=params)
    json_obj = json.loads(response.text)  # 返回json格式
    try:
        for entry in json_obj['data']['list']:
            followID = entry['mid']
            insertUser(mid=followID, fanID=mid)
    except:
        print("插入失败")
 
    return my


def getUserDetails(mid):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:76.0) Gecko/20100101 Firefox/76.0',
        'Accept': 'application/json, text/plain, */*',
        'Accept-Language': 'zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2',
        'Origin': 'https://space.bilibili.com',
        'Connection': 'keep-alive',
        'Referer': 'https://space.bilibili.com/546195/fans/fans',
        'Cache-Control': 'max-age=0',
    }
    params = (
        ('mid', str(mid)),
        ('jsonp', 'jsonp'),
    )
    response = requests.get(
        'https://api.bilibili.com/x/space/acc/info', headers=headers, params=params)
    return response


def BFS(level, start_id):
    id_list = deque()
    id_list.append(start_id)
    href_head = "https://space.bilibili.com/"
    layer = 0

    # 层次遍历
    while(len(id_list) > 0 and layer < level):
        print(id_list)
        list_size = len(id_list)

        for i in range(list_size):
            mid = id_list.popleft()

            userDetails = getUserDetails(mid)
            json_obj = json.loads(userDetails.text)
            name = json_obj['data']['name']
            sex = json_obj['data']['sex']
            userlevel = json_obj['data']['level']

            following = 0
            follower = 0
            try:
                res = requests.get(
                    'https://api.bilibili.com/x/relation/stat?vmid=' + str(mid) + '&jsonp=jsonp').text
                js_fans_data = json.loads(res)
                following = js_fans_data['data']['following']
                follower = js_fans_data['data']['follower']
            except:
                following = 0
                follower = 0

            insertUserData(mid, name, sex, following, follower, userlevel)
            time.sleep(5)

            fans_list = getPage(mid, href_head+str(mid))
            id_list.extend(fans_list)
            time.sleep(5)  # 防止封ip

        layer = layer + 1


def insertUser(mid, fanID):
    db = pymysql.connect(host='localhost', user='root', password='123456',
                         port=3306, db='bilibili')
    cursor = db.cursor()
    sql = '''
            insert into user_fans (mid,fanid) select %s,%s from DUAL where NOT EXISTS
            (select mid from user_fans where mid = %s and fanid = %s);
            '''

    val = (mid, fanID, mid, fanID)
    try:
        cursor.execute(sql, val)
        db.commit()
    except:
        db. rollback()
    db.close()


def insertUserData(mid, name, sex, following, follower, level):
    db = pymysql.connect(host='localhost', user='root', password='123456',
                         port=3306, db='bilibili')
    cursor = db.cursor()
    sql = 'INSERT ignore INTO userdata(mid,name,sex,following,follower,level) values(%s,%s,%s,%s,%s,%s)'
    val = (mid, name, sex, following, follower, level)
    try:
        cursor.execute(sql, val)
        db.commit()
    except:
        db. rollback()
    db.close()


if __name__ == "__main__":
    BFS(level=7, start_id=208259)
