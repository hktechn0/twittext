#!/usr/bin/env python

import curses

class PopupMenu:
    def __init__(self, coly, colx):
        self.pad = curses.newpad(coly, colx)
        
        self.pad.bkgd(" ", curses.color_pair(4))
        self.pad.clear()
        self.pad.box()

    def popup(self, r):
        self.pad.refresh(*r)
