#!/usr/bin/env python

import UserDict

class settings(UserDict.UserDict):
    def __init__(self, initialdata):
        UserDict.UserDict.__init__(self, initialdata)
        #self.data = dict(initialdata)
        self.user = self["default_user"]
    
    def uget(self, key, x = None):
        uset = self["user"][self.user]
        return uset[key] if key in uset else x
    
    def get_consumer(self):
        return (self.get("ckey"), self.get("csecret"))

    def get_token(self):
        return self.get_consumer() + (self.uget("atoken"), self.uget("asecret"))

    def get_screen_name(self):
        return self.user
    
    def add_user(self, atoken, asecret, screen_name, footer = ""):
        if "user" not in self.data:
            self.user = screen_name
            self["default_user"] = screen_name
            self["user"] = dict()
        self["user"][screen_name] = dict()
        self["user"][screen_name]["atoken"] = atoken
        self["user"][screen_name]["asecret"] = atoken
        self["user"][screen_name]["footer"] = footer
    
    def change_user(self, screen_name):
        self.user = screen_name
    
    @classmethod
    def open(cls, path = ""):
        fp = open(path, "r")
        s = eval(fp.read())
        fp.close()

        d = cls(s)
        d.savepath = path
        
        return d
    
    def save(self, path = None):
        if path != None: self.savepath = path
        
        fp = open(self.savepath, "w")
        fp.write(str(self.data))
        fp.close()
