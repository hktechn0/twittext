#!/usr/bin/env python
#-*- coding: utf-8 -*-
#
# Twittext - select.py
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

from tools import *
from newinput import *

def tl_select(self, lpost):
    self.tlwin.move(0, 0)
    self.tlwin.refresh()
    (Y, X) = (self.Y - 3, self.X)

    # if Direct Messages?
    if "sender" in lpost[0].keys():
        dm = True
        for m in lpost:
            m["user"] = m["sender"]
    else:
        dm = False

    i = 0

    while True:
        attr = attr_select(lpost[i], self.api.user) & 0xffffff00

        s = self.tlwin.instr(i, 0)

        self.tlwin.move(i, 0)
        self.tlwin.clrtoeol()

        if i + 1 >= Y:
            # last row fix
            self.tlwin.addstr(s[:-1], attr | curses.A_STANDOUT)
        else:
            self.tlwin.addstr(s, attr | curses.A_STANDOUT)

        #self.tlwin.move(i, 0)
        self.tlwin.refresh()

        # print screen_name
        u = lpost[i]["user"]
        p = u"[Protected]" if u["protected"] == u"true" else u""
        h = u"@%s (%s) %s" % (u["screen_name"], u["name"], p)
        self.stdcur.addstr(0, 0, h.encode("utf-8"))
        self.stdcur.clrtoeol()
        self.stdcur.refresh()

        # print created_at time
        self.footwin.addstr(0, 0, str(statusinfo(lpost[i]).encode("utf-8")))
        self.footwin.clrtoeol()

        curses.flushinp()
        c = self.stdcur.getch(0, 0)

        if len(lpost) <= i:
            target = None
        else:
            target = lpost[i]

        # cursor point
        p = 0

        if c == curses.KEY_DOWN:
            # Down
            if i < Y - 1 and i < len(lpost) - 1:
                p = 1
            elif i == Y - 1:
                # scroll
                self.mode = self.oldmode
                self.tmp = list(self.oldtmp)
                self.max_id = target["id"]
                self.since_id = ""
                self.hist.append(lpost[0]["id"])
                break
        elif c == curses.KEY_UP:
            # Up
            if i > 0:
                p = -1
            elif self.hist:
                # scroll
                self.mode = self.oldmode
                self.tmp = list(self.oldtmp)
                self.max_id = self.hist.pop()
                self.since_id = ""
                break
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
            elif c == ord("U"):
                # Show reply_to User Timeline
                user = split_user(target["text"])
                if user:
                    self.mode = 2
                    self.tmp.append(user)
                    break
                else:
                    continue
            elif c == ord("d"):
                # Destroy
                self.destroy(target)
            elif c == ord("D"):
                # Direct Message
                self.dmessage(target["user"]["screen_name"])
            elif c == ord("f"):
                # Favorite
                self.stdcur.addstr(0, 0, "Favorite: ")
                self.stdcur.clrtoeol()
                self.api.favorite_create(target["id"])
                self.stdcur.addstr("OK. (%s)" % target["id"])
                self.stdcur.getch()
            elif c == ord("F"):
                # Friendship
                self.friendship(target["user"]["screen_name"])
            elif c == ord("t"):
                # Show reply_to
                if target["in_reply_to_status_id"]:
                    self.detail(
                        self.api.status_show(
                            target["in_reply_to_status_id"]))
                    break
                else:
                    continue
            else:
                continue
        else:
            continue

        self.tlwin.move(i, 0)
        self.tlwin.clrtoeol()

        if i + 1 >= Y:
            # last row fix
            self.tlwin.addstr(s[:-1], attr)
        else:
            self.tlwin.addstr(s, attr)

        i += p

        #self.tlwin.move(i, 0)
        self.tlwin.refresh()

    return
