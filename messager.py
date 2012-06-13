from collections import deque

__author__ = 'Pavel Padinker'

class Messager():
    def __init__(self, online_users, location_users):
        self.callbacks = dict()
        self.cache = dict()
        self.online_users = online_users
        self.location_users = location_users
        pass

    def subscribe(self, name, callback):
        if name in self.cache.keys():
            callback_tmp = self.callbacks[name]
            self.callbacks[name] = None
            callback_tmp(self.cache[name].popleft())
        else:
            self.callbacks[name] = callback

    def unsubscribe(self, name):
        if name in self.callbacks:
            self.callbacks.pop(name)

    def new_message(self, user_name, message):
        to_whom = message["to"]
        if to_whom == "all":
            location_users = self.location_users[self.online_users[user_name].location]
            for location_user_name in location_users.keys():
                if location_user_name in self.callbacks.keys() and self.callbacks[location_user_name]:
                    # to avoid replacement of callback in process of callback call
                    callback_tmp = self.callbacks[location_user_name]
                    self.callbacks[location_user_name] = None
                    callback_tmp(message)
                elif location_user_name in self.cache and len(self.cache[location_user_name]) < 10:
                    self.cache[location_user_name].append(message)
                else:
                    self.cache[location_user_name] = deque()
                    self.cache[location_user_name].append(message)
        elif to_whom in self.callbacks:
            # to avoid replacement of callback in process of callback call
            callback_tmp = self.callbacks[to_whom]
            self.callbacks[to_whom] = None
            callback_tmp(message)
        elif to_whom in self.cache and len(self.cache[to_whom]) < 10:
            self.cache[to_whom].append(message)
        else:
            self.cache[to_whom] = deque()
            self.cache[to_whom].append(message)
