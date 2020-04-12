# coding = utf-8
# -*- coding:utf-8 -*-
import json
import os
import re
import threading
import time
from urllib.parse import urlencode

import bs4 as bs4
import chardet
# from fake_useragent import UserAgent
import redis
import requests
from pyquery import PyQuery as pq
from data_saver import RedisClient

CONN = RedisClient('ccgp', 'd_link')
CONN1 = RedisClient('ccgp', 'filter_link')
CONN2 = RedisClient('ccgp', 'd_uuid')
URL = 'http://htgs.ccgp.gov.cn/GS8/contractpublish/detail/2c8382aa5513c90301551589cd7c0224?contractSign=0'
URL_LIST = CONN1.scan()

# URL = 'http://htgs.ccgp.gov.cn/GS8/contractpublish/detail/2c8382a96dcec594016e8cc65d0458e2?contractSign=0'


#
# Headers = {
#     'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
#     'Accept-Encoding': 'gzip, deflate',
#     'Accept-Language': 'en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7',
#     'Cache-Control': 'max-age=0',
#     'Connection': 'keep-alive',
#     'Content-Length': '227',
#     'Content-Type': 'application/x-www-form-urlencoded',
#     'DNT': '1',
#     'Host': 'htgs.ccgp.gov.cn',
#     'Origin': 'http://htgs.ccgp.gov.cn',
#     'Referer': 'http://htgs.ccgp.gov.cn/GS8/contractpublish/search',
#     'Upgrade-Insecure-Requests': '1',
#     'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.92 Safari/537.36'
# }
#
# DATA = {
#     'codeResult': 'bf903b3ff4056dd512f7d22a2936912a',
#     'searchContractCode': None,
#     'searchContractName': None,
#     'searchProjCode': None,
#     'searchProjName': None,
#     'searchPurchaserName': None,
#     'searchSupplyName': None,
#     'searchAgentName': None,
#     'searchPlacardStartDate': None,
#     'searchPlacardEndDate': None,
#     'code': '9w6s'
# }


class reqpager( ):
    def __init__(self):
        self.data = None
        # self.headers = Headers
        # self.data = DATA

    def page_req(self, url):
        try:
            print(url)
            print("Requsting Pages...")
            ses = requests.Session( )
            res = ses.post(url = url, timeout = 10)
            encoding = chardet.detect(res.content)
            html = res.content.decode(encoding['encoding'], 'ignore')
            print('return html....')
            # print(html)
            return html
        except ConnectionError:
            print('Connection timeout...')

    def parse_page(self, content):
        doc = pq(content)
        context = doc('tr td').text()
        cs = context.split( )
        jsonarr = json.dumps(cs, ensure_ascii = False)
        print(cs)
        print(type(cs))
        print(jsonarr)
        # info = context.items()
        # print(info)
        # for i in info:
        #     print(i)
        # print(context)
        # info = doc('.fileInfo div a')
        # print(info)
        # for i in info.items( ):
        #     if i.attr('onclick') != None:
        #         # print(i.attr('onclick'))
        #         t = i.attr('onclick')
        #         pattern = re.compile(r"'(\S.*?-.*?-.*?\S)',")
        #         r = pattern.findall(str(t))
        #         # CONN2.set('')
        #         print(r)
        #     else:
        #         print('[ERROR]uuid requirment failed.')


rq = reqpager( )
# for url in URL_LIST:
ct = rq.page_req(URL)
rq.parse_page(ct)
