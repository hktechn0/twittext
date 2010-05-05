#!/usr/bin/env python
#-*- coding: utf-8 -*-

#
# Twittext - gettoken.py
# - Hirotaka Kawata <info@techno-st.net>
# - http://www.techno-st.net/wiki/Twittext
#
#    Copyright (C) 2009-2010 Hirotaka Kawata <info@techno-st.net>
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

import twoauth

def token(ckey, csecret):
    print "[Twittext OAuth Setup]"
    oa = twoauth.oauth(ckey, csecret)
    req_token = oa.request_token()
    auth_url = oa.authorize_url(req_token)
    
    print "Authorize URL (Please Allow):"
    print auth_url
    pin = raw_input("PIN: ")
    
    acc_token = oa.access_token(req_token, int(pin))
    
    atoken = acc_token["oauth_token"]
    asecret = acc_token["oauth_token_secret"]
    screen_name = acc_token["screen_name"]
    
    print "screen_name: %s" % screen_name
    
    return (atoken, asecret, screen_name)
