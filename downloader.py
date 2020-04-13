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

Headers = {
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

DATA = {
    'uuid': None
}

Base_URL = 'http://www.ccgp.gov.cn/oss/download?'


class downloader():
    def __init__(self):
        self.headers = Headers
        self.data = DATA
        self.url = Base_URL+urlencode(self.data)

    def mime_judge(self,res):
        response = res.headers['Content-Disposition']
        pattern = re.compile(r'\.(.*?\S$)')
        r = pattern.findall(response)
        print(r[0])
        return r[0]

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
            res = requests.Session()
            r = res.head(self.url)
            mime = self.mime_judge(r)
            rs = res.get(self.url, stream = True)
            f = open('./download/3.'+mime, 'wb')
            start = time.time()
            for chunk in rs.iter_content(chunk_size = 1024):
                if chunk:
                    f.write(chunk)
                    f.flush()
            end = time.time()
            print('Finish in: ', end-start)
        except Exception as e:
            print(e)




dl = downloader()
dl.file_download()