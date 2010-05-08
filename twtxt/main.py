#!/usr/bin/env python

import twitterapi
import statusview
import curses

import cursestools as ctools
import entry

class Main:
    views = dict()
    
    def __init__(self, conf):
        self.twitter = twitterapi.twitterapi(conf.get_token(), 200)
    
    def start(self, stdcur):
        self.stdcur = stdcur
        self.curses_init()
        
        home = self.create_newview("home_timeline", 30, True)        
        self.views[ord("h")] = home
        self.now = ord("h")

        mentions = self.create_newview("mentions", 300)
        self.views[ord("@")] = mentions
        
        self.main()
    
    def create_newview(self, method, interval = -1, enable = False):
        v = statusview.StatusView(self.statuscur)
        v.set_twitterapi(self.twitter)
        v.on_refresh = self.entrycur.refresh
        v.enable = enable
        v.set_timeline(method, interval)
        return v
    
    def main(self):
        selectmode = False
        view = self.views[self.now]
        
        while True:
            c = self.stdcur.getch()
            ctools.dputs("Key: 0x%x" % c)
            
            if c == ord(' '):
                selectmode = not selectmode
                view.clear_selected()
            elif c == curses.KEY_DOWN:
                if selectmode:
                    view.select_scroll()
                else:
                    view.scroll()
            elif c == curses.KEY_UP:
                if selectmode:
                    view.select_scroll(-1)
                else:
                    view.scroll(-1)
            elif c in (curses.KEY_ENTER, 0x0a):
                if selectmode:
                    sid = view.get_selected_statusid()
                    self.menu_popup(sid)
                else:
                    self.status_update()
            elif c == ord('q'):
                break
            else:
                if c in self.views:
                    ctools.dputs("Changed: 0x%x" % c)
                    view.enable = False
                    
                    self.now = c
                    view = self.views[self.now]
                    view.enable = True
                    view.refresh()
    
    def status_update(self):
        text = self.entry.getstr()
        if text != "": self.twitter.api.status_update(text)
    
    def curses_init(self):
        curses.use_default_colors()
        curses.init_pair(1, curses.COLOR_RED, -1)
        curses.init_pair(2, curses.COLOR_GREEN, -1)
        curses.init_pair(3, curses.COLOR_CYAN, -1)
        curses.init_pair(4, curses.COLOR_WHITE, curses.COLOR_BLUE)
        curses.init_pair(5, curses.COLOR_YELLOW, -1)
        
        curses.curs_set(0)
        curses.noecho()
        self.stdcur.keypad(1)
        (my, mx) = self.stdcur.getmaxyx()
        
        self.statuscur = self.stdcur.derwin(my - 2, mx, 2, 0)
        self.headcur = self.stdcur.derwin(1, mx, 1, 0)
        self.entrycur = self.stdcur.derwin(1, mx, 0, 0)
        
        self.headcur.bkgd("-", curses.color_pair(4))

        self.entry = entry.cursesEntry(self.entrycur)
        self.entrycur.addstr(0, 0, "[@%s] " % self.twitter.my_name)
        self.entry.setyx(*self.entrycur.getyx())

    def menu_popup(self, statusid):
        (my, mx) = self.statuscur.getmaxyx()
        popup = self.statuscur.derwin(10, 20, my / 2 - 5, mx / 2 - 10)
        popup.bkgd(" ", curses.color_pair(4))
        popup.clear()
        popup.box()
        popup.refresh()

