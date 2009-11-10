#!/usr/bin/env python
#-*- coding: utf-8 -*-

import curses

def mbgetstr(stdcur, sety, setx, debug = False):
    s = u""
    i = 0
    
    curses.noecho()
    curses.curs_set(1)
    (maxy, maxx) = stdcur.getmaxyx()
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
            if x <= setx:
                continue

            if isascii(s[i - 1], True):
                x -= 1
            else:
                x -= 2

            s = s[:i - 1] + s[i:]
            i -= 1
            
            stdcur.move(y, setx)
            stdcur.clrtoeol()
            stdcur.addstr(s.encode("utf-8"))
            stdcur.move(y, x)
        elif c == curses.KEY_DC:
            if i >= len(s):
                continue

            s = s[:i] + s[i + 1:]

            stdcur.move(y, setx)
            stdcur.clrtoeol()
            stdcur.addstr(s.encode("utf-8"))
            stdcur.move(y, x)
        elif c == curses.KEY_LEFT:
            if x <= setx:
                continue
            elif isascii(s[i - 1], True):
                x -= 1
            else:
                x -= 2

            i -= 1
            stdcur.move(y, x)
        elif c == curses.KEY_RIGHT:
            if i >= len(s):
                continue
            if isascii(s[i], True):
                x += 1
            else:
                x += 2
            
            i += 1
            stdcur.move(y, x)
        elif curses.KEY_MIN <= c <= curses.KEY_MAX:
            pass
        else:
            if c & 0x80:
                cc = c << 1
                while cc & 0x80:
                    cc <<= 1
                    c <<= 8
                    c += (stdcur.getch() & 0xff)

            c = utf2ucs(c)
            s = s[:i] + c + s[i:]
            stdcur.insstr(c.encode("utf-8"))
            i += 1
            
            if isascii(c, True):
                stdcur.move(y, x + 1)
            else:
                stdcur.move(y, x + 2)

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

def isascii(c, printable = False):
    if 0x00 <= ord(c) <= 0x7f:
        if printable:
            if 0x20 <= ord(c) <= 0x7e:
                return True
            else:
                return False
        else:
            return True
    else:
        return False

def _test(stdcur):
    curses.use_default_colors()
    stdcur.addstr(0, 0, "=== Mutibyte getstr() Test ===")
    stdcur.addstr(1, 0, "input?: ")
    stdcur.refresh()
    s = mbgetstr(stdcur, 1, 8, True)
    stdcur.addstr(2, 0, s.encode("utf-8"))
    stdcur.getch()

if __name__ == '__main__':
    import locale
    locale.setlocale(locale.LC_ALL, "")
    curses.wrapper(_test)
