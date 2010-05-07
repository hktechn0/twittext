#!/usr/bin/env python
#-*- coding: utf-8 -*-
#
# Twittext - statusview.py
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


import curses
import math
import copy

import cursestools as ctools

class StatusView():
    CENCODING = "utf-8"
    timeline = tuple()    
    offset = 0
    selected = None
    
    def __init__(self, win):
        self.win = win
        
        (my, mx) = win.getmaxyx()
        self.wname = win.derwin(my - 1, 10, 0, 0)
        self.wtext = win.derwin(my - 1, mx - 11, 0, 11)
        self.winfo = win.derwin(1, mx, my - 1, 0)

        self.winfo.bkgd("-", curses.color_pair(4))
    
    def set_twitterapi(self, api):
        self.twitter = api

    def set_timeline(self, method, interval = -1):
        self.tlthread = self.twitter.create_timeline(method, interval)
        self.tlthread.reloadEventHandler = self.on_timeline_reload
        self.tlthread.start()
    
    def on_timeline_reload(self, ids):
        statuses = self.twitter.get_statuses(ids)
        self.add(statuses)
    
    def add(self, statuses):
        self.timeline = statuses + self.timeline
        self.refresh()
    
    def refresh(self):
        self.wname.clear()
        self.wtext.clear()
        
        (my, mx) = self.wtext.getmaxyx()
        
        y = 0
        for i, s in enumerate(self.timeline[self.offset:]):
            cnt = ctools.cw_count(s.text)
            row = int(math.ceil(float(cnt) / float(mx)))
            rem = my - y
            
            if row > rem:
                s = copy.copy(s)
                s.text = ctools.split_text(s.text, (rem * mx) - 1)[0]
            
            if self.selected == i:
                attr = curses.A_STANDOUT
                self.selected = None
            else:
                attr = curses.A_NORMAL
            
#            ctools.dputs("Status: %d %s %s" % (attr, s.user.screen_name, s.text))

            self.wname.addstr(y, 0, s.user.screen_name[:9], attr)
            self.wtext.addstr(y, 0, s.text.encode(self.CENCODING), attr)
            y = self.wtext.getyx()[0] + 1
            if y >= my: 
                self.last = i
                break
        
        self.wname.refresh()
        self.wtext.refresh()
    
    def scroll(self, i = 1):
        self.offset += i if self.offset + i >= 0 else 0
        self.refresh()
    
    def select(self, i):
        if self.offset <= i <= self.last:
            self.selected = i
        else:
            self.offset = i
        
        self.refresh()
