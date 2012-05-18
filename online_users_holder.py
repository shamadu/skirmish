from collections import deque, OrderedDict
import smarty

__author__ = 'PavelP'

class Action:
    def __init__(self, type, args):
        self.type = type
        self.args = args
        self.args["type"] = type

class OnlineUserInfo():
    def __init__(self, db_manager, name, locale):
        self.counter = 10
        self.db_manager = db_manager
        self.character = db_manager.get_character(name)
        self.turn_info = list()
        self.turn_info_string = ""
        self.user_callback = None
        self.user_cache = deque()
        self.skirmish_callback = None
        self.skirmish_cache = deque()
        self.character_callback = None
        self.character_cache = deque()
        self.locale = locale

    def set_user_callback(self, user_callback):
        self.counter = 10
        if len(self.user_cache) != 0 and user_callback:
            user_callback(self.user_cache.popleft())
        else:
            self.user_callback = user_callback

    def send_user_action(self, action):
        if self.user_callback:
            # to avoid replacement of callback in process of callback call
            callback_tmp = self.user_callback
            self.user_callback = None
            callback_tmp(action)
        else:
            self.user_cache.append(action)

    def set_skirmish_callback(self, skirmish_callback):
        self.counter = 10
        if len(self.skirmish_cache) != 0 and skirmish_callback:
            skirmish_callback(self.skirmish_cache.popleft())
        else:
            self.skirmish_callback = skirmish_callback

    def send_skirmish_action(self, action):
        if self.skirmish_callback:
            # to avoid replacement of callback in process of callback call
            callback_tmp = self.skirmish_callback
            self.skirmish_callback = None
            callback_tmp(action)
        else:
            self.skirmish_cache.append(action)

    def set_character_callback(self, character_callback):
        self.counter = 10
        if len(self.character_cache) != 0 and character_callback:
            character_callback(self.character_cache.popleft())
        else:
            self.character_callback = character_callback

    def send_character_action(self, action):
        if self.character_callback:
            # to avoid replacement of callback in process of callback call
            callback_tmp = self.character_callback
            self.character_callback = None
            callback_tmp(action)
        else:
            self.character_cache.append(action)

    def parse_turn_info(self, turn_info):
        self.turn_info_string = turn_info
        actions = self.turn_info_string.split(",")
        for action in actions:
            self.turn_info.append(action.split(":"))

    def get_turn_info(self):
        return self.turn_info_string

    def reset_turn(self):
        self.turn_info = list()

    def is_turn_done(self):
        if len(self.turn_info) > 0:
            return True
        else:
            return False

    def get_team_name(self): # return always current team name
        return self.db_manager.get_character(self.character.name).team_name

class OnlineUsersHolder():
    def __init__(self, db_manager):
        self.db_manager = db_manager
        self.online_users = dict()
        self.skirmish_users = dict()
        self.users_manager = None

    def add_if_not_online(self, user_name, locale):
        if not user_name in self.online_users.keys():
            self.users_manager.on_user_online(user_name)
            self.online_users[user_name] = OnlineUserInfo(self.db_manager, user_name, locale)
            self.users_manager.send_online_users_to(user_name)
        else:
            self.online_users[user_name].locale = locale

    def user_enter(self, user_name, locale):
        # remove callbacks
        self.online_users[user_name].user_callback = None
        self.online_users[user_name].skirmish_callback = None
        self.online_users[user_name].character_callback = None
        self.add_if_not_online(user_name, locale)
        self.users_manager.send_online_users_to(user_name)
        self.users_manager.send_skirmish_users_to(user_name)

    def add_skirmish_user(self, user_name):
        self.skirmish_users[user_name] = self.online_users[user_name]
        self.users_manager.user_join_skirmish(user_name)

    def remove_skirmish_user(self, user_name):
        self.users_manager.user_leave_skirmish(user_name)
        self.skirmish_users.pop(user_name)
