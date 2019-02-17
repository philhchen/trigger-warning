import wget
import time
import tarfile
import os
import sys
from collections import OrderedDict
import json
import bz2
from langdetect import detect

DATA_DIR = os.path.join(os.getcwd(), 'data')

def download_files(month):
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)

    # downloaded = [each for each in os.listdir(DATA_DIR) if each.endswith('.tar')]
    # if len(downloaded) > 0:
    #     last = max(downloaded)
    #     month = int(last.split("-")[2])
    #     day = int(last.split("-")[3][0:2])

    iter = 0
    for day in range(1,32):
        url = "https://archive.org/download/archiveteam-twitter-stream-2018-" + '{0:02d}'.format(month) + "/twitter-2018-" + '{0:02d}'.format(month) + "-" + '{0:02d}'.format(day) + ".tar"
        filename = os.path.basename(url)
        tries = 0
        while (tries < 3):
            try:
                filepath = os.path.join(DATA_DIR, filename)
                wget.download(url, filepath)
                path_to_extract = os.path.join(DATA_DIR, os.path.splitext(filename)[0])
                if not os.path.exists(path_to_extract):
                    os.makedirs(path_to_extract)
                try:
                    tar = tarfile.open(filepath, "r:")
                    tar.extractall(path = path_to_extract)
                    tar.close()
                    construct_tweet_dict(path_to_extract, month)
                except:
                    pass
                os.remove(filepath)
                break
            except:
                time.sleep(1)
                tries += 1
        iter += 1
        print(iter)
    print("Finished downloading!")


def construct_tweet_dict(path_to_extract, month):

    tweet_dict = OrderedDict()
    dict_file_name = 'tweet_dict' + str(month) + '.json'
    if os.path.isfile(dict_file_name):
        with open(dict_file_name, 'r') as infile:
            tweet_dict = json.loads(infile.read())

    for subdir, dirs, files in os.walk(path_to_extract):
        for file in files:
            filepath = subdir + os.sep + file
            if not (filepath.endswith(".bz2")):
                continue
            try:
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
            except:
                pass

    with open(dict_file_name, 'w') as outfile:
        # order for ease of saving in calling Google Cloud
        ordered_tweets = OrderedDict(sorted(tweet_dict.items()))
        json.dump(ordered_tweets, outfile)


construct_tweet_dict("/Users/wangjinhui/Desktop/Stanford/Projects/twitter_analyzer/test", 5)

# uncompress_files()
