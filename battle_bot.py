from collections import OrderedDict
from threading import Thread
import time
from online_users_holder import Action
import smarty

__author__ = 'Pavel Padinker'

# types are:
# 3 - can join
# 4 - can leave
# 5 - can do turn
# 6 - can cancel turn
# 7 - wait for result
# 8 - reset to initial
# 9 - message action
class ActionManager:
    def __init__(self, skirmish_users):
        self.skirmish_users = skirmish_users

    def create_can_join_action(self):
        return Action(3, {})

    def create_can_leave_action(self):
        return Action(4, {})

    def create_can_do_turn_action(self, user_name):
        return Action(5, self.create_div_args(user_name))

    def create_can_cancel_turn_action(self, user_name):
        return Action(6, self.create_div_args(user_name))

    def create_wait_for_result_action(self, user_name):
        return Action(7, self.create_div_args(user_name))

    def create_reset_to_initial_action(self):
        return Action(8, {})

    def create_text_action(self, message_number, args=None):
        if not args:
            args = {}
        args["message_number"] = message_number

        return Action(9, args)

    def create_div_args(self, user_name):
        user = self.skirmish_users[user_name]
        actions = OrderedDict()
        actions[0] = user.locale.translate(smarty.main_abilities[0]), smarty.get_attack_count(user.character.classID, user.character.level)
        actions[1] = user.locale.translate(smarty.main_abilities[1]), smarty.get_defence_count(user.character.classID, user.character.level)
        actions[2] = smarty.get_ability_name(user.character.classID, user.locale) , smarty.get_spell_count(user.character.classID, user.character.level)
        actions[3] = smarty.get_substance_name(user.character.classID, user.locale) , 0
        return {
            "actions" : actions,
            "users" : self.skirmish_users.keys(),
            "spells" : smarty.get_spells(user.character, user.locale),
            "turn_info" : user.get_turn_info()
        }

class BattleBot(Thread):
    def __init__(self, db_manager, online_users_holder):
        Thread.__init__(self)
        self.online_users_holder = online_users_holder
        self.action_manager = ActionManager(self.skirmish_users)
        self.db_manager = db_manager
        # phases:
        # -1 - none
        # 0 - registration
        # 1,2,... - rounds
        self.phase = -1
        self.counter = 0

    @property
    def online_users(self):
        return self.online_users_holder.online_users

    @property
    def skirmish_users(self):
        return self.online_users_holder.skirmish_users

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
                for user_name in self.skirmish_users.keys():
                    self.skirmish_users[user_name].send_skirmish_action(self.action_manager.create_can_do_turn_action(user_name))
            elif self.phase > 0 and self.counter == smarty.turn_time:
                self.send_action_to_all(self.action_manager.create_text_action(3, {"round" : self.phase})) # round has been ended
                for user_name in self.skirmish_users.keys():
                    self.skirmish_users[user_name].send_skirmish_action(self.action_manager.create_wait_for_result_action(user_name))
                self.counter = 0
                self.phase += 1
                self.process_round_result()

            self.counter += 1

            time.sleep(1)
            pass

    def process_round_result(self):
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
        self.send_action_to_all(self.action_manager.create_text_action(4)) # game has been ended
        for user_name in self.skirmish_users.keys():
            self.remove_from_skirmish(user_name)
        self.phase = -1
        self.counter = 0
        pass

    def remove_from_skirmish(self, user_name):
        self.send_action_to_user(user_name, self.action_manager.create_reset_to_initial_action())
        self.online_users_holder.remove_skirmish_user(user_name)

    def subscribe(self, user_name, callback):
        self.online_users[user_name].set_skirmish_callback(callback)

    def unsubscribe(self, user_name):
        if user_name in self.online_users:
            self.online_users[user_name].set_skirmish_callback(None)

    def user_join(self, user_name):
        if self.phase == 0 and user_name not in self.skirmish_users.keys():
            self.send_action_to_user(user_name, self.action_manager.create_can_leave_action())
            self.online_users_holder.add_skirmish_user(user_name)

    def user_leave(self, user_name):
        if self.phase == 0:
            self.send_action_to_user(user_name, self.action_manager.create_can_join_action())
            self.online_users_holder.remove_skirmish_user(user_name)

    def user_turn(self, user_name, turn_info):
        if self.phase > 0:
            self.online_users[user_name].parse_turn_info(turn_info)
            action = self.action_manager.create_can_cancel_turn_action(user_name)
            self.send_action_to_user(user_name, action)

    def user_turn_cancel(self, user_name):
        if self.phase > 0:
            self.online_users[user_name].reset_turn()
            self.send_action_to_user(user_name, self.action_manager.create_can_do_turn_action(user_name))

    def send_action_to_all(self, action):
        for user_name in self.online_users.keys():
            self.online_users[user_name].send_skirmish_action(action)

    def send_action_to_user(self, user_name, action):
        if user_name in self.online_users.keys():
            self.online_users[user_name].send_skirmish_action(action)

    def user_enter(self, user_name):
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
                    self.send_action_to_user(user_name, self.action_manager.create_can_do_turn_action(user_name))
                # and if user is in skirmish and the turn is done, send "can cancel turn" action
                elif user_name in self.skirmish_users and self.skirmish_users[user_name].is_turn_done():
                    self.send_action_to_user(user_name, self.action_manager.create_can_cancel_turn_action(user_name))
            # all turns were done and if user is in skirmish and the turn is done, send "can cancel turn" action
            elif user_name in self.skirmish_users and self.skirmish_users[user_name].is_turn_done():
                self.send_action_to_user(user_name, self.action_manager.create_wait_for_result_action(user_name))
