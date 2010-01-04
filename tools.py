#!/usr/bin/env python
#-*- coding: utf-8 -*-
#
# Twittext - tools.py
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

import re
import htmlentitydefs
import curses
import datetime
import locale

def split_text(s, w):
    i = 0
    ss = ""
    sss = []
    
    for c in s:
        if 0x00 <= ord(c) <= 0x7f:
            i += 1
        else:
            i += 2
        
        ss += c
        
        if i >= w - 1:
            if len(sss) == 0:
                sss = [ss]
            else:
                sss.append(ss)
            
            ss = ""
            i = 0
    
    if not ss == "":
        sss.append(ss)
    
    return sss

def replace_htmlentity(string):
    amp = string.find('&')
    if amp == -1:
        return string
    
    entity = re.compile("&([A-Za-z]+);")
    entity_match = entity.findall(string)

    for name in entity_match:
        c = htmlentitydefs.name2codepoint[name]
        string = string.replace("&%s;" % name, unichr(c))
    
    return string

def delete_notprintable(string):
    s = ""

    for c in string:
        if (not(0x00 <= ord(c) <= 0x7f)
            or 0x20 <= ord(c) <= 0x7e):
            s += c

    return s

def attr_select(post, me):
    user = post["user"]["screen_name"]
    reply_to = post["in_reply_to_screen_name"]
    myname = me["screen_name"]

    # Color Change
    if user == myname:
        # my status
        return curses.color_pair(3)
    elif reply_to == myname:
        # reply to me
        return (curses.color_pair(1) | curses.A_BOLD)
    else:
        at = post["text"].find("@%s" % myname)
        if at == 0:
            # reply to me, but no in_reply_to
            return curses.color_pair(1)
        elif at != -1:
            # maybe Retweet
            return curses.color_pair(2)
    
    return 0

def twittertime(timestr):
    format = "%a %b %d %H:%M:%S +0000 %Y"
    locale.setlocale(locale.LC_ALL, "C")
    dt = datetime.datetime.strptime(timestr, format)
    locale.setlocale(locale.LC_ALL, "")
    tz = datetime.datetime.now() - datetime.datetime.utcnow()
    dt += tz

    return dt

def twitterago(time):
    ago = datetime.datetime.now() - time

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

def twittersource(source):
    if source == "web":
        return "web"
    else:
        return source.split(">")[1].split("<")[0]

def isretweet(status):
    return "retweeted_status" in status.keys()

def listed_count(api):
    listed = 0
    cursor = -1

    while True:
        lists = api.lists_memberships(cursor = cursor)
        cursor = int(lists["next_cursor"])
        listed += len(lists["lists"])
        if cursor <= 0:
            break
        
    return listed

def split_user(s, i = 0):
    match = re.findall("@([0-9A-Za-z_]*)", s)
    if match:
        return match[i]

    return None

def statusinfo(status):
    created_at = twittertime(status["created_at"])
    puttime = str(created_at).split(".")[0]
    ago = twitterago(created_at)
    #isretweet(lpost[i])
    
    if "source" in status.keys():
        source = twittersource(status["source"])
        footer = "[%s] %s from %s" % (
            puttime, ago, source.encode("utf-8"))
    else:
        footer = "[%s] %s" % (puttime, ago)

    return footer
