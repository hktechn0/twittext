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
    enable = False
    
    def __init__(self, win):
        self.win = win

        (my, mx) = win.getmaxyx()
        self.wname = win.derwin(my - 1, 10, 0, 0)
        self.wtext = win.derwin(my - 1, mx - 11, 0, 11)
        self.winfo = win.derwin(1, mx, my - 1, 0)
        
        self.win.leaveok(1)
        self.wname.leaveok(1)
        self.wtext.leaveok(1)
        self.winfo.leaveok(1)
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
        if self.enable:
            self.refresh()
            curses.flash()
    
    def refresh(self):
        syx = curses.getsyx()
        ctools.dputs(syx)
        
        self.wname.clear()
        self.wtext.clear()
        
        (my, mx) = self.wtext.getmaxyx()
        
        y = 0
        for i, s in enumerate(self.timeline[self.offset:]):
            # escape illegal character
            s.text = ctools.delete_notprintable(s.text)
            
            cnt = ctools.cw_count(s.text)
            row = int(math.ceil(float(cnt) / float(mx)))
            rem = my - y
            
            if row > rem:
                s = copy.copy(s)
                s.text = ctools.split_text(s.text, (rem * mx) - 1)[0]
            
            if self.selected == i:
                attr = curses.A_STANDOUT
#                self.selected = None
            else:
                attr = curses.A_NORMAL
            
            self.wname.addstr(y, 0, s.user.screen_name[:9], attr)
            self.wtext.addstr(y, 0, s.text.encode(self.CENCODING), attr)

            y += row
            if y >= my: 
                self.last = i
                break
        
        self.wname.refresh()
        self.wtext.refresh()
        
        curses.setsyx(*syx)
        self.on_refresh()
    
    def scroll(self, i = 1):
        self.offset += i if self.offset + i >= 0 else 0
        self.refresh()
    
    def select_scroll(self, i = 1):
        ctools.dputs(self.selected)
        
        if self.selected != None:
            n = self.selected + i
            
            if n > self.last:
                oldlast = self.last
                self.scroll(n - self.last)
                self.select(self.last)
            elif n < 0:
                self.scroll(n)
            else:
                self.select(n)
        else:
            self.select(0)
    
    def select(self, i):        
        if i < 0 or self.last < i: return
        self.selected = i
        self.refresh()
    
    def clear_selected(self):
        self.selected = None
        self.refresh()

    def on_refresh(self): pass
