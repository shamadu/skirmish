from collections import deque
import smarty

__author__ = 'PavelP'

class Action:
    def __init__(self, type, args):
        self.type = type
        self.args = args
        self.args["type"] = type

class TurnAction:
    def __init__(self, who, whom, type, spell_id, percent):
        self.who = who
        self.whom = whom
        # 0 - attack
        # 1 - defence
        # 2 - spell/ability
        # 3 - mana/energy regeneration
        self.type = type
        if type == 2:
            self.spell_id = int(spell_id)
        self.percent = float(percent)/100

class OnlineUserInfo():
    def __init__(self, user_name, location, locale):
        self.user_name = user_name
        self.counter = smarty.user_offline_time
        self.callback = None
        self.cache = deque()
        self.character = None # will be filled by db_manager
        self.battle_character = None # will be filled by battle_bot
        # 0 - default, alive
        # 1 - in skirmish, alive
        # 2 - ran from skirmish, alive
        # 3 - dead
        self.state = 0
        self.locale = locale
        self.location = location
        self.opened_chats = list() # users' names
        self.turn_info_string = ""
        self.previous_turn_string = ""

    def set_callback(self, callback):
        self.counter = smarty.user_offline_time
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
            self.cache.append(action)

    def set_turn_string(self, turn_info_string):
        self.turn_info_string = turn_info_string
        self.previous_turn_string = turn_info_string

    def get_previous_turn_string(self):
        return self.previous_turn_string

    def reset_turn(self):
        self.turn_info_string = ""

    def is_turn_done(self):
        if len(self.turn_info_string) > 0:
            return True
        else:
            return False

    def get_turn_info(self):
        result = list()
        actions = self.turn_info_string.split(",")
        for action in actions:
            if action:
                action_tokens = action.split(":")
                result.append(TurnAction(self.user_name, action_tokens[1], int(action_tokens[0]), action_tokens[2], int(action_tokens[3])))

        return result

class UsersHolder:
    def __init__(self):
        self.online_users = dict()
        self.location_users = dict()
        for location in smarty.locations:
            self.location_users[location[0]] = dict()