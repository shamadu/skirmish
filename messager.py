from collections import deque
from users_holder import Action

__author__ = 'Pavel Padinker'

class Messager():
    def message_action(self, message):
        return Action(300, message)

    def __init__(self, online_users, location_users):
        self.online_users = online_users
        self.location_users = location_users
        pass

    def new_message(self, user_name, message):
        to_whom = message["to"]
        if to_whom == "all":
            location_users = self.location_users[self.online_users[user_name].location]
            for location_user in location_users.values():
                location_user.send_action(self.message_action(message))
        elif to_whom in self.online_users.keys():
            self.online_users[to_whom].send_action(self.message_action(message))