#!/usr/bin/env python
#-*- coding: utf-8 -*-

import curses

def mbgetstr(stdcur, sety, setx, debug = False):
    s = u""
    i = 0
    cc = 0
    
    curses.noecho()

    # for iTerm fix
    try:
        curses.curs_set(1)
    except:
        pass

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

            if isascii(s[i - 1]):
                x -= 1
                cc -= 1
            else:
                x -= 2
                cc -= 2

            s = s[:i - 1] + s[i:]
            i -= 1
            
            stdcur.move(sety, setx)
            stdcur.clrtoeol()

            if cc + setx > maxx - 1:
                j = getoffset(s, cc, setx, maxx)
            else:
                j = 0
            
            stdcur.addstr(s[j:i].encode('utf-8'))
            (y, x) = stdcur.getyx()
            stdcur.addstr(s[i:].encode('utf-8'))
            stdcur.move(y, x)
        elif c == curses.KEY_DC:
            if i >= len(s):
                continue

            if isascii(s[i]):
                cc -= 1
            else:
                cc -= 2

            s = s[:i] + s[i + 1:]

            stdcur.move(sety, setx)
            stdcur.clrtoeol()
            
            if cc + setx > maxx - 1:
                j = getoffset(s, cc, setx, maxx)
            else:
                j = 0

            stdcur.addstr(s[j:i].encode('utf-8'))
            (y, x) = stdcur.getyx()
            stdcur.addstr(s[i:].encode('utf-8'))
            stdcur.move(y, x)
        elif c == curses.KEY_LEFT:
            if x <= setx:
                continue
            
            if isascii(s[i - 1]):
                x -= 1
            else:
                x -= 2
            
            i -= 1
            stdcur.move(y, x)
        elif c == curses.KEY_RIGHT:
            if i >= len(s):
                continue
            
            if isascii(s[i]):
                x += 1
            else:
                x += 2
            
            i += 1
            stdcur.move(y, x)
        elif curses.KEY_MIN <= c <= curses.KEY_MAX:
            pass
        else:
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
            
            if isascii(c):
                cursor = 1
                cc += 1
            else:
                cursor = 2
                cc += 2
            
            if cc + setx > maxx - 1:
                stdcur.move(sety, setx)
                stdcur.clrtoeol()
                j = getoffset(s, cc, setx, maxx)
                
                stdcur.addstr(s[j:i].encode('utf-8'))
                (y, x) = stdcur.getyx()
                stdcur.addstr(s[i:].encode('utf-8'))
                stdcur.move(y, x)
            else:
                stdcur.insstr(c.encode('utf-8'))
                stdcur.move(y, x + cursor)
    
    # for iTerm fix
    try:
        curses.curs_set(0)
    except:
        pass

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
