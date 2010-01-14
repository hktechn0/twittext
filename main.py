#!/usr/bin/env python
#-*- coding: utf-8 -*-
#
# Twittext - main.py
# - Hirotaka Kawata <info@techno-st.net>
# - http://www.techno-st.net/wiki/Twittext
#
#    Copyright (C) 2009 Hirotaka Kawata <info@techno-st.net>
#
#    This file is part of "Twittext".
#
#    Twittext is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    Twittext is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with Twittext.  If not, see <http://www.gnu.org/licenses/>.
#

import twoauth

from tools import *
from newinput import *

import curses
import locale
import datetime
import urllib2
import httplib

class twittext():
    from home import home
    from tl_show import tl_show
    from tl_select import tl_select
    
    def __init__(self, ckey, csecret, atoken, asecret):
        locale.setlocale(locale.LC_ALL, "")

        # twitter api instance
        self.api = twoauth.api(
            ckey, csecret, atoken, asecret)
        self.userlastget = datetime.datetime.now()

        # init temporary stack
        self.tmp = list()
        self.hist = list()

        self.statusfooter = ""
        self.autoreload = 60000 # ms        
    
    def run(self):
        while True:
            try:
                # start curses
                curses.wrapper(self.start)
                break
            except curses.error:
                pass

    def init(self):
        # curses init
        curses.use_default_colors()
        curses.curs_set(0)
        
        self.Y, self.X = self.stdcur.getmaxyx()

        # define color set
        curses.start_color()
        curses.init_pair(1, curses.COLOR_RED, -1)
        curses.init_pair(2, curses.COLOR_GREEN, -1)
        curses.init_pair(3, curses.COLOR_CYAN, -1)
        curses.init_pair(4, curses.COLOR_WHITE, curses.COLOR_BLUE)
        curses.init_pair(5, curses.COLOR_YELLOW, -1)

        self.stdcur.idlok(1)
        self.stdcur.scrollok(True)
        self.stdcur.clear()

        # create subwin
        self.tlwin = self.stdcur.subwin(self.Y - 3, self.X, 2, 0)
        self.tlwin.idlok(1)
        self.tlwin.scrollok(True)
        self.tlwin.clear()
        
        self.headwin = self.stdcur.subwin(1, self.X, 1, 0)
        self.headwin.immedok(True)
        self.headwin.bkgd(" ", curses.color_pair(4))
        self.headwin.attrset(curses.color_pair(4))

        self.footwin = self.stdcur.subwin(self.Y - 1, 0)
        self.footwin.immedok(True)
        self.footwin.bkgd(" ", curses.color_pair(4))
        self.footwin.attrset(curses.color_pair(4))

        self.hometl = list()
        self.since_id = str()
        self.max_id = str()

        self.mode = 0
        self.oldmode = -1
        self.stdcur.timeout(self.autoreload)

    def start(self, stdcur):
        # initialize
        self.stdcur = stdcur
        self.init()
        
        try:
            self.listed = listed_count(self.api)
        except:
            self.listed = -1

        while True:
            try:
                # show timeline
                while self.home():
                    y, x = self.stdcur.getmaxyx()
                    if (y, x) != (self.Y, self.X):
                        self.init()
                break
            except urllib2.HTTPError, e:
                # Twitter over capacity
                if e.code in (503, 502):
                    message = "Twitter Over Capacity..."
                elif e.code == 500:
                    message = "Twitter Server Error..."
                elif e.code == 400:
                    message = "Twitter REST API Rate Limited!"
                elif e.code == 404:
                    message = "Not Found..."
                elif e.code in (401, 403):
                    message = "Access Denied..."
                else:
                    raise

                self.mode = 0
                self.clear_head()
                self.stdcur.addstr(
                    0, 0,
                    "[Error] %s" % message,
                    curses.color_pair(1) | curses.A_BOLD)
                self.stdcur.refresh()
                self.stdcur.getch()
            except (httplib.BadStatusLine, urllib2.URLError):
                self.mode = 0
                self.clear_head()
                self.stdcur.addstr(
                    0, 0,
                    "[Error] HTTP Error",
                    curses.color_pair(1) | curses.A_BOLD)
                self.stdcur.refresh()
                self.stdcur.getch()
    
    def clear_head(self):
        self.stdcur.move(0, 0)
        self.stdcur.clrtoeol()
        self.stdcur.refresh()
    
    def getstr(self, *args):
        self.stdcur.timeout(-1)
        s = mbgetstr(self.stdcur, *args)
        self.stdcur.timeout(self.autoreload)
        return unicode(s)
    
    def post(self, status, error = 0):
        self.clear_head()
        self.stdcur.addstr(0, 0, "Updating Status...")
        self.stdcur.refresh()
        
        post = u"%s %s" % (
            status,
            self.statusfooter)

        try:
            self.api.status_update(post)
        except urllib2.HTTPError, e:
            # Twitter over capacity
            if error > 1:
                self.stdcur.addstr(" Error.",
                                   curses.color_pair(1) | curses.A_BOLD)
            elif e.code / 100 == 5:
                self.post(status, error + 1)
            else:
                raise
        else:
            self.stdcur.addstr(" OK.")

        self.stdcur.refresh()
        self.stdcur.getch()
    
    def reply(self, status):
        self.clear_head()
        self.stdcur.addstr(0, 0, "Reply: ")
        self.stdcur.refresh()

        name = status["user"]["screen_name"]
        reply_to = status["id"]

        replyhead = "@%s " % name
        self.stdcur.addstr(0, 7, replyhead)
        
        message = self.getstr()
        
        if message:
            self.clear_head()
            self.stdcur.addstr(0, 0, "Reply... ")
            self.stdcur.refresh()

            reply = u"%s%s" % (replyhead, message)
            post = self.api.status_update(
                reply, in_reply_to_status_id = reply_to)
            
            self.stdcur.addstr("OK. (%s)" % post["id"])
            self.stdcur.refresh()
            self.stdcur.getch()

    def retweet(self, _id):
        self.clear_head()
        self.stdcur.addstr("Retweet? (Y/n)")
        self.stdcur.refresh()

        if self.stdcur.getch() != ord("n"):
            self.clear_head()
            self.stdcur.addstr(0, 0, "Retweet... ")
            self.stdcur.refresh()

            self.api.status_retweet(_id)
            self.stdcur.addstr("OK.")
            self.stdcur.refresh()
            self.stdcur.getch()
    
    def quotetweet(self, status):
        self.clear_head()
        self.stdcur.addstr("QT: ")
        message = self.getstr()
        
        if message:
            qt = u"%s QT: @%s: %s" % (
                message, status["user"]["screen_name"], status["text"])
            self.post(qt)
    
    def destroy(self, status):
        self.clear_head()
      
        if int(self.api.user["id"]) == int(status["user"]["id"]):
            self.stdcur.addstr(0, 0, "Destroy? (Y/n): ")
            self.stdcur.refresh()
            
            if self.stdcur.getch() != ord("n"):
                self.clear_head()
                self.stdcur.addstr("Destroying: ")
                self.stdcur.refresh()

                self.api.status_destroy(status["id"])

                self.stdcur.addstr("OK.")
                self.stdcur.refresh()
                self.stdcur.getch()
            else:
                self.clear_head()
        else:
            self.stdcur.addstr(0, 0, "[Error] Can't destroy this status...")
            self.stdcur.refresh()
            self.stdcur.getch()
    
    def friendship(self, user):
        self.clear_head()
        
        fr = self.api.friends_show(user)
        ed = fr["source"]["followed_by"] == "true"
        ing = fr["source"]["following"] == "true"
        
        a = "<" if ed else " "
        b = ">" if ing else " "
        
        me = self.api.user["screen_name"]
        self.stdcur.addstr("@%s %s===%s @%s" % (me, a, b, user))
        self.stdcur.getch()

    def dmessage(self, user):
        self.clear_head()
        self.stdcur.addstr("D %s " % user)
        message = self.getstr()
        
        self.clear_head()
        self.stdcur.addstr("Sending Direct Message: ")
        self.stdcur.refresh()
        self.api.dm_new(user, message)
        self.stdcur.addstr("OK.")
        self.stdcur.refresh()
        self.stdcur.getch()

    def detail(self, status):
        self.clear_head()
        
        #self.headwin.addstr(0, 0, "[Status Detail]")
        #self.headwin.clrtoeol()
        
        self.footwin.addstr(0, 0, statusinfo(status))
        self.footwin.clrtoeol()
        
        self.tlwin.clear()
        self.tlwin.move(0, 0)
        s = "%s\n(%s)\n\n%s\n%s\n\n<%s>" % (
            status["user"]["screen_name"],
            status["user"]["name"],
#            status["user"]["following"],
#            "Protected" if status["user"]["protected"] == "true" else "",
            "-" * (self.X - 1),
            status["text"],
            status["id"],)
        self.tlwin.addstr(s.encode("utf-8"))
        self.tlwin.refresh()
        self.stdcur.getch()
    
    def loading(self, name):
        self.tlname = name
        self.headwin.addstr(0, 0, "[%s]" % name)
        
        self.tlwin.clear()
        self.tlwin.refresh()
        
        self.clear_head()
        self.stdcur.addstr(0, 0, "Loading...")
        self.stdcur.refresh()
