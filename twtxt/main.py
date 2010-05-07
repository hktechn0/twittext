#!/usr/bin/env python

import twitterapi
import statusview
import curses

import cursestools as ctools

class Main:
    views = dict()
    
    def __init__(self, conf):
        self.twitter = twitterapi.twitterapi(conf.get_token(), 200)
    
    def start(self, stdcur):
        self.stdcur = stdcur
        self.curses_init()
        
        home = statusview.StatusView(self.statuscur)
        home.set_twitterapi(self.twitter)
        home.set_timeline("home_timeline", 30)
        self.views["h"] = home
        self.now = "h"

        self.main()
        
    def main(self):
        while True:
            c = self.stdcur.getch()
            ctools.dputs("Key: 0x%x" % c)
            
            if   c == ord(' '): self.views[self.now].scroll()
            elif c == curses.KEY_DOWN: self.views[self.now].scroll()
            elif c == curses.KEY_UP: self.views[self.now].scroll(-1)
            elif c == ord('q'): break
    
    def curses_init(self):
        curses.use_default_colors()
        curses.init_pair(1, curses.COLOR_RED, -1)
        curses.init_pair(2, curses.COLOR_GREEN, -1)
        curses.init_pair(3, curses.COLOR_CYAN, -1)
        curses.init_pair(4, curses.COLOR_WHITE, curses.COLOR_BLUE)
        curses.init_pair(5, curses.COLOR_YELLOW, -1)
        
        self.statuscur = self.stdcur.derwin(2, 0)
