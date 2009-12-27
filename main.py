#!/usr/bin/env python
#-*- coding: utf-8 -*-

import twoauth

from tools import *

import curses
import locale
import datetime

class twittext():
    def __init__(self, ckey, csecret, atoken, asecret):
        # twitter api instance
        self.api = twoauth.api(
            ckey, csecret, atoken, asecret)

        # init temporary stack
        self.tmp = []

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
        curses.init_pair(4, curses.COLOR_WHITE, curses.COLOR_BLUE)

        # create subwin
        self.stdcur = stdcur
        self.stdcur.idlok(1)
        self.stdcur.scrollok(True)
        self.stdcur.clear()

        self.tlwin = stdcur.subwin(self.Y - 3, self.X, 2, 0)
        self.tlwin.idlok(1)
        self.tlwin.scrollok(True)
        self.tlwin.clear()

        self.headwin = stdcur.subwin(1, self.X, 1, 0)
        self.headwin.immedok(True)
        self.headwin.bkgd(" ", curses.color_pair(4))
        self.headwin.attrset(curses.color_pair(4))

        self.footwin = stdcur.subwin(self.Y - 1, 0)
        self.footwin.immedok(True)
        self.footwin.bkgd(" ", curses.color_pair(4))
        self.footwin.attrset(curses.color_pair(4))

        # show timeline
        self.mode = 0
        while self.home(): pass;

    def home(self):
        if self.mode >= 0:
            self.headwin.clear()
        self.footwin.clear()

        # Header
        limit = self.api.rate_limit()
        (lnow, lmax) = (limit["remaining-hits"], limit["hourly-limit"])
        header = "%d/%d (@%s) [Twittext]" % (
            int(lnow), int(lmax), self.api.user["screen_name"])
        self.headwin.addstr(0, self.X - len(header) - 1, header)

        # Footer init
        me = self.api.verify_credentials()
        listed = listed_count(self.api)

        # Footer
        userinfo = "Total: %s tweets, Following: %s, Followers %s, Listed: %d" % (
            me["statuses_count"], me["friends_count"], me["followers_count"], listed)
        self.footwin.addstr(0, 0, userinfo)

        self.stdcur.addstr(0, 0, "Loading...")
        self.stdcur.clrtoeol()
        self.stdcur.refresh()

        # timeline mode
        if self.mode == 0:
            self.headwin.addstr(0, 0, "[Home Timeline]")
            self.tl = self.api.home_timeline(count = self.Y)
        elif self.mode == 1:
            self.headwin.addstr(0, 0, "[Tweets mentioning @%s]" % 
                                (self.api.user["screen_name"]))
            self.tl = self.api.mentions(count = self.Y)
        elif self.mode == 2:
            tluser = self.tmp.pop()
            self.headwin.addstr(0, 0, "[@%s Timeline]" % tluser)
            self.tl = self.api.user_timeline(tluser, count = self.Y)
        elif self.mode == 3:
            m = self.tmp.pop()
            if m == 1:
                self.headwin.addstr(0, 0, "[Retweets by others]")
                self.tl = self.api.rt_to_me(count = self.Y)
            elif m == 2:
                self.headwin.addstr(0, 0, "[Retweets by you]")
                self.tl = self.api.rt_by_me(count = self.Y)
            elif m == 3:
                self.headwin.addstr(0, 0, "[Your tweets, retweeted]")
                self.tl = self.api.rt_of_me(count = self.Y)

        # print header
        self.stdcur.addstr(0, 0, "Post?: ")
        self.stdcur.addstr(" " * (self.X - 8), curses.A_UNDERLINE)
        
        self.mode = -1
        
        # print timeline
        lshow = self.tl_show(self.tl)
        
        while True:
            # key input
            curses.flushinp()
            key = self.stdcur.getch(0, 7)
            
            if key == curses.KEY_DOWN:
                # Post Select Mode
                self.tl_select(lshow)
            elif key in (curses.KEY_ENTER, 0x0a):
                # Update Status
                self.stdcur.move(0, 7)
                self.stdcur.clrtoeol()
                status = self.getstr()
                
                if status:
                    self.post(status)
            elif key == ord("@"):
                # Show Reply
                self.mode = 1
            elif key == ord("u"):
                # User Timeline
                self.stdcur.addstr(0, 0, "User?: @")
                self.stdcur.clrtoeol()
                user = self.getstr()
                self.tmp.append(user)
                self.mode = 2
            elif key == ord("r"):
                # Retweet
                self.stdcur.addstr(
                    0, 0, "1: Retweets by others, 2: Retweets by you, 3: Your tweets, retweeted")
                self.stdcur.clrtoeol()

                n = -1
                while n not in (1, 2, 3):
                    n = self.stdcur.getch() - ord("0")
                
                self.mode = 3
                self.tmp.append(n)
            elif key == ord("f"):
                # Friendship
                self.stdcur.addstr(0, 0, "User?: @")
                self.stdcur.clrtoeol()
                user = self.getstr()
                self.friendship(user)
                self.stdcur.getch()
            elif key in (curses.KEY_LEFT, ord("h"), ord(" ")):
                # Home Timeline
                self.mode = 0
            elif key == ord("q"):
                # Quit
                return False
            else:
                continue

            break
                
        return True
    
    def getstr(self, *args):
        import newinput
        return newinput.mbgetstr(self.stdcur, *args).encode("utf-8")
    
    def post(self, status):
        self.stdcur.addstr(0, 0, "Updating Status...")
        self.stdcur.clrtoeol()
        self.stdcur.refresh()

        self.api.status_update(status)
        self.stdcur.addstr(" OK.")
    
    def reply(self, status):
        self.stdcur.addstr(0, 0, "Reply: ")
        self.stdcur.clrtoeol()

        name = status["user"]["screen_name"]
        reply_to = status["id"]

        replyhead = "@%s " % name
        self.stdcur.addstr(0, 7, replyhead)
        
        message = self.getstr()
        
        if message:
            self.stdcur.addstr(0, 0, "Reply... ")
            self.stdcur.clrtoeol()
            self.stdcur.refresh()

            reply = ("%s%s" % (
                    replyhead, message.decode("utf-8"))).encode("utf-8")
            post = self.api.status_update(
                reply, in_reply_to_status_id = reply_to)
            
            self.stdcur.addstr("OK. (%s)" % post["id"])
        else:
            self.stdcur.move(0, 0)
            self.stdcur.clrtoeol()

    def retweet(self, _id):
        self.stdcur.move(0, 0)
        self.stdcur.clrtoeol()
        self.stdcur.addstr("Retweet? (Y/n)")

        if self.stdcur.getch() != ord("n"):
            self.stdcur.addstr(0, 0, "Retweet... ")
            self.stdcur.clrtoeol()
            self.stdcur.refresh()

            self.api.status_retweet(_id)
            self.stdcur.addstr("OK.")
        else:
            self.stdcur.move(0, 0)
            self.stdcur.clrtoeol()

    def quotetweet(self, status):
        self.stdcur.move(0, 0)
        self.stdcur.clrtoeol()
        self.stdcur.addstr("QT: ")
        message = self.getstr().decode("utf-8")
        
        if message:
            qt = "%s QT: @%s: %s" % (
                message, status["user"]["screen_name"], status["text"])
            self.post(qt.encode("utf-8"))
        else:
            self.stdcur.move(0, 0)
            self.stdcur.clrtoeol()

    def destroy(self, status):
        self.stdcur.move(0, 0)
        self.stdcur.clrtoeol()

        if int(self.api.user["id"]) == int(status["user"]["id"]):
            self.stdcur.addstr(0, 0, "Destroy? (Y/n): ")

            if self.stdcur.getch() != ord("n"):
                self.stdcur.addstr(0, 0, "Destroying: ")
                self.stdcur.clrtoeol()
                self.stdcur.refresh()

                self.api.status_destroy(status["id"])
                self.stdcur.addstr("OK.")
            else:
                self.stdcur.move(0, 0)
                self.stdcur.clrtoeol()
        else:
            self.stdcur.addstr(0, 0, "Can't destroy this status...")
    
    def friendship(self, user):
        self.stdcur.move(0, 0)
        self.stdcur.clrtoeol()

        fr = self.api.friends_show(user)
        ed = fr["source"]["followed_by"] == "true"
        ing = fr["source"]["following"] == "true"

        if ed:
            a = "<"
        else:
            a = " "

        if ing:
            b = ">"
        else:
            b = " "

        me = self.api.user["screen_name"]
        self.stdcur.addstr("@%s %s===%s @%s" % (me, a, b, user))
            
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

            # print created_at time
            created_at = twittertime(lpost[i]["created_at"])
            puttime = str(created_at).split(".")[0]
            ago = twitterago(created_at)
            source = twittersource(lpost[i]["source"])
            # isretweet(lpost[i])

            self.footwin.addstr(0, 0, "[%s] %s from %s" % (puttime, ago, source))
            self.footwin.clrtoeol()
            
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
                # Down
                if i < Y - 1:
                    p = 1
            elif c == curses.KEY_UP:
                # Up
                if i > 0:
                    p = -1
            elif c in (curses.KEY_LEFT, curses.KEY_BACKSPACE, 0x1b):
                # Return
                break
            elif target:
                if c in (curses.KEY_ENTER, 0x0a, ord("@")):
                    # Reply
                    self.reply(target)
                elif c == ord("r"):
                    # Retweet
                    self.retweet(target["id"])
                elif c == ord("q"):
                    # Quote tweet
                    self.quotetweet(target)
                elif c in (curses.KEY_RIGHT, ord("u")):
                    # Show User Timeline
                    self.mode = 2
                    self.tmp.append(target["user"]["screen_name"])
                    break
                elif c == ord("d"):
                    # Destroy
                    self.destroy(target)
                elif c == ord("f"):
                    # Friendship
                    self.friendship(target["user"]["screen_name"])
            else:
                continue
            
            self.tlwin.move(i, 0)
            self.tlwin.clrtoeol()
            self.tlwin.addstr(s[:-1], attr)
            
            i += p
            
            #self.tlwin.move(i, 0)
            self.tlwin.refresh()
        
        return
