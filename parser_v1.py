# -*- coding: utf-8 -*-
"""
Created on Sat Feb 16 13:05:22 2019

@author: Allan
"""

import json
import os
import bz2
import xlwt 
from langdetect import detect
from xlwt import Workbook 
  
# Workbook is created 
wb = Workbook() 
  
# add_sheet is used to create sheet. 
sheet1 = wb.add_sheet('Sheet 1') 


#filepath = "/Users/wangjinhui/Desktop/Stanford/Projects/twitter_analyzer/2018/10/01/00/29 2.json"

i=0
for subdir, dirs, files in os.walk("C:/Users/Allan/Desktop/twitter_analyzer/2017"):
    for file in files:
        #print os.path.join(subdir, file)
        filepath = subdir + os.sep + file

        if filepath.endswith(".bz2"):
            source = bz2.BZ2File(filepath)
            #data = bz2.decompress(source)
            for line in source:
                tweet=json.loads(line)
                if 'text' in tweet:
                    try:
                        if detect(tweet['text'])=='en':
                            sheet1.write(i,0,tweet['id_str'])
                            sheet1.write(i,1,tweet['text'])
                            sheet1.write(i,2,tweet['user']['followers_count'])
                            sheet1.write(i,3,tweet['user']["friends_count"])
                            sheet1.write(i,4,tweet['in_reply_to_user_id_str'])
                            
                            i=i+1
                    except:
                        pass
        wb.save('2017-11-01.xls') 