from collections import deque
from threading import Thread
import time

__author__ = 'Pavel'

class BattleBot(Thread):
    def __init__(self):
        Thread.__init__(self)
        self.skirmish_users = list()
        self.callbacks = dict()
        self.cache = dict()

    def run(self):
        while 1:
            time.sleep(1)
            pass

    def user_join(self, name):
        if not name in self.skirmish_users:
            self.skirmish_users.append(name)
            self.send_skirmish_users()

    def user_leave(self, name):
        if name in self.skirmish_users:
            self.skirmish_users.remove(name)
            self.send_skirmish_users()

    def get_user_status(self, name):
        if name in self.skirmish_users:
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
        action = {"skirmish_users" : ', '.join(self.skirmish_users)}
        for skirmish_user in self.callbacks.keys():
            if self.callbacks[skirmish_user]:
                callback_tmp = self.callbacks[skirmish_user]
                self.callbacks[skirmish_user] = None
                callback_tmp(action)

    def send_skirmish_users_to(self, name):
        action = {"skirmish_users" : ', '.join(self.skirmish_users)}
        if not name in self.cache or not self.cache[name]:
            self.cache[name] = deque()
        self.cache[name].append(action)
