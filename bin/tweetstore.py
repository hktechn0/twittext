#-*- coding: utf-8 -*-

class TweetStore(dict):
    def add(self, tweet):
        self[tweet.id] = tweet

    def add_tweets(self, tweets):
        for t in tweets:
            self.add(t)
