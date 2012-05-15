from collections import deque
from threading import Thread
import time
import smarty

__author__ = 'Pavel Padinker'

class Action:
    def __init__(self, type, args):
        # types are:
        # 0 - show all online users
        # 1 - add new user
        # 2 - remove online user
        self.type = type
        self.args = args
        self.args["type"] = type

class OnlineUser():
    def __init__(self):
        self.counter = 10
        self.callback = None
        self.cache = deque()

    def set_callback(self, callback):
        self.counter = 10
        if len(self.cache) != 0 and callback:
            callback(self.cache.popleft())
        else:
            self.callback = callback

    def send_action(self, action):
        if self.callback:
            # to avoid replacement of callback in process of callback call
            callback_tmp = self.callback
            self.callback = None
            callback_tmp(action)
        else:
            self.add_to_cache(action)

    def add_to_cache(self, action):
        self.cache.append(action)

class UsersManager(Thread):
    def __init__(self, db, battle_bot):
        Thread.__init__(self)
        self.db = db
        self.online_users = dict()
        self.battle_bot = battle_bot
        self.db.execute("create table if not exists users (id integer(11) primary key not null auto_increment unique, "
                        "login text, password text)")

    def run(self):
        while 1:
            for user_name in self.online_users.keys():
                if not self.online_users[user_name].callback:
                    if not self.online_users[user_name].counter:
                        self.user_offline(user_name)
                    else:
                        self.online_users[user_name].counter -= 1

            time.sleep(1)
            pass

    def user_login(self, login, password):
        login_response = {
            'error': False,
            'msg': ''
        }

        # try to find user with this login in db:
        user = self.db.get("select * from users where login = %s", login)
        if not user:
            # no such user - insert the new one
            self.db.execute("insert into users (login, password) values (%s, %s)", login, password)
        elif user["password"] != password:
            login_response["error"] = True
            login_response["msg"] = smarty.error_messages[2]

        if not login_response["error"]:
            login_response["msg"] = login

        return login_response

    def user_logout(self, login):
        self.user_offline(login)

    def user_offline(self, name):
        if name in self.online_users.keys():
            self.online_users.pop(name)
            self.on_user_offline(name)
            self.battle_bot.user_offline(name)

    def subscribe(self, user_name, callback):
        if not user_name in self.online_users.keys():
            self.on_user_online(user_name)
            self.online_users[user_name] = OnlineUser()
            self.send_online_users_to(user_name)
        self.online_users[user_name].set_callback(callback)

    def unsubscribe(self, user_name):
        if user_name in self.online_users:
            self.online_users[user_name].set_callback(None)

    def send_online_users_to(self, user_name):
        self.online_users[user_name].send_action(Action(0, {"users" : ','.join(self.online_users.keys())}))

    def on_user_online(self, user_name):
        for online_user in self.online_users.values():
            online_user.send_action(Action(1, {"user" : user_name}))

    def on_user_offline(self, user_name):
        for online_user in self.online_users.values():
            online_user.send_action(Action(2, {"user" : user_name}))

    def user_enter(self, user_name):
        if not user_name in self.online_users.keys():
            self.on_user_online(user_name)
            self.online_users[user_name] = OnlineUser()
        self.send_online_users_to(user_name)
