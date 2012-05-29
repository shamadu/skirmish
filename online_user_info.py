from collections import deque

__author__ = 'PavelP'

class TurnAction:
    def __init__(self, who, whom, type, spell_id, percent):
        self.who = who
        self.whom = whom
        # 0 - attack
        # 1 - defence
        # 2 - spell/ability
        # 3 - mana/energy regeneration
        self.type = type
        self.spell_id = spell_id
        self.percent = percent

class OnlineUserInfo():
    def __init__(self, name, locale):
        self.counter = 10
        self.character = {} # will be filled by db_manager
        self.turn_info_string = ""
        self.user_callback = None
        self.user_cache = deque()
        self.skirmish_callback = None
        self.skirmish_cache = deque()
        self.character_callback = None
        self.character_cache = deque()
        self.locale = locale
        self.location = "En"
        self.user_name = name

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

    def set_turn_string(self, turn_info_string):
        self.turn_info_string = turn_info_string

    def get_turn_string(self):
        return self.turn_info_string

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
