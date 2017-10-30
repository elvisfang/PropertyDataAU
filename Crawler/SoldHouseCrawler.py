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

import basecrawler
import time
from Database import MongoDBClient
from bs4 import BeautifulSoup
import re
from Log import logger

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
            raise TypeError('bs must be bs4.BeautifulSoup, now: ' + type(bs))

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
            _house_info['SoldDate'] = detail_tag.find(text=re.compile('Sold')).parent.next_sibling[3:].replace('(Auction)','').strip()
        else:
            _house_info['SoldDate'] = 'null'
        # Get Last Sold Price sample " $1,505,000 in Oct 1997"
        if detail_tag.find(text=re.compile('Last Sold')):
            _sl = detail_tag.find(text=re.compile('Last Sold')).parent.next_sibling
            _house_info['LastSoldPrice'] = _sl.split('in')[0].strip()[1:]
            _house_info['LastSoldDate'] = _sl.split('in')[1].replace('(Auction)','').strip()
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
            _house_info['RentPrice'] = _rp.split('in')[0].strip()[1:-2]
            _house_info['RentDate'] = _rp.split('in')[1].strip()
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
            _house_info['LandSize'] = detail_tag.find(text=re.compile('Land size:')).parent.next_sibling.split('sqm')[0].strip()
            if _house_info['LandSize'] == '':
                _house_info['LandSize'] = 'null'
        else:
            _house_info['LandSize'] = 'null'
        # get building size
        if detail_tag.find(text=re.compile('Building size:')):
            _house_info['BuildingSize'] = detail_tag.find(text=re.compile('Building size:')).parent.next_sibling.split('sqm')[0].strip()
            if _house_info['BuildingSize'] == '':
                _house_info['BuildingSize'] = 'null'
        else:
            _house_info['BuildingSize'] = 'null'
        # get Build Year
        if detail_tag.find(text=re.compile('Build year:')):
            _house_info['BuildYear'] = detail_tag.find(text=re.compile('Build year:')).parent.next_sibling
        else:
            _house_info['BuildYear'] = 'null'
        # Get Agent Name
        if detail_tag.find(text=re.compile('Agent')):
            # <td><b>Agent:</b> <a href="http://www.ksouhouse.com/agent.php?id=21225&amp;name=Rodney+Morley+Pty+Ltd+-" title="View more about this realestate agent">Rodney Morley Pty Ltd -</a></td>
            if detail_tag.find(text=re.compile('Agent')).parent.parent.find('a'):
                _house_info['Agent'] = detail_tag.find(text=re.compile('Agent')).parent.parent.a.string.strip()
            else:  # <td><b>Agent:</b> hockingstuart  Armadale</td>
                _house_info['Agent'] = detail_tag.find(text=re.compile('Agent')).parent.next_sibling.strip()
        else:
            _house_info['Agent'] = 'null'
        # get distance to cbd sample 5.3 km to CBD; 825 metres to Heyington Station, unit meters
        if detail_tag.find(text=re.compile('Distance')):
            _dist = detail_tag.find(text=re.compile('Distance')).parent.next_sibling
            _house_info['Distance2CBD'] = _dist.split(';')[0].split('to')[0].strip()
            _house_info['Distance2Stat'] = _dist.split(';')[1].split('to')[0].strip()
        else:
            _house_info['Distance2CBD'] = 'null'
            _house_info['Distance2Stat'] = 'null'

        #return one house info
        return _house_info

    def crawl_sold_house(self,state,mode='CONTINUE',excluderegion=''):
        _region_list = self.__crawler.load_region_list(state)
        _excludelist = excluderegion
        #create a new crawler to fro detail data
        _crawler = basecrawler.BaseCrawler()
        #-------------------
        # set both crawler proxy enabled
        _crawler.proxy_enabled = True
        self.__crawler.proxy_enabled = True
        #------------------
        #new collction for detail property
        _mongoclient = MongoDBClient.MongodbClient('PropertyDetails')
        for _region in _region_list:
            if _region in _excludelist:
                continue
            for i in range(30):
                _query = self.__generate_query_string(_region,i,_region,state)
                #_bs_searchresult = self.__crawler.crawl_data(**_query)
                _bs_searchresult = self.__crawler.requests_crawl_data(**_query)
                for addr in _bs_searchresult.find_all('span', class_='addr'):
                    _crawler.crawl_url = self.__crawl_url + addr.a.get('href')[5:]
                    try:
                        if mode == 'FULL' or \
                                (mode == 'CONTINUE' and (not _mongoclient.get_one_value_by_key({'URL':_crawler.crawl_url}))):
                            #_bs_detailinfo = _crawler.crawl_data()
                            _bs_detailinfo = _crawler.requests_crawl_data()
                            _house_data = self.__absctract_house_info(_bs_detailinfo)
                            _house_data['State'] = state
                            _house_data['Region'] = _region
                            _house_data['URL'] = self.__crawl_url + addr.a.get('href')[5:]
                            #save data to mongodb
                            _mongoclient.update_one_record({'Addr':_house_data['Addr']},_house_data,'PropertyDetails')
                            # sleep 2 second
                            time.sleep(2)
                            print('save data:' + _house_data['URL'])
                        else:
                            print(_crawler.crawl_url + 'existed')
                    except BaseException as e:
                        logger.log_to_file('SoldHouseCrawler.log', 'error when processing '+ _crawler.crawl_url +'err: ' + str(e))
                #time.sleep(10)
        _mongoclient.close_bd()


if __name__ =='__main__':
    _crawler1 = SoldhouseCrawler()
    _crawler1.crawl_sold_house('vic',mode='FULL')
    #TODO exclude regions if 300 entries are existed in CONTINUE Mode, and how to process crawler in different mode
    #TODO using proxy and change IP address when error occures