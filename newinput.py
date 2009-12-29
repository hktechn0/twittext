#!/usr/bin/env python
#-*- coding: utf-8 -*-

#
# Twittext
# curses.getstr() for UTF-8
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

# usage: newinput.mbgetstr(win, [y, x])
def mbgetstr(stdcur, sety = None, setx = None, debug = False):
    s = u""
    i = 0
    
    curses.noecho()
    curses.curs_set(1)
    
    (maxy, maxx) = stdcur.getmaxyx()

    if sety == None and setx == None:
        (sety, setx) = stdcur.getyx()
    else:
        stdcur.move(sety, setx)
    
    while True:
        (y, x) = stdcur.getyx()
        
        # Debug
        if debug:
            stdcur.addstr(maxy - 1, 0, str(i) + "\t%s" % s.encode("utf-8"))
            stdcur.clrtoeol()
            stdcur.move(y, x)
        
        c = stdcur.getch()

        if c == 0x0a:
            break
        elif c == curses.KEY_BACKSPACE:
            if i <= 0:
                continue
            
            s = s[:i - 1] + s[i:]
            i -= 1
            rewrite_text(stdcur, setx, sety, s, i)
        elif c == curses.KEY_DC:
            s = s[:i] + s[i + 1:]
            rewrite_text(stdcur, setx, sety, s, i)
        elif c == curses.KEY_LEFT:
            if i <= 0:
                continue
            
            i -= 1
            rewrite_text(stdcur, setx, sety, s, i)
        elif c == curses.KEY_RIGHT:
            if i >= len(s):
                continue
            
            i += 1
            rewrite_text(stdcur, setx, sety, s, i)
        elif curses.KEY_MIN <= c <= curses.KEY_MAX:
            pass
        else:
            # UTF-8 input
            if c & 0x80:
                f = c << 1
                while f & 0x80:
                    f <<= 1
                    c <<= 8
                    c += (stdcur.getch() & 0xff)
            
            c = utf2ucs(c)
            
            if isascii(c) and not(isprintable(c)):
                continue
            
            s = s[:i] + c + s[i:]
            i += 1
            rewrite_text(stdcur, setx, sety, s, i)
    
    curses.curs_set(0)

    return s

def utf2ucs(utf):
    if utf & 0x80:
        # multibyte
        buf = []
        while not(utf & 0x40):
            buf.append(utf & 0x3f)
            utf >>= 8
        buf.append(utf & (0x3f >> len(buf)))

        ucs = 0
        while buf != []:
            ucs <<= 6
            ucs += buf.pop()
    else:
        # ascii
        ucs = utf
    
    return unichr(ucs)

def isascii(c):
    if 0x00 <= ord(c) <= 0x7f:
        return True
    else:
        return False

def isprintable(c):
    if 0x20 <= ord(c) <= 0x7e:
        return True
    else:
        return False

# no use....
def getoffset(s, cc, setx, maxx):
    w = 0
    j = 0

    for ic in s:
        j += 1
        
        if isascii(ic):
            w += 1
        else:
            w += 2
            
        if w > cc + setx - maxx:
            break

    return j

# Character width count
# no use...
def cw_count(string):
    cnt = 0

    for c in string:
        if isascii(c):
            cnt += 1
        else:
            cnt += 2
    
    return cnt

# Extract string by width
def exstr_width(string, cnt):
    width = 0
    i = 0

    for c in string:
        if isascii(c):
            width += 1
        else:
            width += 2

        if width >= cnt:
            break
        else:
            i += 1

    return string[:i]

def rewrite_text(stdcur, setx, sety, s, i):
    (maxy, maxx) = stdcur.getmaxyx()
    (os, oe) = rewrite_text.old

    stdcur.move(sety, setx)
    stdcur.clrtoeol()

    if os <= i <= oe:
        stdcur.addstr(s[os:i].encode('utf-8'))
        (y, x) = stdcur.getyx()
        exstr = exstr_width(s[i:], maxx - x)
        stdcur.addstr(exstr.encode('utf-8'))
        stdcur.move(y, x)
        rewrite_text.old = (os, i + len(exstr))
    else:
        if i < os:
            exstr = exstr_width(s[i:], maxx - setx)
            rewrite_text.old = (i, i + len(exstr))
            stdcur.addstr(exstr.encode('utf-8'))
            stdcur.move(sety, setx)
        else:
            exstr = exstr_width(s[i - 1::-1], cw_count(s[os:oe]) + 3)
            exstr = exstr_width(exstr, maxx - setx)
            exstr = exstr[::-1]
            rewrite_text.old = (i - len(exstr), i)
            stdcur.addstr(exstr.encode('utf-8'))

def _test(stdcur):
    curses.use_default_colors()
    stdcur.addstr(0, 0, "=== Mutibyte getstr() Test ===")
    stdcur.addstr(1, 0, "input?: ")
    stdcur.refresh()
    s = mbgetstr(stdcur, 1, 8, True)
    stdcur.addstr(2, 0, s.encode("utf-8"))
    stdcur.getch()

# init
rewrite_text.old = (-1, -1)

if __name__ == '__main__':
    import locale
    locale.setlocale(locale.LC_ALL, "")
    curses.wrapper(_test)
