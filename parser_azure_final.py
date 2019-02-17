import json
import os
import bz2
import collections
from langdetect import detect
import urllib.request

apiKey = '46ca12e9299d43d6969e541139265958'
sentimentUri = 'https://westus.api.cognitive.microsoft.com/text/analytics/v2.0/sentiment'
headers = {}
headers['Ocp-Apim-Subscription-Key'] = apiKey
headers['Content-Type'] = 'application/json'
headers['Accept'] = 'application/json'

ROOT_DIR = '/scratch/users/philhc'
DATA_DIR = os.path.join(ROOT_DIR, 'data')

def construct_tweet_dict():
    tweet_dict = {}

    #load
    last_file = ""
    if (os.path.isfile('saved_tweet_dict.json')):
        with open('saved_tweet_dict.json') as infile:
            saved_params = json.loads(infile.read())
            tweet_dict = saved_params["tweet_dict"]
            last_file = saved_params["last_file"]

    for subdir, dirs, files in os.walk(DATA_DIR):
        for file in files:
            filepath = subdir + os.sep + file
            if not (filepath.endswith(".bz2")):
                continue
            if (filepath <= last_file):
                continue
            source = bz2.BZ2File(filepath)
            for line in source:
                tweet = json.loads(line)
                if not ("text" in tweet and "quoted_status" in tweet):
                    continue
                try:
                    if not (detect(tweet["text"]) == "en"):
                        continue
                    parent_id = tweet["quoted_status"]["id_str"]
                    if not (parent_id in tweet_dict):
                        fields = {}
                        fields["num_comments"] = 0
                        fields["num_followers"] = tweet["quoted_status"]["user"]["followers_count"]
                        fields["text"] = tweet["quoted_status"]["text"]
                        fields["comments"] = ""
                        tweet_dict[parent_id] = fields
                    tweet_dict[parent_id]["comments"] += tweet["text"]
                    tweet_dict[parent_id]["num_comments"] += 1
                except:
                    pass

            # save after every file
            with open('saved_tweet_dict.json', 'w') as outfile:
                print("Completed: " + filepath)
                saved = {}
                saved["last_file"] = filepath
                saved["tweet_dict"] = tweet_dict
                json.dump(saved, outfile)

    with open('tweet_dict.json', 'w') as outfile:
        # order for ease of saving in calling Google Cloud
        ordered_tweets = collections.OrderedDict(sorted(tweet_dict.items()))
        json.dump(ordered_tweets, outfile)

def analyze_tweets():

    if not (os.path.isfile('./tweet_dict.json')):
        throw("No tweet_dict found.")


    #load previous sentiments
    sentiment_dict = collections.OrderedDict()
    last_tweet_id = "";
    if (os.path.isfile('./saved_sentiments.json')):
        with open('saved_sentiments.json', 'r') as infile:
            saved_params = json.loads(infile.read())
            sentiment_dict = saved_params["sentiment_dict"]
            last_tweet_id = saved_params["last_tweet_id"]

    #load tweet_dict
    tweet_dict = {}
    with open('./tweet_dict.json', 'r') as infile:
        tweet_dict = collections.OrderedDict(json.loads(infile.read())).items()

    iter = 0
    for (id, tweet) in tweet_dict:
        if (id <= last_tweet_id):
            continue
        iter += 1
        try:     
            list=[{"id":tweet['id_str'], "language":'en', "text":tweet['text']}]
            postData2 = json.dumps({"documents":list}).encode('utf-8')
            request2 = urllib.request.Request(sentimentUri, postData2, headers)
            response2 = urllib.request.urlopen(request2)
            response2json = json.loads(response2.read().decode('utf-8'))
            score = response2json['documents'][0]['score']
            
            sentiment_dict[id] = tweet
            magnitude = 1
            sentiment_dict[id]["sentiment_score"] = score
            sentiment_dict[id]["sentiment_magnitude"] = magnitude
            sentiment_dict[id]["sentiment"] = score * magnitude
        except:
            pass

        # save after every thousand
        if (iter % 100 == 0):
            print(iter)
            with open('saved_sentiments.json', 'w') as outfile:
                saved_params = {}
                saved_params["last_tweet_id"] = id
                saved_params["sentiment_dict"] = sentiment_dict
                json.dump(saved_params, outfile)

    with open('sentiments.json', 'w') as outfile:
        json.dump(sentiment_dict, outfile)

construct_tweet_dict()