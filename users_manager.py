from threading import Thread
import time
from online_users_holder import Action
import smarty

__author__ = 'Pavel Padinker'

# action types are:
# 0 - show all online and skirmish users
# 1 - add new user
# 2 - remove online user
# 3 - add skirmish users
# 4 - remove skirmish users

class UsersManager(Thread):
    def __init__(self, db_manager, online_users_holder):
        Thread.__init__(self)
        self.db_manager = db_manager
        self.online_users_holder = online_users_holder

    @property
    def online_users(self):
        return self.online_users_holder.online_users

    @property
    def skirmish_users(self):
        return self.online_users_holder.skirmish_users

    def create_initial_users_action(self):
        online_user_non_skirmish = list()
        for user_name in self.online_users.keys():
            if user_name not in self.skirmish_users.keys():
                online_user_non_skirmish.append(user_name)
        skirmish_users = list()
        for user_name in self.skirmish_users:
            if not self.skirmish_users[user_name].team_name:
                skirmish_users.append(user_name)
            else:
                skirmish_users.append("%(user_name)s:%(team_name)s" % {"user_name" : user_name, "team_name" : self.online_users[user_name].team_name})
        return Action(0, {"online_users" : ','.join(online_user_non_skirmish), "skirmish_users" : ','.join(skirmish_users)})

    def create_user_online_action(self, user_name):
        return Action(1, {"user" : user_name})

    def create_user_offline_action(self, user_name):
        return Action(2, {"user" : user_name})

    def create_add_skirmish_user_action(self, user_name):
        if not self.online_users[user_name].character.team_name:
            return Action(3, {"skirmish_user" : user_name})
        return Action(3, {"skirmish_user" : "%(user_name)s:%(team_name)s" % {"user_name" : user_name, "team_name" : self.online_users[user_name].character.team_name}})

    def create_remove_skirmish_user_action(self, user_name):
        if not self.online_users[user_name].character.team_name:
            return Action(4, {"skirmish_user" : user_name})
        return Action(4, {"skirmish_user" : "%(user_name)s:%(team_name)s" % {"user_name" : user_name, "team_name" : self.online_users[user_name].character.team_name}})


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

    def user_join_skirmish(self, user_name):
        self.send_action_to_all(self.create_add_skirmish_user_action(user_name))

    def user_leave_skirmish(self, user_name):
        self.send_action_to_all(self.create_remove_skirmish_user_action(user_name))

    def subscribe(self, user_name, callback, locale):
        self.online_users_holder.add_if_not_online(user_name, self.db_manager, locale)
        self.online_users[user_name].set_user_callback(callback)

    def unsubscribe(self, user_name):
        if user_name in self.online_users:
            self.online_users[user_name].set_user_callback(None)

    def send_initial_users_to(self, user_name):
        self.online_users[user_name].send_user_action(self.create_initial_users_action())

    def send_action_to_all(self, action):
        for online_user in self.online_users.values():
            online_user.send_user_action(action)

    def on_user_online(self, user_name):
        self.send_action_to_all(self.create_user_online_action(user_name))

    def on_user_offline(self, user_name):
        self.send_action_to_all(self.create_user_offline_action(user_name))
