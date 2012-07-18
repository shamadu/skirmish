from collections import deque
from threading import Thread
import time
from users_holder import Action
from users_holder import OnlineUserInfo
import smarty

__author__ = 'Pavel Padinker'

class UsersManager(Thread):
# user action types are:
# 101 - add new user
# 102 - remove online user
    def user_online_action(self, user_name, type):
        return Action(101, {"user_name" : user_name, "user_type" : type})

    def user_offline_action(self, user_name):
        return Action(102, {"user_name" : user_name})

    def open_chat_action(self, user_name, message):
        return Action(103, {"user" : user_name, "message" : message})

    def user_team_online_action(self, user_name):
        return Action(104, {"user_name" : user_name})

    def user_team_offline_action(self, user_name):
        return Action(105, {"user_name" : user_name})

    def __init__(self, db_manager, users_holder, characters_manager, battle_manager):
        Thread.__init__(self)
        self.db_manager = db_manager
        self.characters_manager = characters_manager
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
        for chat_user_name in self.online_users[user_name].opened_chats:
            self.online_users[user_name].send_action(self.open_chat_action(chat_user_name, ""))

    def change_location(self, user_name, location):
        user = self.online_users[user_name]
        online_users = self.location_users[user.location]
        self.send_action_to_all(online_users, self.user_offline_action(user_name))
        if user_name not in self.battle_manager.battle_bots[location].battle_users.keys():
            for online_user in self.location_users[location].values():
                type = 2
                if online_user.character.team_name and (user.character.team_name == online_user.character.team_name):
                    type = 1
                online_user.send_action(self.user_online_action(user_name, type))
        self.location_users[user.location].pop(user_name)
        self.location_users[location][user_name] = user
        self.db_manager.update_user_location(user_name, location)
        self.on_user_enter(user_name, user.locale)

    def on_user_enter(self, user_name, locale):
        new_user = False
        if not user_name in self.online_users.keys():
            new_user = True
            user = self.db_manager.get_user(user_name)
            self.online_users[user_name] = OnlineUserInfo(user_name, user.location, locale)
            self.location_users[user.location][user_name] = self.online_users[user_name]
        if self.online_users[user_name].state != 1:
            self.db_manager.update_character(user_name)
        if new_user: # new user
            user = self.online_users[user_name]
            # send everyone in his location that he is online
            for online_user in self.location_users[user.location].values():
                type = 2
                if online_user.character.team_name and (user.character.team_name == online_user.character.team_name):
                    type = 1
                online_user.send_action(self.user_online_action(user_name, type))
            # send every his online team mate that he is online
            if self.online_users[user_name].character.team_name:
                self.send_action_to_all(self.get_online_team_members(user, self.online_users), self.user_team_online_action(user_name))
        self.online_users[user_name].cache = deque()
        self.user_enter(user_name)
        self.characters_manager.user_enter(user_name)
        self.battle_manager.user_enter(user_name)

    def remove_online_user(self, user_name):
        user = self.online_users[user_name]
        online_users = self.location_users[user.location]
        self.send_action_to_all(online_users, self.user_offline_action(user_name))
        if user.character.team_name:
            self.send_action_to_all(self.get_online_team_members(user, self.online_users), self.user_team_offline_action(user_name))
        self.online_users.pop(user_name)
        online_users.pop(user_name)

    def get_online_team_members(self, user, online_users):
        team = dict()
        for online_user in online_users.values():
            if online_user.character.team_name == user.character.team_name:
                team[online_user.user_name] = online_user
        return team

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
