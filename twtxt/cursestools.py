#!/usr/bin/env python
#-*- coding: utf-8 -*-
#
# Twittext - tools.py
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

import re
import htmlentitydefs
import curses

# split_text by width
def split_text(s, w):
    i = 0
    ss = unicode()
    sss = list()
    
    for c in unicode(s):
        i += 1 if 0x00 <= ord(c) <= 0x7f else 2        
        ss += c

        if i >= w - 1:
            if len(sss) == 0: sss = [ss]
            else: sss.append(ss)            
            ss = unicode()
            i = 0
    
    if ss: sss.append(ss)
    return sss

# isascii?
def isascii(c):
    if 0x00 <= ord(c) <= 0x7f:
        return True
    else:
        return False

# Character width count
def cw_count(string):
    cnt = 0

    for c in string:
        cnt += 1 if isascii(c) else 2
    
    return cnt

# Extract string by width
def exstr_width(string, cnt):
    width = 0
    i = 0

    for c in string:
        width += 1 if isascii(c) else 2

        if width >= cnt:
            break
        else:
            i += 1

    return string[:i]

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

# isprintable?
def isprintable(c):
    if 0x20 <= ord(c) <= 0x7e:
        return True
    else:
        return False

def delete_notprintable(string):
    s = unicode()

    for c in unicode(string):
        if (not(0x00 <= ord(c) <= 0x7f)
            or 0x20 <= ord(c) <= 0x7e):
            s += c

    return s

def attr_select(post, myname):
    user = post.user.screen_name
    reply_to = post.in_reply_to_screen_name if (
        "in_reply_to_screen_name" in post.keys()) else None
    
    # Color Change
    if user == myname:
        # my status
        return curses.color_pair(3)
    elif reply_to == myname:
        # reply to me
        return (curses.color_pair(1) | curses.A_BOLD)
    else:
        at = post.text.find("@%s" % myname)
        if at == 0:
            # reply to me, but no in_reply_to
            return curses.color_pair(1)
        elif at != -1:
            # maybe Retweet
            return curses.color_pair(2)

    return 0

def utf2ucs(utf):
    if utf & 0x80:
        # multibyte
        buf = list()
        while not (utf & 0x40):
            buf.append(utf & 0x3f)
            utf >>= 8
        buf.append(utf & (0x3f >> len(buf)))

        ucs = 0
        while buf:
            ucs <<= 6
            ucs += buf.pop()
    else:
        # ascii
        ucs = utf
    
    return unichr(ucs)

def dputs(*args):
    fp = open("debug", 'a')
    l = list()
    for i in args:
        l.append(unicode(i))
    fp.write("%s\n" % " ".join(l).encode("utf-8"))
    fp.close()
