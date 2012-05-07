from collections import deque, OrderedDict
from threading import Thread
import time
import smarty

__author__ = 'Pavel Padinker'

class Action:
    def __init__(self, for_all, type, args):
        self.for_all = for_all
        # types are:
        # show_div_action
        # show_skirmish_users
        # start_registration
        self.type = type
        self.args = args

class TurnInfo:
    def __init__(self):
        self.done = False
        self.turn_info = list()
        pass;

    def is_done(self):
        return self.done

    def parse_turn_info(self, turn_info):
        actions = turn_info.split(",")
        for action in actions:
            self.turn_info.append(action.split(":"))
        self.done = True

    def cancel_turn(self):
        self.done = False
        self.turn_info = list()

class UserInfo:
    def __init__(self, character):
        self.character = character
        self.show_div_action = Action(
            False,
            "show_div_action",
            {
                "actions" : OrderedDict([
                    ("attack" , smarty.get_attack_count(self.character.classID, self.character.level)),
                    ("defence" , smarty.get_defence_count(self.character.classID, self.character.level)),
                    (smarty.get_ability_name(character.classID) , smarty.get_spell_count(self.character.classID, self.character.level)),
                    (smarty.get_substance_name(character.classID) , 0)
            ]),
                "users" : list(),
                "spells" : smarty.get_spells(self.character.classID, self.character.level)
            }
        )

        self.turn_info = TurnInfo()

class BattleBot(Thread):
    def __init__(self, characters_manager):
        Thread.__init__(self)
        self.characters_manager = characters_manager
        self.skirmish_users = dict()
        self.callbacks = dict()
        self.cache = dict()

        self.registration_time = 20
        self.turn_time = 20
        self.counter = 0
        # phases:
        # -1 - none
        # 0 - registration
        # 1,2,... - rounds
        self.phase = -1

    def run(self):
        while 1:
            if self.phase == -1 and self.counter == 0:
                self.send_action(Action(True, "start_registration", {}))
                self.phase = 0
                counter += 1
            elif self.phase == 0 and self.counter == self.registration_time:
                self.send_action(Action(True, "end_registration", {}))
                self.phase = 1
                self.counter = 0
            elif self.phase > 0 and self.counter == 0:
                self.send_action(Action(True, "start_turn", {}))
            elif self.phase > 0 and self.counter == self.turn_time:
                self.send_action(Action(True, "end_turn", {}))
                self.phase += 1
                self.counter = 0
                self.process_round_result()
            time.sleep(1)
            pass

    def process_round_result(self):
        pass

    def user_join(self, name):
        if not name in self.skirmish_users.keys():
            self.skirmish_users[name] = UserInfo(self.characters_manager.get(name))
            self.send_skirmish_users()

            action = self.skirmish_users[name].show_div_action
            action.args["users"] = self.skirmish_users.keys()
            self.send_action_to(name, action)


    def user_leave(self, name):
        if name in self.skirmish_users.keys():
            action = Action(
                False,
                "hide_div_action",
                {}
            )
            self.send_action_to(name, action)
            self.skirmish_users.pop(name)
            self.send_skirmish_users()

    def user_turn(self, name, turn_info):
        self.skirmish_users[name].turn_info.parse_turn_info(turn_info)

    def user_turn_cancel(self, name):
        self.skirmish_users[name].turn_info.cancel_turn()

    def get_user_status(self, name):
        if name in self.skirmish_users.keys():
            return 'battle'
        else:
            return 'rest'

    def subscribe(self, name, callback):
        if name in self.cache.keys() and self.cache[name]:
            callback(self.cache[name].popleft())
        else:
            self.callbacks[name] = callback

    def unsubscribe(self, name):
        if name in self.callbacks.keys():
            self.callbacks[name] = None

    def send_skirmish_users(self):
        action = Action(True, "show_skirmish_users", {"skirmish_users" : ', '.join(self.skirmish_users.keys())})
        self.send_action(action)

    def send_action(self, action):
        if action.for_all:
            users = self.callbacks.keys()
        else:
            users = self.skirmish_users.keys()

        for skirmish_user in users:
            if self.callbacks[skirmish_user]:
                callback_tmp = self.callbacks[skirmish_user]
                self.callbacks[skirmish_user] = None
                callback_tmp(action)
            else:
                if not skirmish_user in self.cache or not self.cache[skirmish_user]:
                    self.cache[skirmish_user] = deque()
                self.cache[skirmish_user].append(action)

    def send_action_to(self, name, action):
        if self.callbacks[name]:
            callback_tmp = self.callbacks[name]
            self.callbacks[name] = None
            callback_tmp(action)
        else:
            if not name in self.cache or not self.cache[name]:
                self.cache[name] = deque()
            self.cache[name].append(action)

    def reenter_from_user(self, name):
        action = Action(True, "show_skirmish_users", {"skirmish_users" : ', '.join(self.skirmish_users.keys())})
        if not name in self.cache or not self.cache[name]:
            self.cache[name] = deque()
        self.cache[name].append(action)
        if name in self.skirmish_users:
            self.cache[name].append(self.skirmish_users[name].show_div_action)

