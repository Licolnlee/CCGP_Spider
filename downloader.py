# coding = utf-8
# -*- coding:utf-8 -*-
import json
import os
import re
import threading
import time
from urllib.parse import urlencode
from urllib.request import urlopen, Request

import bs4 as bs4
import chardet
# from fake_useragent import UserAgent
import redis
import requests
from pyquery import PyQuery as pq
from data_saver import RedisClient
from concurrent.futures.thread import ThreadPoolExecutor
NUM = 16
CONN = RedisClient('ccgp', 'd_uuid')

pool = redis.ConnectionPool(host = 'localhost', port = 6379, db = 1, password = '')
r_pool = redis.StrictRedis(connection_pool = pool, charset = 'UTF-8', errors = 'strict', decode_responses = True,
                           unix_socket_path = None)
r_pipe = r_pool.pipeline( )

Base_URL = 'http://www.ccgp.gov.cn/oss/download?'


class downloader():
    def __init__(self):

        self.headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': 'en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7',
            'Cache-Control': 'max-age=0',
            'Connection': 'keep-alive',
            'Content-Length': '227',
            'Content-Type': 'application/x-www-form-urlencoded',
            'DNT': '1',
            'Host': 'htgs.ccgp.gov.cn',
            'Origin': 'http://htgs.ccgp.gov.cn',
            'Referer': 'http://htgs.ccgp.gov.cn/GS8/contractpublish/search',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.92 Safari/537.36'
        }
        self.uuid = None
        self.data = {
            'uuid': self.uuid
        }
        # self.url = 'http://www.ccgp.gov.cn/oss/download?' + urlencode(self.data)
        self.url = None
        self.key = None
        self.key_list = CONN.usernames()
        self.uuid_list = CONN.get_alval()

    def mime_judge(self,res):
        try:
            response = res.headers['Content-Disposition']
            pattern = re.compile(r'\.(.*?\S$)')
            r = pattern.findall(response)
            # print(r)
            print(r[0])
            return r[0]
        except IndexError as e:
            return None

    def get_range(self, total):
        ranges = []
        offset = int(total / NUM)
        for i in range(NUM):
            if i == NUM - 1:
                ranges.append((i * offset, ''))
            else:
                ranges.append((i * offset, (i + 1) * offset))
        return ranges

    def page_req(self, url):
        try:
            print(url)
            print("Requsting Pages...")
            ses = requests.Session( )
            res = ses.get(url = url, timeout = 10)
            # mime = self.mime_judge(res)
            # encoding = chardet.detect(res.content)
            # html = res.content.decode(encoding['encoding'], 'ignore')
            print('return html....')
            # print(html)
            # return html
            return res
        except ConnectionError:
            print('Connection timeout...')

    def file_download(self):
        try:
            self.data.update(uuid = self.uuid)
            self.url = Base_URL+urlencode(self.data)
            res = requests.Session()
            r = res.head(self.url)
            print(self.url)
            mime = self.mime_judge(r)
            if mime != None:
                rs = res.get(self.url, stream = True)
                f = open('./download/'+self.key+'.'+mime, 'wb')
                start = time.time()
                for chunk in rs.iter_content(chunk_size = 1024):
                    if chunk:
                        f.write(chunk)
                        f.flush()
                end = time.time()
                print('Finish in: ', end-start)
            else:
                rs = res.get(self.url, stream = True)
                f = open('./download/' + self.key, 'wb')
                start = time.time( )
                for chunk in rs.iter_content(chunk_size = 1024):
                    if chunk:
                        f.write(chunk)
                        f.flush( )
                end = time.time( )
                print('Finish in: ', end - start)
        except Exception as e:
            print(e)

    def parallel_download(self):
        try:
            for i in range(2):
                self.key = self.key_list[i]
                self.uuid = CONN.get(self.key)
                self.file_download()
                print(self.key)
                print(self.uuid)
        except Exception as e:
            print(e)



dl = downloader()
dl.parallel_download()