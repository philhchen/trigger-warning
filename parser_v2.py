import json
import os
import bz2
import collections
from langdetect import detect

from google.cloud import language
from google.cloud.language import enums
from google.cloud.language import types


ROOT_DIR = os.getcwd()
DATA_DIR = os.path.join(ROOT_DIR, 'data')

def construct_tweet_dict():
    tweet_dict = {}

    #load
    last_file = ""
    if (os.path.isfile('./saved_tweet_dict.json')):
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
                    lang = detect(tweet["text"])
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

    #setup
    CREDENTIALS = os.path.join(ROOT_DIR, "twitter-c62696ee4e94.json")
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = CREDENTIALS
    client = language.LanguageServiceClient()

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
        document = types.Document(content=tweet["comments"],type=enums.Document.Type.PLAIN_TEXT)
        try:
            analyzed = client.analyze_sentiment(document=document)
            sentiment_dict[id] = tweet
            score = analyzed.document_sentiment.score
            magnitude = analyzed.document_sentiment.magnitude
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
