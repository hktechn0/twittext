#!/usr/bin/env python
#-*- coding: utf-8 -*-

#
# Twittext - show.py
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

def tl_show(self, tl):
    self.tlwin.clear()

    # if Direct Messages?
    if "sender" in tl[0].keys() if tl else ():
        dm = True
        for m in tl:
            m["user"] = m["sender"]
    else:
        dm = False

    ret = list()
    i = 0
    for s in tl[::-1]:
        # curses attr (color)
        attr = attr_select(s, self.api.user)

        # new status
        if self.newcnt:
            self.newcnt -= 1
            if attr == curses.A_NORMAL:
                attr = curses.A_BOLD | curses.color_pair(5)
            else:
                attr |= curses.A_BOLD

        # set attr
        self.tlwin.attrset(attr)

        # print screen_name
        sname = "[%7s] " % (s["user"]["screen_name"][0:7])
        self.tlwin.addstr(i, 0, sname)

        # escape status text
        raw_str = s["text"]
        raw_str = replace_htmlentity(raw_str)
        raw_str = delete_notprintable(raw_str)

        (Y, X) = (self.Y - 3, self.X)

        # split status text
        sss = split_text(raw_str, X - len(sname))
        sss = sss[0:Y - i]

        for ss in sss:
            if i + 1 >= Y and cw_count(ss) + 10 >= X:
                # last row fix
                ss = ss[:-1]
            self.tlwin.addstr(i, 10, ss.encode("utf-8"))
            ret.append(s)
            i += 1

        if Y <= i:
            break

    # dispose...
    self.tlwin.attrset(0)
    self.tlwin.refresh()

    return ret
