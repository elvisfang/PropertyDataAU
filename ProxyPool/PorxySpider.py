# -*- coding:UTF-8 -*-
"""
-------------------------------------------------
   File Name：     ProxySpider.py
   Description :   A Spider to get proxy ip:port form http://www.xicidaili.com/nn/
   Author :       elvisfang
   date：          2017/8/23
-------------------------------------------------
   Change Activity:
                   2017/8/23:
-------------------------------------------------
"""
__author__ = 'elvisfang'
from bs4 import BeautifulSoup
from Database import MongoDBClient
from Crawler import basecrawler
from Log import logger
import socket
import urllib
import urllib.request
import time

def IPspider(numpage):
    _url  = 'http://www.xicidaili.com/nn/'
    _crawler = basecrawler.BaseCrawler()
    #init the database IPPool
    _mongoclient = MongoDBClient.MongodbClient('IPPool')
    _mongoclient.remove_all_from_collection('IPPool')
    for num in range(1, numpage + 1):
        _ipurl = _url + str(num)
        print('Now downloading the ' + str(num * 100) + ' ips')
        _crawler.crawl_url = _ipurl
        _bs = _crawler.crawl_data()
        _res = _bs.find_all('tr')
        for item in _res:
            try:
                _tempip = {}
                _tds = item.find_all('td')
                if _tds:
                    if CheckProxy(_tds[5].text,_tds[1].text,_tds[2].text):
                        _tempip['IP'] = _tds[1].text
                        _tempip['Port'] = _tds[2].text
                        _tempip['Type']=_tds[5].text
                        _mongoclient.update_one_record({'IP': _tempip['IP']}, _tempip, 'IPPool')
            except BaseException as e:
                logger.log_to_file('ProxySpider.log','error when processing ' + _crawler.crawl_url + ' err: ' + str(e))

def CheckProxy(Type,IP,Port):
    #define socket timeout seconds
    socket.setdefaulttimeout(2)
    _proxy = IP + ':' + Port
    _proxy_handler = urllib.request.ProxyHandler({Type: _proxy})
    _opener = urllib.request.build_opener(_proxy_handler)
    urllib.request.install_opener(_opener)
    try:
        html = urllib.request.urlopen('http://house.ksou.cn')
    except Exception as e:
        return False
    else:
        return True

#return a random proxy ip from IP Pool
def GetRandomProxy():
    _mongoclient = MongoDBClient.MongodbClient('IPPool')
    try:
        _proxy = _mongoclient.return_random_record('IPPool')
    except BaseException as e:
        logger.log_to_file('ProxySpider.log', 'error when get random proxy ip' + 'err: ' + str(e))
    else:
        return _proxy[0]


if __name__ == '__main__':
    while(True):
        IPspider(1)
        time.sleep(60)
    #GetRandomProxy()