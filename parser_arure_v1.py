# -*- coding: utf-8 -*-
"""
Created on Sat Feb 16 12:25:32 2019

@author: Allan
"""

import json
import os
import bz2
import urllib.request
from langdetect import detect

apiKey = '46ca12e9299d43d6969e541139265958'
sentimentUri = 'https://westus.api.cognitive.microsoft.com/text/analytics/v2.0/sentiment'
headers = {}
headers['Ocp-Apim-Subscription-Key'] = apiKey
headers['Content-Type'] = 'application/json'
headers['Accept'] = 'application/json'

tweet_dict = {}


for subdir, dirs, files in os.walk("C:/Users/Allan/Desktop/twitter_analyzer/2017"):
    for file in files:
        #print os.path.join(subdir, file)
        filepath = subdir + os.sep + file

        if filepath.endswith(".bz2"):
            source = bz2.BZ2File(filepath)
            #data = bz2.decompress(source)
            for line in source:
                tweet = json.loads(line)
                if not ("text" in tweet):
                    continue
                if "quoted_status" in tweet:
                    parent_id = tweet["quoted_status"]["id_str"]
                    try:
                        if (detect(tweet['text']) == "en"):
                            if not (parent_id in tweet_dict):
                                fields = {};
                                fields["mean_sentiment"] = 0;
                                fields["num_sentiment"] = 0;
                                fields["num_followers"] = tweet["quoted_status"]["user"]["followers_count"]
                                fields["num_friends"] = tweet["quoted_status"]["user"]["friends_count"]
                                fields["text"] = tweet["quoted_status"]["text"]
                                tweet_dict[parent_id] = fields;
                            list=[{"id":tweet['id_str'], "language":'en', "text":tweet['text']}]
                            postData2 = json.dumps({"documents":list}).encode('utf-8')
                            request2 = urllib.request.Request(sentimentUri, postData2, headers)
                            response2 = urllib.request.urlopen(request2)
                            response2json = json.loads(response2.read().decode('utf-8'))
                            score = response2json['documents'][0]['score']
                            prev_size = tweet_dict[parent_id]["num_sentiment"]
                            prev_mean = tweet_dict[parent_id]["mean_sentiment"]
                            tweet_dict[parent_id]["mean_sentiment"] = (prev_mean * prev_size + score) / (prev_size + 1)
                            tweet_dict[parent_id]["num_sentiment"] += 1
                    except:
                        pass
        print("finished file")

with open('data.json', 'w') as outfile:
    json.dump(tweet_dict, outfile)
