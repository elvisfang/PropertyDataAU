# -*- coding:UTF-8 -*-
"""
-------------------------------------------------
   File Name：     SoldHouseCrawler.py
   Description :   to crawler sold house from http://house.ksou.cn/p.php
   Author :       elvisfang
   date：          2017/8/2
-------------------------------------------------
   Change Activity:
                   2017/8/2:
-------------------------------------------------
"""
__author__ = 'elvisfang'

from . import basecrawler
from bs4 import BeautifulSoup
import re

class SoldhouseCrawler():

    __crawl_url = 'http://house.ksou.cn/p.php'
    __porxy_enabled = False

    def __init__(self, proxy_enable=False):
        self.__proxy_enabled = proxy_enable
        self.__crawler = basecrawler.BaseCrawler(self.__crawl_url,self.__proxy_enabled)

    #generate the query string of the search data for http://house.ksou.cn/p.php
    def __generate_query_string(self,query,page,region,state):
        Query_String = {}
        Query_String['q'] = query
        Query_String['p'] = page
        Query_String['s'] = 1
        Query_String['st'] = ''
        Query_String['type'] = ''
        Query_String['count'] = '300'
        Query_String['region'] = region
        Query_String['lat'] = '0'
        Query_String['lng'] = '0'
        Query_String['sta'] = state
        Query_String['htype'] = ''
        Query_String['agent'] = '0'
        Query_String['minprice'] = '0'
        Query_String['maxprice'] = '0'
        Query_String['minned'] = '0'
        Query_String['maxbed'] = '0'
        Query_String['minland'] = '0'
        Query_String['maxland'] = '0'
        return Query_String

    def __absctract_house_info(self,bs):
        if not isinstance(bs,BeautifulSoup):
            raise TypeError('bs must be bs4.BeautifulSoup')

        _house_info = {}
        addr_tag = bs.find('span', class_='addr')
        detail_tag = addr_tag.parent.parent.next_sibling
        # find detail info in the currnet page

        # Get Address sample "37 Clendon Road, Toorak"
        _house_info['Addr'] = addr_tag.text.split(',')[0]

        # Get Sold Price sample Sold $8,790,000 unit AU dollar
        if detail_tag.find(text=re.compile('Sold')):
            _house_info['SoldPrice'] = detail_tag.find(text=re.compile('Sold'))[6:]
        else:
            _house_info['SoldPrice'] = 'null'
        # Get Sold Date sample in Jun 2017(Auction)
        if detail_tag.find(text=re.compile('Sold')):
            _house_info['SoldDate'] = detail_tag.find(text=re.compile('Sold')).parent.next_sibling[3:].replace('(Auction)',
                                                                                                          '')[:-1]
        else:
            _house_info['SoldDate'] = 'null'
        # Get Last Sold Price sample " $1,505,000 in Oct 1997"
        if detail_tag.find(text=re.compile('Last Sold')):
            _sl = detail_tag.find(text=re.compile('Last Sold')).parent.next_sibling
            _house_info['LastSoldPrice'] = _sl.split('in')[0][2:-1]
            _house_info['LastSoldDate'] = _sl.split('in')[1][1:].replace('(Auction)', '')
        else:
            _house_info['LastSoldPrice'] = 'null'
            _house_info['LastSoldDate'] = 'null'
        # Get Rent Price
        if detail_tag.find(text=re.compile('Rent')):
            if detail_tag.find(text=re.compile('Rent')).parent.parent.find('a'):
                _rp = detail_tag.find(text=re.compile('Rent')).parent.parent.a.string  # with Rent link
            else:
                _rp = detail_tag.find(
                    text=re.compile('Rent')).parent.next_sibling  # <td><b>Rent</b> $1,150pw in Jun 2014</td>
            _house_info['RentPrice'] = _rp.split('in')[0][1:-3]
            _house_info['RentDate'] = _rp.split('in')[1][1:]
        else:
            _house_info['RentPrice'] = 'null'
            _house_info['RentDate'] = 'null'
        # get property type
        if detail_tag.find(text=re.compile('Apartment|Unit|House')):
            _house_info['Type'] = detail_tag.find(text=re.compile('Apartment|Unit|House'))[:-1]
        else:
            _house_info['Type'] = 'null'
        # get Bed Room Number
        if detail_tag.find(title='Bed rooms'):
            _house_info['BedRoom'] = detail_tag.find(title='Bed rooms').previous_sibling
        else:
            _house_info['BedRoom'] = '0'
        # get Bath Room Number
        if detail_tag.find(title='Bath rooms'):
            _house_info['BathRoom'] = detail_tag.find(title='Bath rooms').previous_sibling
        else:
            _house_info['BathRoom'] = '0'
        # Get car space
        if detail_tag.find(title='Car spaces'):
            _house_info['CarSpace'] = detail_tag.find(title='Car spaces').previous_sibling
        else:
            _house_info['CarSpace'] = '0'
        # Get Land Size
        if detail_tag.find(text=re.compile('Land size:')):
            _house_info['LandSize'] = detail_tag.find(text=re.compile('Land size:')).parent.next_sibling[:-4]
            if _house_info['LandSize'] == '':
                _house_info['LandSize'] = 'null'
        else:
            _house_info['LandSize'] = 'null'
        # get Build Year
        if detail_tag.find(text=re.compile('Build year:')):
            _house_info['BuildYear'] = detail_tag.find(text=re.compile('Build year:')).parent.next_sibling
        else:
            _house_info['BuildYear'] = 'null'
        # Get Agent Name
        if detail_tag.find(text=re.compile('Agent')):
            # <td><b>Agent:</b> <a href="http://www.ksouhouse.com/agent.php?id=21225&amp;name=Rodney+Morley+Pty+Ltd+-" title="View more about this realestate agent">Rodney Morley Pty Ltd -</a></td>
            if detail_tag.find(text=re.compile('Agent')).parent.parent.find('a'):
                _house_info['Agent'] = detail_tag.find(text=re.compile('Agent')).parent.parent.a.string
            else:  # <td><b>Agent:</b> hockingstuart  Armadale</td>
                _house_info['Agent'] = detail_tag.find(text=re.compile('Agent')).parent.next_sibling
        else:
            _house_info['Agent'] = 'null'
        # get distance to cbd sample 5.3 km to CBD; 825 metres to Heyington Station, unit meters
        if detail_tag.find(text=re.compile('Distance')):
            _dist = detail_tag.find(text=re.compile('Distance')).parent.next_sibling
            _house_info['Distance2CBD'] = _dist.split(';')[0].split('to')[0][:-1]
            _house_info['Distance2Stat'] = _dist.split(';')[1].split('to')[0][:-1]
        else:
            _house_info['Distance2CBD'] = 'null'
            _house_info['Distance2Stat'] = 'null'


    def crawl_sold_house(self,state):
        _region_list = self.__crawler.load_region_list(state)
        _crawler = basecrawler.BaseCrawler()
        for _region in _region_list:
            for i in range(30):
                _query = self.__generate_query_string(_region,i,_region,state)
                _bs_searchresult = self.__crawler.crawl_data(**_query)
                for addr in _bs_searchresult.find_all('span', class_='addr'):
                    _crawler.crawl_url = addr.a.get('href')[5:]
                    _bs_detailinfo = _crawler.crawl_data()



