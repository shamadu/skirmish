from threading import Thread
import time
import smarty

__author__ = 'Pavel Padinker'

class OnlineUser():
    def __init__(self):
        self.counter = 10

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
            self.unsubscribe(name)
            self.send_online_users()
            self.battle_bot.user_offline(name)

    def subscribe(self, name, callback):
        if not name in self.online_users.keys():
            self.online_users[name] = OnlineUser()
            self.online_users[name].callback = callback
            self.send_online_users()
        else:
            self.online_users[name].callback = callback

    def unsubscribe(self, name):
        if name in self.online_users:
            self.online_users[name].callback = None

    def send_online_users(self):
        for online_user in self.online_users.values():
            if online_user.callback:
                callback_tmp = online_user.callback
                online_user.callback = None
                callback_tmp(', '.join(self.online_users.keys()))

