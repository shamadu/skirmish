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

class ActionManager:
    def __init__(self, skirmish_users):
        self.skirmish_users = skirmish_users

    def create_skirmish_users_action(self):
        skirmish_users = list()
        for user_name in self.skirmish_users:
            skirmish_users.append("%(user_name)s[%(team_name)s]" % {"user_name" : user_name, "team_name" : self.skirmish_users[user_name].get_team_name()})
        return Action(0, {"skirmish_users" : ','.join(skirmish_users)})

    def create_can_join_action(self):
        return Action(1, {})

    def create_can_leave_action(self):
        return Action(2, {})

    def create_can_do_turn_action(self, args=None):
        if not args:
            args = {}
        return Action(3, args)

    def create_can_cancel_turn_action(self, args=None):
        if not args:
            args = {}
        return Action(4, args)

    def create_wait_for_result_action(self, args=None):
        if not args:
            args = {}
        return Action(5, args)

    def create_reset_to_initial_action(self):
        return Action(6, {})

    def create_text_action(self, message_number, args=None):
        if not args:
            args = {}
        args["message_number"] = message_number

        return Action(7, args)

class UserInfo:
    def __init__(self, character, locale):
        self.character = character
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

    def get_team_name(self):
        return self.character.team_name

class BattleBot(Thread):
    def __init__(self, characters_manager):
        Thread.__init__(self)
        self.characters_manager = characters_manager
        self.users = dict()
        self.skirmish_users = dict()
        self.action_manager = ActionManager(self.skirmish_users)

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
                self.send_action_to_all(self.action_manager.create_text_action(0)) # registration has been started
                self.send_action_to_all(self.action_manager.create_can_join_action())
            elif self.phase == 0 and self.counter == smarty.registration_time:
                # registration end
                self.counter = 0
                if len(self.skirmish_users) > 1:
                    self.phase = 1
                    self.send_action_to_all(self.action_manager.create_text_action(1)) # registration has been ended
                else:
                    self.send_action_to_all(self.action_manager.create_text_action(5)) # game can't be started, not enough players
            elif self.phase > 0 and self.counter == 1:
                self.send_action_to_all(self.action_manager.create_text_action(2, {"round" : self.phase})) # round has been started
                self.send_action_to_skirmish(self.action_manager.create_can_do_turn_action())
            elif self.phase > 0 and self.counter == smarty.turn_time:
                self.send_action_to_all(self.action_manager.create_text_action(3, {"round" : self.phase})) # round has been ended
                self.send_action_to_skirmish(self.action_manager.create_wait_for_result_action())
                self.counter = 0
                self.phase += 1
                self.process_round_result()

            self.counter += 1

            time.sleep(1)
            pass

    def process_round_result(self):
        for user_name in self.skirmish_users.keys():
            if self.users[user_name].is_turn_done(): # process user's turn
                # TODO:
                self.users[user_name].reset_turn()
            else: # remove users from skirmish
                self.remove_from_skirmish(user_name)

        # if there is just users of one team - end game
        # count teams of users
        if len(self.skirmish_users) < 2:
            self.process_game_result()

    def process_game_result(self):
        # TODO:
        self.send_action_to_all(self.action_manager.create_text_action(4)) # game has been ended
        for user_name in self.skirmish_users.keys():
            self.remove_from_skirmish(user_name)
        self.phase = -1
        self.counter = 0
        pass

    def remove_from_skirmish(self, user_name):
        self.skirmish_users.pop(user_name) #unregistered
        self.send_action_to_user(user_name, self.action_manager.create_reset_to_initial_action())
        self.send_action_to_all(self.action_manager.create_skirmish_users_action())

    def user_join(self, user_name):
        if self.phase == 0:
            self.skirmish_users[user_name] = self.users[user_name] # registered
            self.send_action_to_all(self.action_manager.create_skirmish_users_action())
            self.send_action_to_user(user_name, self.action_manager.create_can_leave_action())

    def user_leave(self, user_name):
        if self.phase == 0:
            self.skirmish_users.pop(user_name) #unregistered
            self.send_action_to_all(self.action_manager.create_skirmish_users_action())
            self.send_action_to_user(user_name, self.action_manager.create_can_join_action())

    # it's called from user_manager
    def user_offline(self, user_name):
        if self.phase == 0 or self.phase == -1:
            self.users.pop(user_name)
        else:
            # TODO: remove user from users after battle_bot round
            pass

    def user_turn(self, user_name, turn_info):
        if self.phase > 0:
            self.users[user_name].parse_turn_info(turn_info)
            args = self.users[user_name].create_div_args(self.skirmish_users.keys())
            args["turn_info"] = self.users[user_name].get_turn_info()
            self.send_action_to_user(user_name, self.action_manager.create_can_cancel_turn_action(args))

    def user_turn_cancel(self, user_name):
        if self.phase > 0:
            self.users[user_name].reset_turn()
            args = self.users[user_name].create_div_args(self.skirmish_users.keys())
            args["turn_info"] = self.users[user_name].get_turn_info()
            self.send_action_to_user(user_name, self.action_manager.create_can_do_turn_action(args))

    def subscribe(self, user_name, callback, locale):
        if not user_name in self.users.keys():
            self.users[user_name] = UserInfo(self.characters_manager.get_character(user_name), locale)
        self.users[user_name].set_callback(callback)

    def unsubscribe(self, user_name):
        if user_name in self.users.keys():
            self.users[user_name].set_callback(None)

    def send_action_to_all(self, action):
        for user_name in self.users.keys():
            self.users[user_name].send_action(action)

    def send_action_to_skirmish(self, action):
        for user_name in self.skirmish_users.keys():
            if action.type > 2 and action.type < 6:
                action.args.update(self.users[user_name].create_div_args(self.skirmish_users.keys()))
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
        self.send_action_to_user(user_name, self.action_manager.create_skirmish_users_action())
        # if registration is in progress
        if self.phase == 0:
            # and if user is not in skirmish, send "can join" action
            if not user_name in self.skirmish_users.keys():
                self.send_action_to_user(user_name, self.action_manager.create_can_join_action())
            # and if user is in skirmish, send "can leave" action
            elif user_name in self.skirmish_users.keys():
                self.send_action_to_user(user_name, self.action_manager.create_can_leave_action())
        # if round is in progress
        elif self.phase > 0:
            # if it's time to do the turn
            if self.counter < smarty.turn_time:
                # and if user is in skirmish and the turn isn't done, send "can do turn" action
                if user_name in self.skirmish_users and not self.skirmish_users[user_name].is_turn_done():
                    self.send_action_to_user(user_name, self.action_manager.create_can_do_turn_action(self.users[user_name].create_div_args(self.skirmish_users.keys())))
                # and if user is in skirmish and the turn is done, send "can cancel turn" action
                elif user_name in self.skirmish_users and self.skirmish_users[user_name].is_turn_done():
                    args = self.users[user_name].create_div_args(self.skirmish_users.keys())
                    args["turn_info"] = self.users[user_name].get_turn_info()
                    self.send_action_to_user(user_name, self.action_manager.create_can_cancel_turn_action(args))
            # all turns were done and if user is in skirmish and the turn is done, send "can cancel turn" action
            elif user_name in self.skirmish_users and self.skirmish_users[user_name].is_turn_done():
                args = self.users[user_name].create_div_args(self.skirmish_users.keys())
                args["turn_info"] = self.users[user_name].get_turn_info()
                self.send_action_to_user(user_name, self.action_manager.create_wait_for_result_action(args))
