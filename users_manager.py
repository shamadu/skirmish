from threading import Thread
import time
from online_users_holder import Action
import smarty

__author__ = 'Pavel Padinker'

# action types are:
# 0 - show all online users
# 1 - add new user
# 2 - remove online user

class UsersManager(Thread):
    def __init__(self, db_manager, online_users_holder):
        Thread.__init__(self)
        self.db_manager = db_manager
        self.online_users_holder = online_users_holder

    @property
    def online_users(self):
        return self.online_users_holder.online_users

    def run(self):
        while 1:
            for user_name in self.online_users.keys():
                if not self.online_users[user_name].user_callback and not self.online_users[user_name].skirmish_callback and not self.online_users[user_name].character_callback:
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
        user = self.db_manager.get_user(login)
        if not user:
            # no such user - add new one
            self.db_manager.add_user(login, password)
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

    def subscribe(self, user_name, callback, locale):
        self.online_users_holder.add_if_not_online(user_name, locale)
        self.online_users[user_name].set_user_callback(callback)

    def unsubscribe(self, user_name):
        if user_name in self.online_users:
            self.online_users[user_name].set_user_callback(None)

    def send_online_users_to(self, user_name):
        self.online_users[user_name].send_user_action(Action(0, {"users" : ','.join(self.online_users.keys())}))

    def on_user_online(self, user_name):
        for online_user in self.online_users.values():
            online_user.send_user_action(Action(1, {"user" : user_name}))

    def on_user_offline(self, user_name):
        for online_user in self.online_users.values():
            online_user.send_user_action(Action(2, {"user" : user_name}))

    def user_enter(self, user_name, locale):
        self.online_users_holder.add_if_not_online(user_name, locale)
