#!/usr/bin/env python
#-*- coding: utf-8 -*-

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
    import re
    import htmlentitydefs

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
    import curses

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
