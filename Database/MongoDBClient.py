# coding: utf-8
"""
-------------------------------------------------
   File Name：     MongoDBClint.py
   Description :  client to do some operation towards mongodb
   Author :       elvisfang
   date：          2017/8/1
-------------------------------------------------
   Change Activity:
                   2017/8/1:
-------------------------------------------------
"""

__author__ = 'elvisfang'

from pymongo import MongoClient
from pymongo import errors
from Log import logger

class MongodbClient(object):
    __dbname = 'KsouData'
    __client = MongoClient('127.0.0.1', 27017)
    __collectionname = ''

    def __init__(self, collectionname,dbname ='KsouData',host='127.0.0.1', port='27017'):
        self.__dbname = dbname
        self.__collectionname = collectionname
        self.__client = MongoClient(host, int(port),connect=False)

    def get_collection_name(self):
        return self.__collectionname

    def set_collection_name(self, collectionname):
        self.__collectionname = collectionname

    def remove_all_from_collection(self,collectionname):
        try:
            if collectionname == ():
                collection = self.__client[self.__dbname][self.__collectionname]
            else:
                collection = self.__client[self.__dbname][collectionname]
            collection.remove({})
            return True
        except errors.PyMongoError as e:
            logger.log_to_file('MongoError.log', e.reason.strerror)
            self.__client.close()

    def get_one_value_by_key(self,filter,*collectionname):
        if not isinstance(filter,dict):
            raise TypeError('filter must be a dir with key:keyname')
        else:
            try:
                if collectionname == ():
                    collection = self.__client[self.__dbname][self.__collectionname]
                else:
                    collection = self.__client[self.__dbname][collectionname[0]]
                return collection.find_one(filter)
            except errors.PyMongoError as e:
                logger.log_to_file('MongoError.log', e.reason.strerror)
                self.__client.close()

    def update_one_record(self,keyfield,document,*collectionname):
        if not (isinstance(keyfield,dict) and isinstance(document,dict)):
            raise TypeError('keyself and document should be dict')
        else:
            try:
                if collectionname ==():
                    if self.__collectionname =='':
                        raise BaseException('colllection name should be set using set_collection_name')
                    else:
                        collection = self.__client[self.__dbname][self.__collectionname]
                else:
                    collection = self.__client[self.__dbname][collectionname[0]]
                collection.update(keyfield,
                                  {'$set':document},
                                  upsert=True,
                                  multi=True
                                  )
            except errors.PyMongoError as e:
                logger.log_to_file('MongoError.log', e.reason.strerror)
                self.__client.close()

    def return_random_record(self,collectionname):
        try:
            if collectionname == ():
                collection = self.__client[self.__dbname][self.__collectionname]
            else:
                collection = self.__client[self.__dbname][collectionname]
            return list(collection.aggregate([{'$sample':{'size':1}}])) #return a radmon cursor and convert to list
        except errors.PyMongoError as e:
            logger.log_to_file('MongoError.log', e.reason.strerror)
            self.__client.close()

    def close_bd(self):
        self.__client.close()

    def __del__(self):
        self.__client.close()

if __name__ == "__main__":
    db1 = MongodbClient('regions')
    s = db1.get_one_value_by_key({'state':'vic'})
    f = db1.get_one_value_by_key({'state':'vic'},'regions')
    print(s)
    print(f)