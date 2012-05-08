from collections import deque, OrderedDict
from threading import Thread
import time
import smarty

__author__ = 'Pavel Padinker'

class Action:
    def __init__(self, for_all, type, args):
        self.for_all = for_all
        # types are:
        # 0 - show divAction
        # 1 - hide divAction
        # 2 - show skirmish users
        # 3 - start registration
        # 4 - end registration
        # 5 - start turn
        # 6 - end turn
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
            0,
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

        # user's states:
        # 0 - unregistered
        # 1 - registered
        # 2 - round turn is in progress
        # 3 - round turn is finished
        self.state = 0 # unregistered
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
                self.send_action(Action(True, 3, {}))
                self.phase = 0
                self.counter += 1
            elif self.phase == 0 and self.counter == self.registration_time:
                self.send_action(Action(True, 4, {}))
                self.phase = 1
                self.counter = 0
            elif self.phase > 0 and self.counter == 0:
                self.send_action(Action(True, 5, {}))
            elif self.phase > 0 and self.counter == self.turn_time:
                self.send_action(Action(True, 6, {}))
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
            action = Action(False, 1, {})
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

    def subscribe(self, user_name, callback):
        if user_name in self.cache.keys() and self.cache[user_name]:
            callback(self.cache[user_name].popleft())
        else:
            self.callbacks[user_name] = callback

    def unsubscribe(self, user_name):
        if user_name in self.callbacks.keys():
            self.callbacks[user_name] = None

    def send_skirmish_users(self):
        action = Action(True, 2, {"skirmish_users" : ', '.join(self.skirmish_users.keys())})
        self.send_action(action)

    def add_to_cache(self, user_name, action):
        if not user_name in self.cache or not self.cache[user_name]:
            self.cache[user_name] = deque()
        self.cache[user_name].append(action)

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
                self.add_to_cache(skirmish_user, action)

    def send_action_to(self, user_name, action):
        if self.callbacks[user_name]:
            callback_tmp = self.callbacks[user_name]
            self.callbacks[user_name] = None
            callback_tmp(action)
        else:
            self.add_to_cache(user_name, action)

    def reenter_from_user(self, user_name):
        # send skirmish users
        action = Action(True, 2, {"skirmish_users" : ', '.join(self.skirmish_users.keys())})
        self.send_action_to(user_name, action)
        # if user state is 1 or 2 - send "registration is in process" action

        if user_name in self.skirmish_users:
            self.send_action_to(user_name, self.skirmish_users[user_name].show_div_action)

