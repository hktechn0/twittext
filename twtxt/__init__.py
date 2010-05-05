#!/usr/bin/env python

import curses
import locale

locale.setlocale(locale.LC_ALL, '')

from settings import settings
from gettoken import token

def main(conf):
    from main import Main
    m = Main(conf)
    curses.wrapper(m.start)
