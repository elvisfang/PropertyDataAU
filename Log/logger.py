# coding: utf-8
"""
-------------------------------------------------
   File Name：     logger.py
   Description :  log file
   Author :       elvisfang
   date：          2017/8/2
-------------------------------------------------
   Change Activity:
                   2017/8/2:
-------------------------------------------------
"""

__author__ = 'elvisfang'

import time

def log_to_file(filename,str):
    _logfile = open(filename,'a',str,encoding='utf-8')
    _logfile.write(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) + ':' +str)
    _logfile.close()