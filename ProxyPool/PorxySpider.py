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

def IPspider(numpage):
    _url  = 'http://www.xicidaili.com/nn/'
    _crawler = basecrawler.BaseCrawler()
    _mongoclient = MongoDBClient.MongodbClient('IPPool')
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
                _tempip['IP'] = _tds[1].text  # .text.encode('utf-8'))
                _tempip['Port'] = _tds[2].text  # .text.encode('utf-8'))
                _mongoclient.update_one_record({'IP': _tempip['IP']}, _tempip, 'IPPool')
            except BaseException as e:
                logger.log_to_file('ProxySpider.log','error when processing ' + _crawler.crawl_url + 'err: ' + str(e))

if __name__ == '__main__':
    IPspider(1)