#!/usr/bin/env python
#-*- coding: utf-8 -*-
#
# Twittext - home.py
# - Hirotaka Kawata <info@techno-st.net>
# - http://www.techno-st.net/wiki/Twittext
#
#    Copyright (C) 2009-2010 Hirotaka Kawata <info@techno-st.net>
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

from tools import *
from newinput import *

MODE_INVALID = -1
MODE_HOME_TIMELINE = 0
MODE_MENTION_TIMELINE = 1
MODE_USER_TIMELINE = 2
MODE_RETWEET_TIMELINE = 3
MODE_PUBLIC_TIMELINE = 4
MODE_FAVORITES = 5
MODE_DIRECT_MESSAGES = 7
MODE_HELP = 8

helptext = ("=== Command Mode ===", \
			"Enter .... Updated status", \
			"h ........ Show (Update) Home Timeline", \
			"@ ........ Show mentions", \
			"r ........ Show retweets", \
			"p ........ Show public timeline", \
			"u ........ Show user timeline", \
			"f ........ Show your favorites", \
			"d ........ Show Direct Messages", \
			"D ........ Send direct message", \
			"F ........ Friendship check", \
			"q ........ Quit", \
			"Key Down . To Status Selection Mode", \
			"", \
			"=== Status Selection Mode ===", \
			"@ ........ Reply", \
			"r ........ Retweet (Using retweet API method)", \
			"q ........ Quote tweet", \
			"u ........ User timeline", \
			"U ........ Reply_to user timeline", \
			"t ........ Show reply_to status", \
			"d ........ Destroy status", \
			"D ........ Send direct message", \
			"f ........ Favorite status", \
			"F ........ Friendship check",\
			"Key Left . Return to Command Mode", \
			"", \
			"=== Key alias ===", \
			"Space .... Update Home Timeline", \
			"Key Left . Update Home Timeline", \
			"", \
			"Enter .... Reply", \
			"Escape ... To Command Mode", \
			"Backspace. To Command Mode", \
			"Key Right. Show User Timeline", \
			)



def home(self):
    if self.mode > MODE_INVALID: self.headwin.clear()
    self.footwin.clear()
    
    # Header
    header = "%d/%d %d/%d (@%s) [Twittext]" % (
        self.api.ratelimit_remaining,
        self.api.ratelimit_limit,
        self.api.ratelimit_ipremaining,
        self.api.ratelimit_iplimit,
        self.api.user["screen_name"])
    self.headwin.addstr(0, self.X - len(header) - 1, header)
    
    # Footer
    if (datetime.datetime.now() - self.userlastget).seconds > 300:
        me = self.api.verify_credentials()
        self.api.user = me
        self.userlastget = datetime.datetime.now()
    else:
        me = self.api.user

    userinfo = """\
Total: %s tweets, \
Following: %s, Followers: %s, \
Listed: %d""" % (
        me["statuses_count"], 
        me["friends_count"], me["followers_count"],
        self.listed)
    self.footwin.addstr(0, 0, userinfo)

    helpinfo = "Press ? for Help"
    self.footwin.addstr(0, self.X - len(helpinfo) - 1, helpinfo)

    if self.mode != MODE_INVALID:
        # clear scroll hist
        if self.oldmode != self.mode:
            self.hist = list()

        # Backup for scroll
        self.oldmode = self.mode
        self.oldtmp = list(self.tmp)

    # timeline mode
    if self.mode == MODE_HOME_TIMELINE:
        self.loading("Home Timeline")

        newtl = self.api.home_timeline(
            count = self.Y, 
            since_id = self.since_id, max_id = self.max_id)

        if newtl:
            self.newcnt = len(newtl) \
                if not self.max_id and self.since_id else 0

            self.hometl.extend(newtl)

        self.tl = self.hometl

        if not self.max_id:
            self.since_id = self.hometl[-1]["id"]
    elif self.mode == MODE_MENTION_TIMELINE:
        self.loading("Tweets mentioning @%s" % 
                     (self.api.user["screen_name"]))
        self.tl = self.api.mentions(count = self.Y,
                                    max_id = self.max_id)
    elif self.mode == MODE_USER_TIMELINE:
        tluser = self.tmp.pop()
        self.loading("@%s Timeline" % tluser)
        self.tl = self.api.user_timeline(tluser, count = self.Y,
                                         max_id = self.max_id)
    elif self.mode == MODE_RETWEET_TIMELINE:
        m = self.tmp.pop()
        if m == 1:
            self.loading("Retweets by others")
            self.tl = self.api.retweeted_to_me(count = self.Y,
                                        max_id = self.max_id)
        elif m == 2:
            self.loading("Retweets by you")
            self.tl = self.api.retweeted_by_me(count = self.Y,
                                        max_id = self.max_id)
        elif m == 3:
            self.loading("Your tweets, retweeted")
            self.tl = self.api.retweets_of_me(count = self.Y,
                                        max_id = self.max_id)
    elif self.mode == MODE_PUBLIC_TIMELINE:
        self.loading("Public Timeline")
        self.tl = self.api.public_timeline(count = self.Y,
                                           max_id = self.max_id)
    elif self.mode == MODE_FAVORITES:
        self.loading("Your Favorites")
        self.tl = self.api.favorites()
#    elif self.mode == 6:
#        q = self.tmp.pop()
#        self.loading("Real-time results for %s" % q)
#        self.tl = pass
    elif self.mode == MODE_DIRECT_MESSAGES:
        self.loading("Direct messages sent only to you")
        self.tl = self.api.dm_list(count = self.Y,
                                   max_id = self.max_id)
    elif self.mode == MODE_HELP:
        self.loading("Help")

    # print header
    self.stdcur.addstr(0, 0, "Post?: ")
    self.stdcur.addstr(" " * (self.X - 8), curses.A_UNDERLINE)

    # print timeline
    if self.mode == MODE_HELP:
        self.tl_help(helptext)
        lshow = None
    else:
        lshow = self.tl_show(self.tl)

    self.mode = MODE_INVALID
    self.max_id = ""    

    while True:
        # key input
        curses.flushinp()

        key = self.stdcur.getch(0, 7)

        if self.oldmode == MODE_HELP:
            # nothing
            self.mode = MODE_HOME_TIMELINE
        elif key == curses.KEY_DOWN:
            # Post Select Mode
            if lshow: self.tl_select(lshow)
        elif key in (curses.KEY_ENTER, 0x0a):
            # Update Status
            self.stdcur.move(0, 7)
            self.stdcur.clrtoeol()
            status = self.getstr()
            if status: self.post(status)
        elif key == ord("@"):
            # Show Reply
            self.mode = MODE_MENTION_TIMELINE
        elif key == ord("u"):
            # User Timeline
            self.clear_head()
            self.stdcur.addstr(0, 0, "User?: @")
            self.stdcur.refresh()
            user = self.getstr()
            self.tmp.append(user)
            self.mode = MODE_USER_TIMELINE
        elif key == ord("p"):
            # Public Timeline
            self.mode = MODE_PUBLIC_TIMELINE
        elif key == ord("r"):
            # Retweet
            self.clear_head()
            self.stdcur.addstr(
                0, 0, """\
1: Retweets by others, \
2: Retweets by you, \
3: Your tweets, retweeted""")
            n = self.stdcur.getch() - ord("0")
            if n in (1, 2, 3):
                self.mode = MODE_RETWEET_TIMELINE
                self.tmp.append(n)
        elif key == ord("f"):
            # Favorite
            self.mode = MODE_FAVORITES
        elif key == ord("F"):
            # Friendship
            self.clear_head()
            self.stdcur.addstr(0, 0, "User?: @")
            self.stdcur.refresh()
            user = self.getstr()
            self.friendship(user)
            self.stdcur.getch()
            continue
#        elif key == ord("s"):
#            # Search
#            self.stdcur.addstr(0, 0, "Search: ")
#            self.stdcur.clrtoeol()
#            q = self.getstr()
#            self.tmp.append(q)
#            self.mode = 6
        elif key == ord("d"):
            # Show Direct Messages
            self.mode = MODE_DIRECT_MESSAGES
        elif key == ord("D"):
            # Send Direct Message
            self.clear_head()
            self.stdcur.addstr("D User?: ")
            self.stdcur.refresh()
            user = self.getstr()
            if user:
                self.dmessage(user)
        elif key in (-1, curses.KEY_LEFT, ord("h"), ord(" ")):
            # Home Timeline
            self.mode = MODE_HOME_TIMELINE
        elif key == ord("?"):
            # Show help
            self.mode = MODE_HELP
        elif key == ord("q"):
            # Quit
            return False
        else:
            continue

        break

    return True
