#!/usr/bin/env python
#-*- coding: utf-8 -*-

import sys
import time
import mutex
import threading

import twoauth
import cursestools as ctools

# Twitter API Class
class twitterapi():
    def __init__(self, keys, maxn = 20):
        # Generate API Library instance
        self.api = twoauth.api(*keys)
#        self.api.initialize()
        self.threads = list()
        
        # User, Status Buffer
        self.users = dict()
        self.statuses = dict()
        
        self.maxn = maxn
#        self.myid = self.api.user.id
#        self.users[self.myid] = self.api.user
    
    def create_timeline(self, func, interval, args = (), kwargs = {}):
        # Add New Timeline Thread
        th = timeline_thread(getattr(self.api, func),
                             interval, self.maxn, args, kwargs)
        th.added_event = self.add_status
        th.statuses = self.statuses
        self.threads.append(th)
        return th
    
    def add_statuses(self, slist):
        for i in slist:
            self.add_status(i)
    
    def add_status(self, status):
        self.statuses[status.id] = status
        self.add_user(status.user)
    
    def add_user(self, user):
        self.users[user.id] = user

    def get_user_from_screen_name(self, screen_name):
        # search user from screen_name
        for user in self.users.itervalues():
            if user.screen_name == screen_name:
                return user
        
        return None

    def get_statuses(self, ids):
        return tuple(self.statuses[i] for i in sorted(tuple(ids), reverse=True))

# Timeline Thread
class timeline_thread(threading.Thread):
    def __init__(self, func, interval, maxn, args, kwargs):
        # Thread Initialize
        threading.Thread.__init__(self)
        self.setDaemon(True)
        
        # Event lock
        self.lock = threading.Event()
        self.addlock = mutex.mutex()
        
        self.func = func
        self.interval = interval
        self.lastid = None
        self.timeline = set()
        
        # API Arguments
        self.args = args
        self.kwargs = kwargs
        self.kwargs["count"] = maxn
    
    # Thread run
    def run(self):
        # extract cached status if gets user_timeline
        if self.func.func_name == "user_timeline":
            cached = set()
            for i in self.statuses.itervalues():
                if i.user.id == self.kwargs["user"]:
                    cached.add(i.id)
            
            if cached:
                self.add(cached)
        
        while True:
            try:
                # Get Timeline
                last = self.func(*self.args, **self.kwargs)
            except Exception, e:
                last = None
                ctools.dputs("[Error] TwitterAPI ")
                ctools.dputs(e)
                ctools.dputs(self.func)
            
            self.on_timeline_refresh()
            
            # If Timeline update
            if last:
                # Append status cache
                new = set()
                for i in last:
                    new.add(i.id)
                    self.added_event(i)
                
                # Add statuses to timeline
                self.add(new)
                
                # update lastid
                self.lastid = last[-1].id
                self.kwargs["since_id"] = self.lastid
            
            # debug print
#            print "[debug] reload", time.strftime("%H:%M:%S"),
#            print self.func.func_name, self.args, self.kwargs
            
            # Reload lock
            self.lock.clear()
            if self.interval != -1:
                self.lock.wait(self.interval)
            else:
                self.lock.wait()
    
    def add(self, ids):
        # mutex lock
        self.addlock.lock(self.add_mutex, ids)
    
    def add_mutex(self, ids):
        # defference update = delete already exists status
        ids.difference_update(self.timeline)
        if ids:
            # exec EventHander (TreeView Refresh)
            self.reloadEventHandler(ids)
            # add new statuse ids
            self.timeline.update(ids)
        
        self.addlock.unlock()

    def on_timeline_refresh(self): pass
    def reloadEventHandler(self): pass
