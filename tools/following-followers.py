#!/usr/bin/env python
#-*- coding: utf-8 -*-

import twitter

from config import *

DEBUG = True

api = twitter.Api(username = USER, password = PASS)
me = api.GetUser(USER)

print "Following: %d, Followers: %d" % (
    me.friends_count, me.followers_count)

following = []
followers = []
already_get_ers = 0
already_get_ing = 0
i = 1

while True:
    if DEBUG:
        print i,

    if me.followers_count > len(following):
        following.extend(api.GetFriends(page = i))

    if me.friends_count > len(followers):
        followers.extend(api.GetFollowers(page = i))

    if ((already_get_ing == len(following))
        and (already_get_ers == len(followers))):
        break
    else:
        already_get_ing = len(following)
        already_get_ers = len(followers)
        i += 1

        if DEBUG:
            print len(following), len(followers)

print "Get Following: %d" % len(following)
print "Get Followers: %d" % len(followers)

print "\n(Following) - (Followers) ====="
for user in following:
    found = False
    
    for user2 in followers:
        if user.id == user2.id:
            found = True
            break
    
    if found == False:
        print user.screen_name
