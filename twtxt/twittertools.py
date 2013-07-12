#!/usr/bin/env python
#-*- coding: utf-8 -*-

import re
import datetime

class TwitterTools:
    _urlpattern = u'''(?P<url>https?://[^\s　]*)'''
    _userpattern = u'''@(?P<user>\w+)'''
    
    def __init__(self):
        self.reurl = re.compile(self._urlpattern)
        self.reuser = re.compile(self._userpattern)

    def get_footer(self, status):
        time = self.get_time_hms(status.created_at)
        ago = self.get_time_ago(status.created_at)
        
        if "source" in status.keys():
            source = status.source_name
            footer = u"[%s] %s via %s" % (
                time, ago, source)
        else:
            fotter = "DirectMessage?"
        
        return footer
    
    ## Status
    # URL
    def get_colored_url(self, string):
        return self.reurl.sub(
            '<span foreground="#0000FF" underline="single">\g<url></span>',
            string)
    
    def get_urls(self, string):
        url_iter = self.reurl.finditer(string)
        urls = list()
        for i in url_iter:
            urls.append(i.group('url'))
        
        return tuple(urls)
    
    # User
    def get_users(self, string):
        match = self.reuser.finditer(string)
        
        users = list()
        for i in match:
            users.append(i.group('user'))
        
        return users
    
    # source
    def get_source_name(self, source):
        if source == "web":
            return u"web"
        else:
            i = source.find(">")
            if i != -1:
                return unicode(source[i + 1:-4])
            else:
                return unicode(source)
    
    ## Datetime
    def get_datetime(self, timestr):
        # Sample
        # Wed Nov 18 18:54:12 +0000 2009
        format = "%m %d %H:%M:%S +0000 %Y"
        m = {
            'Jan' : 1, 'Feb' : 2, 'Mar' : 3, 
            'Apr' : 4, 'May' : 5, 'Jun' : 6,
            'Jul' : 7, 'Aug' : 8, 'Sep' : 9, 
            'Oct' : 10, 'Nov' : 11, 'Dec' : 12
            }
        
        t = "%02d %s" % (m[timestr[4:7]], timestr[8:])
        dt = datetime.datetime.strptime(t, format)
        offset = time.altzone if time.daylight else time.timezone
        dt -= datetime.timedelta(seconds = offset)
        return dt
    
    def get_time_hms(self, dt):
        return dt.strftime("%H:%M:%S")
    
    def get_time_ago(self, dt):
        now = datetime.datetime.now()

        if now < dt:
            return "Just now!"
        
        ago = now - dt
        hours = ago.seconds / 3600
        minutes = ago.seconds / 60
        
        if ago.days:
            if ago.days == 1:
                return "1 day ago"
            else:
                return "%d days ago" % ago.days
        elif hours:
            if hours == 1:
                return "1 hour ago"
            else:
                return "%d hours ago" % hours
        elif minutes:
            if minutes == 1:
                return "1 minute ago"
            else:
                return "%d minutes ago" % minutes
        elif ago.seconds:
            if ago.seconds == 1:
                return "1 second ago"
            else:
                return "%d seconds ago" % ago.seconds
        else:
            return "Just now!"
        
    ## Retweet
    def isretweet(status):
        return "retweeted_status" in status.keys()
    
    ## Lists
    def get_listed_count(self, api, ret = None):
        listed = 0
        cursor = -1

        while True:
            lists = api.lists_memberships(cursor = cursor)
            cursor = int(lists["next_cursor"])
            listed += len(lists["lists"])
            if cursor <= 0:
                break

        if ret != None: ret = listed
        
        return listed

    def listed_count_background(api, ret):
        th = threading.Thread(target = listed_count, args = (api, ret))
        th.isDaemon()
        th.start()
