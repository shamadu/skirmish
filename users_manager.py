from threading import Thread
import time
from users_holder import Action
from users_holder import OnlineUserInfo
import smarty

__author__ = 'Pavel Padinker'

class UsersManager(Thread):
# user action types are:
# 100 - show all online and skirmish users
# 101 - add new user
# 102 - remove online user
    def initial_users_action(self, online_users, skirmish_users):
        online_user_non_skirmish = list()
        for user_name in online_users.keys():
            if user_name not in skirmish_users.keys():
                online_user_non_skirmish.append(user_name)
        skirmish_users_list = list()
        for user_name in skirmish_users:
            if not skirmish_users[user_name].character.team_name:
                skirmish_users_list.append(user_name)
            else:
                skirmish_users_list.append("%(user_name)s:%(team_name)s" % {"user_name" : user_name, "team_name" : skirmish_users[user_name].character.team_name})
        return Action(100, {"online_users" : ','.join(online_user_non_skirmish), "skirmish_users" : ','.join(skirmish_users_list)})

    def user_online_action(self, user_name):
        return Action(101, {"user" : user_name})

    def user_offline_action(self, user_name):
        return Action(102, {"user" : user_name})

    def open_chat_action(self, user_name, message):
        return Action(103, {"user" : user_name, "message" : message})

    def __init__(self, db_manager, users_holder, battle_manager):
        Thread.__init__(self)
        self.db_manager = db_manager
        self.battle_manager = battle_manager
        self.users_holder = users_holder

    @property
    def online_users(self):
        return self.users_holder.online_users

    @property
    def location_users(self):
        return self.users_holder.location_users

    def run(self):
        while 1:
            for user_name in self.online_users.keys():
                if not self.online_users[user_name].callback:
                    if not self.online_users[user_name].counter:
                        self.user_logout(user_name)
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

    def user_logout(self, user_name):
        if user_name in self.online_users.keys():
            self.remove_online_user(user_name)

    def user_enter(self, user_name):
        location = self.online_users[user_name].location
        online_users = self.location_users[location]
        skirmish_users = self.battle_manager.battle_bots[location].battle_users
        self.online_users[user_name].send_action(self.initial_users_action(online_users, skirmish_users))
        for chat_user_name in self.online_users[user_name].opened_chats:
            self.online_users[user_name].send_action(self.open_chat_action(chat_user_name, ""))

    def change_location(self, user_name, location):
        online_users = self.location_users[self.online_users[user_name].location]
        self.send_action_to_all(online_users, self.user_offline_action(user_name))
        if user_name not in self.battle_manager.battle_bots[location].skirmish_users.keys():
            self.send_action_to_all(self.location_users[location], self.user_online_action(user_name))
        self.location_users[self.online_users[user_name].location].pop(user_name)
        self.location_users[location][user_name] = self.online_users[user_name]
        self.online_users[user_name].location = location
        self.users_holder.user_enter(user_name)

    def add_online_user(self, user_name, locale):
        user = self.db_manager.get_user(user_name)
        online_users = self.location_users[user.location]
        self.send_action_to_all(online_users, self.user_online_action(user_name))
        self.online_users[user_name] = OnlineUserInfo(user_name, user.location, locale)
        self.location_users[user.location][user_name] = self.online_users[user_name]

    def remove_online_user(self, user_name):
        self.db_manager.update_user_location(user_name, self.online_users[user_name].location)
        online_users = self.location_users[self.online_users[user_name].location]
        self.send_action_to_all(online_users, self.user_offline_action(user_name))
        self.online_users.pop(user_name)
        online_users.pop(user_name)

    def user_logout(self, user_name):
        if user_name in self.online_users.keys():
            self.remove_online_user(user_name)

    def send_action_to_all(self, online_users, action):
        for online_user in online_users.values():
            online_user.send_action(action)

    def open_chat(self, user_name, chat_user_name, message):
        if user_name != chat_user_name and chat_user_name not in self.online_users[user_name].opened_chats:
            self.online_users[user_name].opened_chats.append(chat_user_name)
            self.online_users[user_name].send_action(self.open_chat_action(chat_user_name, message))

    def close_chat(self, user_name, chat_user_name):
        if chat_user_name in self.online_users[user_name].opened_chats:
            self.online_users[user_name].opened_chats.remove(chat_user_name)
