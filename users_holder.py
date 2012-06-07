from collections import OrderedDict, deque
import items_manager
from online_user_info import OnlineUserInfo
import smarty
import spells_manager

__author__ = 'PavelP'

class Action:
    def __init__(self, type, args):
        self.type = type
        self.args = args
        self.args["type"] = type


class UsersHolder:
    def __init__(self):
        self.online_users = dict()
        self.location_users = {
            "En" : dict(),
            "Ru" : dict()
            }
        self.users_manager = None
        self.characters_manager = None
        self.battle_manager = None

    def user_enter(self, user_name):
        self.online_users[user_name].user_cache = deque()
        self.online_users[user_name].skirmish_cache = deque()
        self.online_users[user_name].character_cache = deque()
        self.users_manager.user_enter(user_name)
        self.characters_manager.user_enter(user_name)
        self.battle_manager.user_enter(user_name)
