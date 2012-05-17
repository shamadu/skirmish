from threading import Thread
import time
from online_users_holder import Action
import smarty

__author__ = 'Pavel Padinker'

# types are:
# 0 - show skirmish users
# 1 - can join
# 2 - can leave
# 3 - can do turn
# 4 - can cancel turn
# 5 - wait for result
# 6 - reset to initial
# 7 - message action
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

class BattleBot(Thread):
    def __init__(self, db_manager, online_users_holder):
        Thread.__init__(self)
        self.skirmish_users = dict()
        self.action_manager = ActionManager(self.skirmish_users)
        self.online_users_holder = online_users_holder
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
            if self.online_users[user_name].is_turn_done(): # process user's turn
                # TODO:
                self.online_users[user_name].reset_turn()
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

    def subscribe(self, user_name, callback, locale):
        self.online_users_holder.add_if_not_online(user_name, locale)
        self.online_users[user_name].set_skirmish_callback(callback)

    def unsubscribe(self, user_name):
        if user_name in self.online_users:
            self.online_users[user_name].set_skirmish_callback(None)

    def user_join(self, user_name):
        if self.phase == 0:
            self.skirmish_users[user_name] = self.online_users[user_name] # registered
            self.send_action_to_all(self.action_manager.create_skirmish_users_action())
            self.send_action_to_user(user_name, self.action_manager.create_can_leave_action())

    def user_leave(self, user_name):
        if self.phase == 0:
            self.skirmish_users.pop(user_name) #unregistered
            self.send_action_to_all(self.action_manager.create_skirmish_users_action())
            self.send_action_to_user(user_name, self.action_manager.create_can_join_action())

    def user_turn(self, user_name, turn_info):
        if self.phase > 0:
            self.online_users[user_name].parse_turn_info(turn_info)
            args = self.online_users[user_name].create_div_args(self.skirmish_users.keys())
            args["turn_info"] = self.online_users[user_name].get_turn_info()
            self.send_action_to_user(user_name, self.action_manager.create_can_cancel_turn_action(args))

    def user_turn_cancel(self, user_name):
        if self.phase > 0:
            self.online_users[user_name].reset_turn()
            args = self.online_users[user_name].create_div_args(self.skirmish_users.keys())
            args["turn_info"] = self.online_users[user_name].get_turn_info()
            self.send_action_to_user(user_name, self.action_manager.create_can_do_turn_action(args))

    def send_action_to_all(self, action):
        for user_name in self.online_users.keys():
            self.online_users[user_name].send_skirmish_action(action)

    def send_action_to_skirmish(self, action):
        for user_name in self.skirmish_users.keys():
            if action.type > 2 and action.type < 6:
                action.args.update(self.online_users[user_name].create_div_args(self.skirmish_users.keys()))
                action.args["turn_info"] = ""
            self.online_users[user_name].send_skirmish_action(action)

    def send_action_to_user(self, user_name, action):
        if user_name in self.online_users.keys():
            self.online_users[user_name].send_skirmish_action(action)

    def user_enter(self, user_name, locale):
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
                    self.send_action_to_user(user_name, self.action_manager.create_can_do_turn_action(self.online_users[user_name].create_div_args(self.skirmish_users.keys())))
                # and if user is in skirmish and the turn is done, send "can cancel turn" action
                elif user_name in self.skirmish_users and self.skirmish_users[user_name].is_turn_done():
                    args = self.online_users[user_name].create_div_args(self.skirmish_users.keys())
                    args["turn_info"] = self.online_users[user_name].get_turn_info()
                    self.send_action_to_user(user_name, self.action_manager.create_can_cancel_turn_action(args))
            # all turns were done and if user is in skirmish and the turn is done, send "can cancel turn" action
            elif user_name in self.skirmish_users and self.skirmish_users[user_name].is_turn_done():
                args = self.online_users[user_name].create_div_args(self.skirmish_users.keys())
                args["turn_info"] = self.online_users[user_name].get_turn_info()
                self.send_action_to_user(user_name, self.action_manager.create_wait_for_result_action(args))
