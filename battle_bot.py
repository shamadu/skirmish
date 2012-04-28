from collections import deque
from threading import Thread
import time

__author__ = 'Pavel Padinker'

class Action:
    def __init__(self, for_all, type, args):
        self.for_all = for_all
        self.type = type
        self.args = args

class UserInfo:
    def __init__(self):
        self.action = ""

class BattleBot(Thread):
    def __init__(self):
        Thread.__init__(self)
        self.skirmish_users = dict()
        self.callbacks = dict()
        self.cache = dict()

    def run(self):
        while 1:
            time.sleep(1)
            pass

    def user_join(self, name):
        if not name in self.skirmish_users.keys():
            self.skirmish_users[name] = UserInfo()
            self.send_skirmish_users()

            action = Action(
                False,
                "show_div_action",
                    {"actions" : {
                    "attack" : 2,
                    "defence" : 3,
                    "spell" : 1,
                    "mana" : 0,
                    },
                     "users" : {"a", "bbbbbbbbbbbbbbbb", "c"}
                }
            )
            self.send_action_to(name, action)


    def user_leave(self, name):
        if name in self.skirmish_users.keys():
            action = Action(
                False,
                "hide_div_action",
                    {}
            )
            self.send_action_to(name, action)
            self.skirmish_users.pop(name)
            self.send_skirmish_users()

    def get_user_status(self, name):
        if name in self.skirmish_users.keys():
            return 'battle'
        else:
            return 'rest'

    def subscribe(self, name, callback):
        if name in self.cache.keys() and self.cache[name]:
            callback(self.cache[name].popleft())
        else:
            self.callbacks[name] = callback

    def unsubscribe(self, name):
        if name in self.callbacks.keys():
            self.callbacks[name] = None

    def send_skirmish_users(self):
        action = Action(True, "show_skirmish_users", {"skirmish_users" : ', '.join(self.skirmish_users.keys())})
        self.send_action(action)

    def send_action(self, action):
        if action.for_all:
            users = self.callbacks.keys()
        else:
            users = self.skirmish_users.keys()

        for skirmish_user in users:
            if self.callbacks[skirmish_user]:
                callback_tmp = self.callbacks[skirmish_user]
                self.callbacks[skirmish_user] = None
                callback_tmp(action)
            else:
                if not skirmish_user in self.cache or not self.cache[skirmish_user]:
                    self.cache[skirmish_user] = deque()
                self.cache[skirmish_user].append(action)

    def send_action_to(self, name, action):
        if self.callbacks[name]:
            callback_tmp = self.callbacks[name]
            self.callbacks[name] = None
            callback_tmp(action)
        else:
            if not name in self.cache or not self.cache[name]:
                self.cache[name] = deque()
            self.cache[name].append(action)

    def reenter_from_user(self, name):
        action = Action(True, "show_skirmish_users", {"skirmish_users" : ', '.join(self.skirmish_users.keys())})
        if not name in self.cache or not self.cache[name]:
            self.cache[name] = deque()
        self.cache[name].append(action)
