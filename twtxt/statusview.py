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
#from tools import *
#from newinput import *

class StatusView():
    def __init__(self, win):
        self.win = win
        self.timeline = tuple()
        
        self.offset = 0
        self.selected = None
        
        (my, mx) = win.getmaxyx()
        self.wname = win.subwin(my, 10, 0, 0)
        self.wtext = win.subwin(0, 11)
            
    def refresh(self, timeline = None):
        self.wname.clear()
        self.wtext.clear()
        
        (my, mx) = self.wtext.getmaxyx()
        
        if timeline:
            self.timeline = timeline
        
        y = 0
        for i, s in enumerate(tuple((self.timeline[::-1])[self.offset:])):
            cnt = cw_count(s.text)
            row = int(math.ceil(float(cnt) / float(mx)))
            rem = my - y
            
            if row > rem:
                s = copy.copy(s)
                s.text = split_text(s.text, (rem * mx) - 1)[0]
            
            if self.selected == i:
                attr = curses.A_STANDOUT
                self.selected = None
            else:
                attr = curses.A_NORMAL
            
            dputs(attr)
            
            self.wname.addstr(y, 0, s.user.screen_name[:9], attr)
            self.wtext.addstr(y, 0, s.text.encode("utf-8"), attr)
            y = self.wtext.getyx()[0] + 1
            if y >= my: 
                self.last = i
                break
        
        self.wname.refresh()
        self.wtext.refresh()
    
    def scroll(self, i = 1):
        self.offset += i
        self.refresh()
    
    def select(self, i):
        if self.offset <= i <= self.last:
            self.selected = i
        else:
            self.offset = i
        
        self.refresh()
