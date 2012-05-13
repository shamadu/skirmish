from collections import deque, OrderedDict
from threading import Thread
import time
import smarty

__author__ = 'Pavel Padinker'

class Action:
    def __init__(self, type, args):
        # types are:
        # 0 - show skirmish users
        # 1 - can join
        # 2 - can leave
        # 3 - can do turn
        # 4 - can cancel turn
        # 5 - wait for result
        # 6 - reset to initial
        # 7 - message action
        self.type = type
        self.args = args
        self.args["type"] = type

class UserInfo:
    def __init__(self, character, locale):
        self.character = character

        # user's states:
        # 0 - unregistered
        # 1 - registered
        # 2 - round turn is finished
        self.state = 0 # unregistered
        self.turn_info = list()
        self.cache = deque()
        self.turn_info_string = ""
        self.callback = None
        self.locale = locale

    def set_callback(self, callback):
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
            self.add_to_cache(action)

    def add_to_cache(self, action):
        self.cache.append(action)

    def create_div_args(self, users):
        actions = OrderedDict()
        actions[0] = self.locale.translate(smarty.main_abilities[0]), smarty.get_attack_count(self.character.classID, self.character.level)
        actions[1] = self.locale.translate(smarty.main_abilities[1]), smarty.get_defence_count(self.character.classID, self.character.level)
        actions[2] = smarty.get_ability_name(self.character.classID, self.locale) , smarty.get_spell_count(self.character.classID, self.character.level)
        actions[3] = smarty.get_substance_name(self.character.classID, self.locale) , 0
        return {
                "actions" : actions,
                "users" : users,
                "spells" : smarty.get_spells(self.character.classID, self.character.level)
                }

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

class BattleBot(Thread):
    def __init__(self, characters_manager):
        Thread.__init__(self)
        self.characters_manager = characters_manager
        self.users = dict()

        # phases:
        # -1 - none
        # 0 - registration
        # 1,2,... - rounds
        self.phase = -1
        self.counter = 0

    def run(self):
        while 1:
            if self.phase == -1 and self.counter == smarty.rest_time:
                # registration start
                self.phase = 0
                self.counter = 0
                self.send_action_to_all(Action(7, {"message_number" : "0"}))
                self.send_action_to_all(Action(1, {}))
            elif self.phase == 0 and self.counter == smarty.registration_time:
                # registration end
                self.counter = 0
                if len(self.get_skirmish_users()) > 1:
                    self.phase = 1
                    self.send_action_to_all(Action(7, {"message_number" : "1"}))
                else:
                    self.send_action_to_all(Action(7, {"message_number" : "5"}))
            elif self.phase > 0 and self.counter == 1:
                self.send_action_to_all(Action(7, {"message_number" : "2", "round" : self.phase}))
                self.send_action_to_skirmish(Action(3, {}))
            elif self.phase > 0 and self.counter == smarty.turn_time:
                self.send_action_to_all(Action(7, {"message_number" : "3", "round" : self.phase}))
                self.send_action_to_skirmish(Action(5, {}))
                self.counter = 0
                self.phase += 1
                self.process_round_result()

            self.counter += 1

            time.sleep(1)
            pass

    def process_round_result(self):
        for user_name in self.get_skirmish_users():
            if self.users[user_name].is_turn_done():
                # TODO:
                self.users[user_name].reset_turn()
                pass
            else:
                self.send_action_to_user(user_name, Action(6, {}))
                self.users[user_name].state = 0 #unregistered
                self.send_action_to_all(self.create_skirmish_users_action())

        if len(self.get_skirmish_users()) < 2:
            self.process_game_result()

    def process_game_result(self):
        # TODO:
        self.send_action_to_all(Action(7, {"message_number" : "4"}))
        for user_name in self.get_skirmish_users():
            self.send_action_to_user(user_name, Action(6, {}))
            self.users[user_name].state = 0 #unregistered
            self.send_action_to_all(self.create_skirmish_users_action())
        self.phase = -1
        self.counter = 0
        pass

    def user_join(self, user_name):
        if self.phase == 0:
            self.users[user_name].state = 1 # registered
            self.send_action_to_all(self.create_skirmish_users_action())
            self.send_action_to_user(user_name, Action(2, {}))

    def user_leave(self, user_name):
        if self.phase == 0:
            self.users[user_name].state = 0 # unregistered
            self.send_action_to_all(self.create_skirmish_users_action())
            self.send_action_to_user(user_name, Action(1, {}))

    def user_turn(self, user_name, turn_info):
        if self.phase > 0:
            self.users[user_name].parse_turn_info(turn_info)
            self.state = 2
            args = self.users[user_name].create_div_args(self.get_skirmish_users())
            args["turn_info"] = self.users[user_name].get_turn_info()
            self.send_action_to_user(user_name, Action(4, args))

    def user_turn_cancel(self, user_name):
        if self.phase > 0:
            self.users[user_name].reset_turn()
            self.state = 1
            args = self.users[user_name].create_div_args(self.get_skirmish_users())
            args["turn_info"] = self.users[user_name].get_turn_info()
            self.send_action_to_user(user_name, Action(3, args))

    def subscribe(self, user_name, callback, locale):
        if not user_name in self.users.keys():
            self.users[user_name] = UserInfo(self.characters_manager.get_character(user_name), locale)
        self.users[user_name].set_callback(callback)

    def unsubscribe(self, user_name):
        self.users[user_name].set_callback(None)

    def get_skirmish_users(self):
        skirmish_users = list()
        for user_name in self.users:
            # 0 is unregistered user
            if self.users[user_name].state != 0:
                skirmish_users.append(user_name)

        return skirmish_users

    def create_skirmish_users_action(self):
        return Action(0, {"skirmish_users" : ', '.join(self.get_skirmish_users())})

    def send_action_to_all(self, action):
        for user_name in self.users.keys():
            if action.type > 2 and action.type < 6:
                action.args.update(self.users[user_name].create_div_args(self.get_skirmish_users()))
                action.args["turn_info"] = ""
            self.users[user_name].send_action(action)

    def send_action_to_skirmish(self, action):
        for user_name in self.get_skirmish_users():
            if action.type > 2 and action.type < 6:
                action.args.update(self.users[user_name].create_div_args(self.get_skirmish_users()))
                action.args["turn_info"] = ""
            self.users[user_name].send_action(action)

    def send_action_to_user(self, user_name, action):
        if(user_name in self.users.keys()):
            self.users[user_name].send_action(action)

    def user_enter(self, user_name, locale):
        if not user_name in self.users.keys():
            self.users[user_name] = UserInfo(self.characters_manager.get_character(user_name), locale)
        else:
            self.users[user_name].locale = locale
        # send skirmish users
        self.send_action_to_user(user_name, self.create_skirmish_users_action())
        # if registration is in progress
        if self.phase == 0:
            # and if user state is "unregistered", send "can join" action
            if self.users[user_name].state == 0:
                self.send_action_to_user(user_name, Action(1, {}))
            # and if user state is "registered", send "can leave" action
            elif self.users[user_name].state == 1:
                self.send_action_to_user(user_name, Action(2, {}))
        # if round is in progress
        elif self.phase > 0:
            # if it's time to do the turn
            if self.counter < smarty.turn_time:
                # and if user state is "registered", send "can do turn" action
                if self.users[user_name].state == 1:
                    self.send_action_to_user(user_name, Action(3, self.users[user_name].create_div_args(self.get_skirmish_users())))
                # and if user state is "round turn is done", send "can cancel turn" action
                elif self.users[user_name].state == 2:
                    args = self.users[user_name].create_div_args(self.get_skirmish_users())
                    args["turn_info"] = self.users[user_name].get_turn_info()
                    self.send_action_to_user(user_name, Action(4, args))
            # all turns were done and if user state is "round turn is done", send "wait for result" action
            elif self.users[user_name].state == 2:
                args = self.users[user_name].create_div_args(self.get_skirmish_users())
                args["turn_info"] = self.users[user_name].get_turn_info()
                self.send_action_to_user(user_name, Action(5, args))
