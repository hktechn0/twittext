#!/usr/bin/env python
#-*- coding: utf-8 -*-

#
# Twittext - tl_help.py
# - Andreas Krennmair <ak@synflood.at>
# - http://www.techno-st.net/wiki/Twittext
#
#    Copyright (C) 2010 Andreas Krennmair <ak@synflood.at>
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

def tl_help(self, helptext):
	self.tlwin.clear()

	self.tlwin.attrset(0)

	y = 0
	for line in helptext:
		self.tlwin.addstr(y, 0, line)
		y += 1

	self.tlwin.attrset(0)
	self.tlwin.refresh()

