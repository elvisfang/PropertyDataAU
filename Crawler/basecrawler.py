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
import time


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
        # _head['Accept'] = 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8'
        # _head['Accept-Encoding']= 'gzip, deflate'
        # _head['Accept-Language']='zh-CN,zh;q=0.8'
        # _head['Cache-Control']='max-age=0'
        # _head['Connection']='keep-alive'
        # _head['Host'] = 'house.ksou.cn'
        # _head['Upgrade-Insecure-Requests'] = '1'
        #_head['Cookie']='u=0815130798178353; __utmt=1; c_sta=vic; __utma=119194128.1000365510.1500881922.1502697441.1502761970.10; __utmb=119194128.22.10.1502761970; __utmc=119194128; __utmz=119194128.1500881923.1.1.utmcsr=(direct)|utmccn=(direct)|utmcmd=(none)'

        _target_req = request.Request(url=self.__crawl_url, headers=_head)
        _sleep = 200
        _loop = True
        _loop_counter = 0
        while(_loop) :
            try:
                if not query_string == {}:
                    _search_data = parse.urlencode(query_string).encode('utf-8')
                    _target_response = request.urlopen(_target_req, _search_data)
                else:
                    _target_response = request.urlopen(_target_req)
            except error.HTTPError as e:
                logger.log_to_file('CrawlerError.log','Basecrawler HTTPError:' + str(e.code) + ' processing:' + _target_req.full_url +'\n')
                if e.code== 503:
                    _loop_counter +=1
                    logger.log_to_file('CrawlerError.log', 'Basecrawler Sleep:' + str(_sleep) + 's processing:' + _target_req.full_url + '\n')
                    time.sleep(_sleep)
                    if _loop_counter >=10:
                        logger.log_to_file('CrawlerError.log','Basecrawler Error 503 >10 times')
                        break
                    continue
            except error.URLError as e:
                logger.log_to_file('CrawlerError.log','Basecrawler URLError:' + e.reason.strerror + ' processing:' + _target_req.full_url + '\n')
            else:
                _target_html = _target_response.read().decode('utf-8', 'ignore')
                # new BeautifulSoup object
                soup = BeautifulSoup(_target_html, 'lxml')
                if not isinstance(soup,BeautifulSoup):
                    _loop_counter +=1
                    logger.log_to_file('CrawlerError.log','Basecrawler Sleep:' + str(_sleep) + 's processing:' + _target_req.full_url + '\n')
                    time.sleep(_sleep)
                    if _loop_counter >=10:
                        logger.log_to_file('CrawlerError.log', 'Basecrawler Error no beautifulsoup >10 times')
                        break
                    continue
                else:
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
