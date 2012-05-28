import random
from threading import Thread
import time
import smarty

__author__ = 'PavelP'

class BattleBot(Thread):
    def __init__(self, actions_manager, location):
        Thread.__init__(self)
        self.actions_manager = actions_manager
        self.skirmish_users = dict()
        self.location = location
        # phases:
        # -1 - none
        # 0 - registration
        # 1,2,... - rounds
        self.phase = -1
        self.counter = 0
        # type - result
        # types :
        # 0 - special spell result - who_name, whom_name, is_hit, is_critical, spell, amount, exp
        # 1 - damage spell result - who_name, whom_name, is_hit, is_critical, spell, amount, exp
        # 2 - ability result - who_name, whom_name, is_hit, amount, exp
        # 3 - attack result - who_name, whom_name, is_hit, is_critical, damage, exp
        # 4 - heal spell result - damage spell result
        self.round_results = dict()
        self.users_to_remove = list()
        self.turn_done_count = 0

    @property
    def online_users(self):
        return self.actions_manager.online_users

    def run(self):
        while 1:
            if self.phase == -1 and self.counter == smarty.rest_time:
                # registration start
                self.phase = 0
                self.counter = 0
                self.actions_manager.registration_started(self.location)
            elif self.phase == 0 and self.counter == smarty.registration_time:
                # registration end
                self.counter = 0
                if len(self.skirmish_users) > 1:
                    self.phase = 1
                    self.actions_manager.registration_ended(self.location)
                else:
                    self.actions_manager.game_cant_start(self.location)
            elif self.phase > 0 and self.counter == 1:
                self.actions_manager.round_started(self.phase, self.location, self.skirmish_users)
            elif self.phase > 0 and (self.counter == smarty.turn_time or self.turn_done_count == len(self.skirmish_users)):
                self.actions_manager.round_ended(self.phase, self.location, self.skirmish_users)
                self.counter = 0
                self.phase += 1
                self.turn_done_count = 0
                self.process_round_result()

            self.counter += 1

            time.sleep(1)
            pass

    # special spell result - who_name, whom_name, is_hit, is_critical, spell, amount, exp
    # damage spell result - who_name, whom_name, is_hit, is_critical, spell, amount, exp
    # ability result - who_name, whom_name, is_hit, amount, exp
    # attack result - who_name, whom_name, is_hit, is_critical, damage, exp
    # heal spell result - damage spell result
    def process_round_result(self):
        skirmish_users_names = self.skirmish_users.keys()
        random.shuffle(skirmish_users_names)
        for user_name in skirmish_users_names:
            skirmish_user = self.skirmish_users[user_name]
            if skirmish_user.is_turn_done(): # process user's turn
                for turn_part in skirmish_user.turn_info:
                    if not int(turn_part[3]) == 0: # don't process 0% actions, update - they shouldn't be sent already
                        if int(turn_part[0]) == 0: # attack
                            pass
                        elif int(turn_part[0]) == 1: # defence
                            pass
                        elif int(turn_part[0]) == 2: # spell
                            pass
                        elif int(turn_part[0]) == 3: # mana/energy regeneration
                            pass
                # TODO:
                self.skirmish_users[user_name].reset_turn()
            else: # remove users from skirmish
                self.users_to_remove.append(user_name)


        for user_name in self.users_to_remove:
            self.remove_from_skirmish(user_name)
        # TODO: count teams, not users
        # if there is just users of one team - end game
        # count teams of users
        if len(self.skirmish_users) < 2:
            self.process_game_result()

    def process_game_result(self):
        # TODO:
        self.actions_manager.game_ended(self.location)
        for user_name in self.skirmish_users.keys():
            self.remove_from_skirmish(user_name)
        self.phase = -1
        self.counter = 0
        pass

    def remove_from_skirmish(self, user_name):
        self.actions_manager.skirmish_user_removed(self.location, user_name)
        self.skirmish_users.pop(user_name)

    def user_join(self, user_name):
        if self.phase == 0 and user_name not in self.skirmish_users.keys():
            self.skirmish_users[user_name] = self.online_users[user_name]
            self.actions_manager.skirmish_user_added(user_name)

    def user_leave(self, user_name):
        if self.phase == 0:
            self.actions_manager.skirmish_user_left(user_name)
            self.skirmish_users.pop(user_name)

    def user_turn(self, user_name, turn_info):
        if self.phase > 0:
            self.turn_done_count += 1
            self.skirmish_users[user_name].set_turn_string(turn_info)
            self.actions_manager.user_did_turn(user_name, self.skirmish_users)

    def user_turn_cancel(self, user_name):
        if self.phase > 0:
            self.turn_done_count -= 1
            self.skirmish_users[user_name].reset_turn()
            self.actions_manager.user_cancel_turn(user_name, self.skirmish_users)

    def user_enter(self, user_name):
        self.actions_manager.user_enter_battle_bot(user_name, self.phase, self.counter, self.skirmish_users)