import random
from threading import Thread
import time
import smarty

__author__ = 'Pavel Padinker'

class BattleBot(Thread):
    def __init__(self, db_manager, actions_manager):
        Thread.__init__(self)
        self.actions_manager = actions_manager
        self.skirmish_users = dict()
        self.db_manager = db_manager
        # phases:
        # -1 - none
        # 0 - registration
        # 1,2,... - rounds
        self.phase = -1
        self.counter = 0

    @property
    def online_users(self):
        return self.actions_manager.online_users

    def run(self):
        while 1:
            if self.phase == -1 and self.counter == smarty.rest_time:
                # registration start
                self.phase = 0
                self.counter = 0
                self.actions_manager.registration_started()
            elif self.phase == 0 and self.counter == smarty.registration_time:
                # registration end
                self.counter = 0
                if len(self.skirmish_users) > 1:
                    self.phase = 1
                    self.actions_manager.registration_ended()
                else:
                    self.actions_manager.game_cant_start()
            elif self.phase > 0 and self.counter == 1:
                self.actions_manager.round_started(self.phase, self.skirmish_users)
            elif self.phase > 0 and self.counter == smarty.turn_time:
                self.actions_manager.round_ended(self.phase, self.skirmish_users)
                self.counter = 0
                self.phase += 1
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
        random.shuffle(self.skirmish_users)
        for user_name in self.skirmish_users.keys():
            if self.skirmish_users[user_name].is_turn_done(): # process user's turn

                # TODO:
                self.skirmish_users[user_name].reset_turn()
            else: # remove users from skirmish
                self.remove_from_skirmish(user_name)

        # if there is just users of one team - end game
        # count teams of users
        if len(self.skirmish_users) < 2:
            self.process_game_result()

    def process_game_result(self):
        # TODO:
        self.actions_manager.game_ended()
        for user_name in self.skirmish_users.keys():
            self.remove_from_skirmish(user_name)
        self.phase = -1
        self.counter = 0
        pass

    def remove_from_skirmish(self, user_name):
        self.actions_manager.skirmish_user_removed(user_name)
        self.skirmish_users.pop(user_name)

    def subscribe(self, user_name, callback):
        self.online_users[user_name].set_skirmish_callback(callback)

    def unsubscribe(self, user_name):
        if user_name in self.online_users:
            self.online_users[user_name].set_skirmish_callback(None)

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
            self.skirmish_users[user_name].parse_turn_info(turn_info)
            self.actions_manager.user_did_turn(user_name, self.skirmish_users)

    def user_turn_cancel(self, user_name):
        if self.phase > 0:
            self.skirmish_users[user_name].reset_turn()
            self.actions_manager.user_cancel_turn(user_name, self.skirmish_users)

    def user_enter(self, user_name):
        self.actions_manager.user_enter_battle_bot(user_name, self.phase, self.counter, self.skirmish_users)