# coding = utf-8
# -*- coding:utf-8 -*-
import json
import os
import re
import sys
import threading
import time
from concurrent.futures.process import ProcessPoolExecutor
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

proxy_pool_url = 'http://127.0.0.1:5010/get'

NUM = 16
CONN = RedisClient('ccgp', 'd_uuid')

pool = redis.ConnectionPool(host = 'localhost', port = 6379, db = 1, password = '')
r_pool = redis.StrictRedis(connection_pool = pool, charset = 'UTF-8', errors = 'strict', decode_responses = True,
                           unix_socket_path = None)
r_pipe = r_pool.pipeline( )

Base_URL = 'http://www.ccgp.gov.cn/oss/download?'
Base_DIR = './download/'


class downloader( ):
    def __init__(self):

        self.temp_size = 0
        self.total_size = 0

        self.headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': 'en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7',
            'Cache-Control': 'max-age=0',
            'Connection': 'keep-alive',
            # 'Content-Length': '227',
            # 'Content-Type': 'application/x-www-form-urlencoded',
            'DNT': '1',
            'Host': 'www.ccgp.gov.cn',
            'Range': 'bytes=%d-' % self.temp_size,
            # 'Origin': 'http://htgs.ccgp.gov.cn',
            # 'Referer': 'http://htgs.ccgp.gov.cn/GS8/contractpublish/search',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.92 Safari/537.36'
        }
        self.uuid = None
        self.data = {
            'uuid': self.uuid
        }
        self.url = Base_URL + urlencode(self.data)
        self.key = None
        self.key_list = CONN.usernames( )
        self.key_num = CONN.count()
        self.uuid_list = CONN.get_alval( )
        self.mime = None
        self.filepath = None

    def get_proxy(self):
        try:
            response = requests.get(proxy_pool_url)
            if response.status_code == 200:
                proxy_url_content = response.content
                encoding = chardet.detect(proxy_url_content)
                proxy_url_context = proxy_url_content.decode(encoding['encoding'], 'ignore')
                proxy_url_context1 = eval(proxy_url_context)
                proxy_url = proxy_url_context1.get('proxy')
                print(proxy_url)
                return proxy_url
        except ConnectionError:
            print('[ERROR]Connection timeout error...')

    def mime_judge(self, res):
        try:
            response = res.headers['Content-Disposition']
            pattern = re.compile(r'\.(.*?\S$)')
            r = pattern.findall(response)
            self.mime = r[0]
            # print(r)
            # print(self.mime)
            return True
        except IndexError as e:
            print(e)
            print('[ERROR]check mime error...')
            return False

    def page_req(self, url):
        global proxy
        try:
            print(url)
            print("Requsting Pages...")
            proxy = self.get_proxy( )
            proxies = {
                'http': 'http://' + proxy
            }
            print(proxies)
            ses = requests.Session( )
            res = ses.get(url = url, timeout = 10, proxies = proxies)
            # mime = self.mime_judge(res)
            # encoding = chardet.detect(res.content)
            # html = res.content.decode(encoding['encoding'], 'ignore')
            print('return html....')
            # print(html)
            # return html
            return res
        except ConnectionError:
            print('Connection timeout...')

    def size_judge(self, res):
        try:
            self.total_size = int(res.headers['content-length'])
            # print(self.total_size)
        except Exception as e:
            print(e)
            print('[ERROR]check total_size error...')

    def check_size(self):
        try:
            if os.path.exists(self.filepath):
                self.temp_size = os.path.getsize(self.filepath)
                # print(self.temp_size)
            else:
                self.temp_size = 0
        except Exception as e:
            print(e)
            print('[ERROR]check temp_size error...')

    def file_dl_manager(self, rs):
        with open(self.filepath, 'ab') as f:
            start = time.time( )
            for chunk in rs.iter_content(chunk_size = 1024):
                if chunk:
                    self.temp_size += len(chunk)
                    f.write(chunk)
                    f.flush( )
                    done = int(50 * self.temp_size / self.total_size)
                    sys.stdout.write(
                        "\r[%s%s] %d%%" % (
                            '█' * done, ' ' * (50 - done), 100 * self.temp_size / self.total_size))
                    sys.stdout.flush( )
            print( )
            end = time.time( )
            print('Finish in: ' + str(end - start) + 's')

    def downloador(self):
        try:
            # print(self.temp_size / self.total_size)
            if self.temp_size is not None and int(self.temp_size / self.total_size) is not 1:
                self.temp_size = 0
                res = requests.Session( )
                rs = res.get(url = self.url, stream = True)
                if os.path.exists(self.filepath):
                    os.remove(self.filepath)
                    self.file_dl_manager(rs)
                else:
                    self.file_dl_manager(rs)
            else:
                print("File Already been downloaded...Passing")
                pass
        except WindowsError as e:
            print(e)
            print('[ERROR]WinError error, failed to check...')
            pass

    def filepath_generate(self, r):
        try:
            if self.mime_judge(r):
                self.filepath = Base_DIR + self.key + '.' + self.mime
                # print(self.filepath)
            else:
                self.filepath = Base_DIR + self.key
                # print(self.filepath)
        except Exception as e:
            print(e)
            print('[ERROR]filepath set error...')

    def file_download(self):
        global proxy
        try:
            print("Requsting Pages...")
            proxy = self.get_proxy( )
            proxies = {
                'http': 'http://' + proxy
            }
            # print(proxies)
            self.data.update(uuid = self.uuid)
            self.url = Base_URL + urlencode(self.data)
            print(self.url)
            res = requests.Session( )
            r = res.head(self.url)
            # print(r.headers)
            # print(self.url)
            self.size_judge(r)
            # print(self.total_size)
            self.filepath_generate(r)
            # print(self.filepath)
            self.check_size( )
            # print(self.temp_size)
            self.downloador( )
            # if mime != None:
            #     rs = res.get(self.url, stream = True)
            #     f = open('./download/' + self.key + '.' + mime, 'wb')
            #     start = time.time( )
            #     for chunk in rs.iter_content(chunk_size = 1024):
            #         if chunk:
            #             f.write(chunk)
            #             f.flush( )
            #     end = time.time( )
            #     print('Finish in: ', end - start)
            # else:
            #     rs = res.get(self.url, stream = True)
            #     f = open('./download/' + self.key, 'wb')
            #     start = time.time( )
            #     for chunk in rs.iter_content(chunk_size = 1024):
            #         if chunk:
            #             f.write(chunk)
            #             f.flush( )
            #     end = time.time( )
            #     print('Finish in: ', end - start)
        except TimeoutError as e:
            print(e)
            print('[ERROR]Proxy Connection Timouterror...')
            self.file_download( )

    def parallel_download(self, key_list):
        try:
            for i in range(self.key_num):
                self.key = self.key_list[i]
                self.uuid = CONN.get(self.key)
                print(self.key)
                # print(self.uuid)
                self.file_download( )
        except Exception as e:
            print(e)

    def job(self):
        with ThreadPoolExecutor(max_workers = 1) as executor:
            executor.map(self.parallel_download, self.key_list)

dl = downloader( )
dl.job()
