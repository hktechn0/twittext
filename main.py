#!/usr/bin/env python
#-*- coding: utf-8 -*-

import twoauth

class twittext():
    def __init__(self, ckey, csecret, atoken, asecret):
        self.api = twoauth.api(
            ckey, csecret, atoken, asecret)

        locale.setlocale(locale.LC_ALL, "")
        curses.wrapper(self.start)

    def start(self, stdcur):
        stdcur.scrollok(True)
        curses.use_default_colors()
        curses.curs_set(0)

        curses.start_color()
        curses.init_pair(1, curses.COLOR_RED, -1)
        curses.init_pair(2, curses.COLOR_GREEN, -1)
        curses.init_pair(3, curses.COLOR_BLUE, -1)

        curses.subwin()
