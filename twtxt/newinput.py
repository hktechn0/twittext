#!/usr/bin/env python
#-*- coding: utf-8 -*-

#
# Twittext
# curses.getstr() for UTF-8
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

import curses
import cursestools as ctools

class cursesEntry:
    CENCODING = "utf-8"
    startend = (0, 0)
    (y, x) = (0, 0)
    
    def __init__(self, win):
        self.win = win
        (self.my, self.mx) = self.win.getmaxyx()
    
    def setyx(y, x):
        self.y = y
        self.x = x
    
    # usage: getstr(win, [y, x])
    def getstr(self):
        self.win.move(self.y, self.x)
        self.win.clrtoeol()
        self.win.refresh()
        self.startend = (0, 0)
        
        curses.flushinp()
        curses.noecho()
        curses.curs_set(1)
        
        s = unicode()
        i = 0
        
        while True:
            (y, x) = self.win.getyx()
            
            c = self.win.getch()
            
            if c == 0x0a:
                break # \n
            elif c in (curses.KEY_BACKSPACE, 0x08):
                if i <= 0: continue            
                s = s[:i - 1] + s[i:]
                i -= 1
                self.rewrite_text(s, i)
            elif c == curses.KEY_DC:
                s = s[:i] + s[i + 1:]
                self.rewrite_text(s, i)
            elif c == curses.KEY_LEFT:
                if i <= 0: continue
                i -= 1
                self.rewrite_text(s, i)
            elif c == curses.KEY_RIGHT:
                if i >= len(s): continue
                i += 1
                self.rewrite_text(s, i)
            elif curses.KEY_MIN <= c <= curses.KEY_MAX:
                pass
            else:
                # UTF-8 input
                if c & 0x80:
                    f = c << 1
                    while f & 0x80:
                        f <<= 1
                        c <<= 8
                        c += (self.win.getch() & 0xff)
                
                c = ctools.utf2ucs(c)
                
                if ctools.isascii(c) and not ctools.isprintable(c):
                    continue
                
                s = u"%s%s%s" % (s[:i], c, s[i:])
                i += 1
                self.rewrite_text(s, i)
        
        curses.curs_set(0)
        
        return s
    
    def rewrite_text(s, i):
        (os, oe) = self.startend
        
        self.win.move(sety, setx)
        self.win.clrtoeol()
        
        if os <= i <= oe:
            self.win.addstr(s[os:i].encode(CENCODING))
            (y, x) = self.win.getyx()
            exstr = ctools.exstr_width(s[i:], self.mx - self.x)
            self.win.addstr(exstr.encode(CENCODING))
            self.win.move(y, x)
            self.startend = (os, i + len(exstr))
        else:
            if i < os:
                exstr = ctools.exstr_width(s[i:], self.mx - self.x)
                self.startend = (i, i + len(exstr))
                self.win.addstr(exstr.encode(CENCODING))
                self.win.move(self.y, self.x)
            else:
                exstr = ctools.exstr_width(
                    s[i - 1::-1], ctools.cw_count(s[os:oe]) + 3)
                exstr = ctools.exstr_width(exstr, self.mx - self.x)
                exstr = exstr[::-1]
                self.startend = (i - len(exstr), i)
                self.win.addstr(exstr.encode(CENCODING))
