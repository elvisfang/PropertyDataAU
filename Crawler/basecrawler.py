# -*- coding:UTF-8 -*-
"""
-------------------------------------------------
   File Name：     basecrawler.py
   Description :  base crawler class
   Author :       elvisfang
   date：          2017/7/27
-------------------------------------------------
   Change Activity:
                   2017/7/27:
-------------------------------------------------
"""
__author__ = 'elvisfang'
from Database import MongoDBClient
from urllib import request
from urllib import parse
from urllib import error
from bs4 import BeautifulSoup
from Log import logger


class BaseCrawler(object):

    __crawl_url = ''
    __proxy_enabled = False

    def __init__(self, crawl_url ='', proxy_enable=False):
        self.__crawl_url = crawl_url
        self.__proxy_enabled = proxy_enable

    @property
    def crawl_url(self):
        return self.__crawl_url

    @crawl_url.setter
    def crawl_url(self,url):
        self.__crawl_url = url

    @staticmethod
    def load_region_list(state):
        _mongoclient = MongoDBClient.MongodbClient('regions')
        _regionlist = _mongoclient.get_one_value_by_key({'state':state})
        _mongoclient.close_bd()
        return _regionlist['region']

    def crawl_data(self, **query_string):
        if self.__crawl_url == '':
            raise BaseException('__crawl_url of basecrawler is null')

        # User-Agent
        if self.__proxy_enabled:
            proxy = {'http': '113.121.188.81:808'}
            proxy_support = request.ProxyHandler(proxy)
            opener = request.build_opener(proxy_support)
            request.install_opener(opener)
        # define Head
        _head = {}
        _head['User-Agent'] = 'Mozilla/5.0 (Linux; Android 4.1.1; Nexus 7 Build/JRO03D) AppleWebKit/535.19 (KHTML, like Gecko) Chrome/18.0.1025.166  Safari/535.19'

        _target_req = request.Request(url=self.__crawl_url, headers=_head)
        try:
            if not query_string == {}:
                _search_data = parse.urlencode(query_string).encode('utf-8')
                _target_response = request.urlopen(_target_req, _search_data)
            else:
                _target_response = request.urlopen(_target_req)
        except error.HTTPError as e:
            logger.log_to_file('CrawlerError.log','Basecrawler HTTPError:' + e.code + ' processing:' + _target_req.full_url +'\n')
        except error.URLError as e:
            logger.log_to_file('CrawlerError.log','Basecrawler URLError:' + e.reason.strerror + ' processing:' + _target_req.full_url + '\n')
        else:
            _target_html = _target_response.read().decode('utf-8', 'ignore')
            # new BeautifulSoup object
            soup = BeautifulSoup(_target_html, 'lxml')
            return soup

if __name__ == "__main__":
    crawler = BaseCrawler('http://house.ksou.cn/p.php')
    Query_String = {}
    Query_String['q'] = 'Toorak'
    Query_String['p'] = '3'
    Query_String['s'] = 1
    Query_String['st'] = ''
    Query_String['type'] = ''
    Query_String['count'] = '300'
    Query_String['region'] = 'Toorak'
    Query_String['lat'] = '0'
    Query_String['lng'] = '0'
    Query_String['sta'] = 'vic'
    Query_String['htype'] = ''
    Query_String['agent'] = '0'
    Query_String['minprice'] = '0'
    Query_String['maxprice'] = '0'
    Query_String['minned'] = '0'
    Query_String['maxbed'] = '0'
    Query_String['minland'] = '0'
    Query_String['maxland'] = '0'
    s = crawler.crawl_data(**Query_String)
    print(s)
