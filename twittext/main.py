#-*- coding: utf-8 -*-

import twoauth
import twoauth.streaming
import terminalui

import timelinethread
import tweetstore

class Twittext(object):
    def __init__(self, settings):
        self.terminal = terminalui.TerminalUI()
        
        text = terminalui.Entry()
        text.set_size(-1, 3)
        self.homeview = terminalui.ListView(2)
        self.homeview.set_column_width((10, -1))
        
        vbox = terminalui.VBox()
        vbox.pack_start(text)
        vbox.pack_end(self.homeview)
        
        self.mainwin = terminalui.Window()
        self.mainwin.add(vbox)
        
        self.settings = settings
        self.twitterapi = twoauth.api(*self.settings.get_token())
        streaming = twoauth.streaming.StreamingAPI(self.twitterapi.oauth)
        userstreams = streaming.user()
        
        self.tweets = tweetstore.TweetStore()
        
        t = timelinethread.StreamingTimelineThread()
        t.set_stream(userstreams)
        t.set_event(self.on_add_tweets)
        t._on_update_before(self.tweets.add_tweets)
        t.start()
    
    def main(self):
        self.terminal.add_widget(self.mainwin)
        self.terminal.main()
    
    def on_add_tweets(self, statuses):
        for i in statuses:
            if isinstance(i, twoauth.TwitterStatus):
                self.homeview.prepend((i.user.screen_name[:10], i.text))
