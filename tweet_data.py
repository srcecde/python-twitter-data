"""
-*- coding: utf-8 -*-
========================
Python Twitter Data Scrap using API
========================
Developed by: Chirag Rathod (Srce Cde)
Email: chiragr83@gmail.com
========================
"""
from tweepy import OAuthHandler
from tweepy import API, Cursor
import argparse
import pandas as pd
import matplotlib.pyplot as plt
import time
import json

plt.style.use("ggplot")

class TwitterData():

    def __init__(self):
        self.api_key = ''
        self.api_secret = ''
        self.access_token = ''
        self.access_token_secret = ''

    def get_auth(self):
        authentication = OAuthHandler(self.api_key, self.api_secret)
        authentication.set_access_token(self.access_token, self.access_token_secret)
        api = API(authentication)
        return api

    def get_data(self, username):
        api_access = self.get_auth()
        get_data = api_access.lookup_users(screen_names=[username])
        for user in get_data:
            with open('user_data.txt', 'w') as f:
                f.write("Screen Name: " + str(user.screen_name) + "\n")
                f.write("Name: " + str(user.name) + "\n")
                f.write("Description: " + str(user.description) + "\n")
                f.write("User URL: " + str(user.url) + "\n")
                f.write("Cover Image URL: " + str(user.profile_banner_url) + "\n")
                f.write("Profile Image URL: " + str(user.profile_image_url) + "\n")
                f.write("Followers Count: " + str(user.followers_count) + "\n")
                f.write("Following Count: " + str(user.friends_count) + "\n")
                f.write("Status Count: " + str(user.statuses_count) + "\n")
                f.write("Likes Count: " + str(user.favourites_count) + "\n")

    def plot_graph(self, typ, title, x_title, y_title, top_n=5):

        tweet_type = typ.value_counts()
        fig, ax = plt.subplots()
        ax.set_xlabel(x_title)
        ax.set_ylabel(y_title)
        ax.set_title(title)
        tweet_type[:top_n].plot(ax=ax, kind='bar')
        plt.show()

    def extract_trending_data(self, hash_tag):
        api_access = self.get_auth()
        data = Cursor(api_access.search, q=hash_tag).items(800)
        trend_data = []
        log_tweets = str(time.time()) + '_moztweets.txt'
        with open(log_tweets, 'w') as outfile:
            for tweet in data:
                trend_data.append(json.loads(json.dumps(tweet._json)))
                outfile.write(json.dumps(tweet._json))
                outfile.write("\n")

        tweets = pd.DataFrame()

        tweets['created_at'] = list(map(
            lambda tweet: time.strftime('%Y-%m-%d %H:%M:%S',
                                        time.strptime(tweet['created_at'], '%a %b %d %H:%M:%S +0000 %Y')),
            trend_data))
        tweets['user'] = list(map(lambda tweet: tweet['user']['screen_name'], trend_data))
        tweets['user_followers_count'] = list(map(lambda tweet: tweet['user']['followers_count'], trend_data))
        tweets['text'] = list(map(lambda tweet: tweet['text'].encode('utf-8'), trend_data))
        tweets['lang'] = list(map(lambda tweet: tweet['lang'], trend_data))
        tweets['Location'] = list(
            map(lambda tweet: tweet['place']['country'] if tweet['place'] != None else None, trend_data))
        tweets['retweet_count'] = list(map(lambda tweet: tweet['retweet_count'], trend_data))
        tweets['favorite_count'] = list(map(lambda tweet: tweet['favorite_count'], trend_data))

        list_of_original_tweets = [element.decode('utf-8') for element in tweets['text'].values if
                                   not element.decode('utf-8').startswith('RT')]

        print("Number of Real Tweets : ", len(list_of_original_tweets))

        list_of_retweets = [element.decode('utf-8') for element in tweets['text'].values if
                            element.decode('utf-8').startswith('RT')]
        print("Number of Retweets : ", len(list_of_retweets))

        self.plot_graph(tweets['user'], "#"+hash_tag+" by user",
                   "Language",
                   "Number of Tweets",
                   50)

def main():

    parser = argparse.ArgumentParser()
    parser.add_argument('-u', help="enter user URL")
    parser.add_argument('-ht', help="enter hashtag without #")

    args = parser.parse_args()

    if not args.u and not args.ht:
        exit("Please specify user URL to parse data")
    td = TwitterData()
    if args.u:
        username = args.u.split("/")[-1]
        try:
            td.get_auth()
            td.get_data(username)
        except:
            exit("Something went wrong")

    if args.ht:
        td.extract_trending_data(args.ht)

main()
