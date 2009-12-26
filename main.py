#!/usr/bin/env python
#-*- coding: utf-8 -*-

import twoauth

from tools import *

import curses
import locale

class twittext():
    def __init__(self, ckey, csecret, atoken, asecret):
        # twitter api instance
        self.api = twoauth.api(
            ckey, csecret, atoken, asecret)

        # start curses
        locale.setlocale(locale.LC_ALL, "")
        curses.wrapper(self.start)
    
    def start(self, stdcur):
        # curses init
        curses.use_default_colors()
        curses.curs_set(0)
        
        (self.Y, self.X) = stdcur.getmaxyx()

        # define color set
        curses.start_color()
        curses.init_pair(1, curses.COLOR_RED, -1)
        curses.init_pair(2, curses.COLOR_GREEN, -1)
        curses.init_pair(3, curses.COLOR_BLUE, -1)

        # create subwin
        self.stdcur = stdcur
        self.stdcur.idlok(1)
        self.stdcur.scrollok(True)
        self.tlwin = stdcur.subwin(self.Y - 3, self.X, 2, 0)
        self.tlwin.idlok(1)
        self.tlwin.scrollok(True)
        self.statwin = stdcur.subwin(self.Y - 1, 0)
        self.statwin.immedok(True)

        # show timeline
        self.mode = 0
        while self.home(): pass;

    def home(self):
        # print header
        self.stdcur.clear()
        self.stdcur.addstr(0, 0, "Post?: ")
        self.stdcur.addstr(" " * (self.X - 8), curses.A_UNDERLINE)
        header = " (@%s) [Twittext]" % self.api.user["screen_name"]
        self.stdcur.addstr(1, self.X - len(header), header)
        self.stdcur.refresh()
        
        # timeline mode
        if self.mode == 0:
            tl = self.api.home_timeline(count = self.Y)
       
        # print timeline
        lshow = self.tl_show(tl)
        
        # key input
        key = self.stdcur.getch(0, 7)

        if key == curses.KEY_DOWN:
            self.tl_select(lshow)
        
        return True
    
    def getstr(self, *args):
        import newinput
        return newinput.mbgetstr(self.stdcur, *args)

    def post(self, status, reply_to = ""):
        self.stdcur.addstr(0, 0, "Updating Status...")
        self.stdcur.clrtoeol()
        return self.api.status_update(
            status, in_reply_to_status_id = reply_to)

    def reply(self, status):
        self.stdcur.addstr(0, 0, "Reply: ")
        self.stdcur.clrtoeol()

        name = status["user"]["screen_name"]
        reply_to = status["id"]

        replyhead = "@%s " % name
        self.stdcur.addstr(0, 7, replyhead)
        
        message = self.getstr()
        
        if message:
            reply = ("%s%s" % (replyhead, message)).encode("utf-8")
            post = self.post(reply, reply_to)

            self.stdcur.addstr(0, 0, "Reply: OK (%s)" % post["id"])
            self.stdcur.clrtoeol()
    
    def tl_show(self, tl):
        self.tlwin.clear()

        ret = []
        i = 0
        for s in tl[::-1]:
            # set curses attr (color)
            self.tlwin.attrset(attr_select(s, self.api.user))
            
            # print screen_name
            sname = "[%7s] " % (s["user"]["screen_name"][0:7])
            self.tlwin.addstr(i, 0, sname)
            
            # escape status text
            raw_str = s["text"]
            raw_str = replace_htmlentity(raw_str)
            raw_str = delete_notprintable(raw_str)
            
            (Y, X) = self.tlwin.getmaxyx()
            
            # split status text
            sss = split_text(raw_str, X - len(sname))
            sss = sss[0:Y - i]
            
            for ss in sss:
                self.tlwin.addstr(i, 10, ss.encode("utf-8"))
                
                ret.append(s)
                i += 1
            
            if Y <= i:
                break
        
        # dispose...
        self.tlwin.attrset(0)
        self.tlwin.refresh()

        return ret

    def tl_select(self, lpost):
        self.tlwin.move(0, 0)
        self.tlwin.refresh()

        i = 0
        
        while True:
            attr = attr_select(lpost[i], self.api.user) & 0xffffff00
            s = self.tlwin.instr(i, 0)

            self.tlwin.move(i, 0)
            self.tlwin.clrtoeol()
            self.tlwin.addstr(s[:-1], attr | curses.A_STANDOUT)
            
            #self.tlwin.move(i, 0)
            self.tlwin.refresh()

            curses.flushinp()
            c = self.stdcur.getch(0, 0)

            if len(lpost) <= i:
                target = None
            else:
                target = lpost[i]

            # cursor point
            p = 0

            (Y, X) = self.tlwin.getmaxyx()

            if c == curses.KEY_DOWN:
                if i < Y - 1:
                    p = 1
            elif c == curses.KEY_UP:
                if i > 0:
                    p = -1
            elif target:
                if c == 0x0a or c == curses.KEY_ENTER:
                    # Reply
                    self.reply(target)
            else:
                continue
            
            self.tlwin.move(i, 0)
            self.tlwin.clrtoeol()
            self.tlwin.addstr(s[:-1], attr)
            
            i += p
            
            #self.tlwin.move(i, 0)
            self.tlwin.refresh()
        
        return
