import random
from threading import Thread
import time
import smarty
import spells_manager

__author__ = 'PavelP'

class ResultAction:
    def __init__(self, action):
        self.who = action.who
        self.whom = action.whom
        self.type = action.type
        self.spell_id = action.spell_id
        self.amount = 0
        self.experience = 0
        self.is_hit = False
        self.is_critical = False
        self.is_low_mana = False
        self.percent = float(action.percent)/100

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
        result_actions = list()
        # collect actions from every user
        skirmish_users_names = self.skirmish_users.keys()
        random.shuffle(skirmish_users_names)
        actions = { # action type : result action
            0 : list(), # attack
            1 : list(), # defence
            2 : list(), # spell/ability
            3 : list() # regeneration
        }
        for user_name in skirmish_users_names:
            skirmish_user = self.skirmish_users[user_name]
            if skirmish_user.is_turn_done(): # process user's turn
                for action in skirmish_user.get_turn_info():
                    actions[action.type].append(ResultAction(action))
                self.skirmish_users[user_name].reset_turn()
            else: # remove users from skirmish
                self.users_to_remove.append(user_name)

        def get_spells_by_ordinal(actions, ordinal):
            spell_actions = list()
            for action in actions:
                if spells_manager.spells[action.spell_id].ordinal == 0:
                    spell_actions.append(action)
            return spell_actions

        # get spells which should be done as 0 ordinal
        spell_actions = get_spells_by_ordinal(actions[2], 0)

        # TODO: increase parameters or do something else with characters
        def add_result_action_special_spell(action):
            if self.skirmish_users[action.who].character.mana >= spells_manager.spells[action.spell_id].mana:
                self.skirmish_users[action.who].character.mana -= spells_manager.spells[action.spell_id].mana
                if smarty.is_magical_hit(self.skirmish_users[action.who].character, action.percent, self.skirmish_users[action.whom].character):
                    action.is_hit = True
            else:
                action.is_low_mana = True
            result_actions.append(action)

        # TODO: increase parameters or do something else with characters
        def add_result_action_ability(action):
            if self.skirmish_users[action.who].character.mana >= spells_manager.spells[action.spell_id].mana:
                self.skirmish_users[action.who].character.mana -= spells_manager.spells[action.spell_id].mana
                if smarty.is_ability_passed(self.skirmish_users[action.who].character, action.percent, self.skirmish_users[action.whom].character):
                    action.is_hit = True
            else:
                action.is_low_mana = True
            result_actions.append(action)

        # TODO: optimize algorithm and add long spells effect (store them on character)
        def add_result_action_damage_heal(action):
            result_action = ResultAction(action)
            spell = spells_manager.spells[action.spell_id]
            if self.skirmish_users[action.who].character.mana >= spell.mana:
                self.skirmish_users[action.who].character.mana -= spell.mana
                if smarty.is_magical_hit(self.skirmish_users[action.who].character, action.percent, self.skirmish_users[action.whom].character):
                    result_action.is_hit = True
                    who_character = self.skirmish_users[action.who].character
                    whom_character = self.skirmish_users[action.whom].character
                    result_action.amount = smarty.get_magical_damage(spell, who_character, who_character.percent, whom_character)
                    if smarty.is_critical_magic_hit(who_character, whom_character):
                        result_action.is_critical = True
                        result_action.amount *= 1.5
                    if spell.ordinal == 3: # damage
                        whom_character.health -= result_action.amount
                    elif spell.ordinal == 4: # heal:
                        whom_character.health += result_action.amount
            else:
                result_action.is_low_mana = True
            result_actions.append(action)

        for action in spell_actions:
            add_result_action_special_spell(action)

        # get spells which should be done as 1 ordinal
        spell_actions = get_spells_by_ordinal(actions[2], 1)

        for action in spell_actions:
            add_result_action_special_spell(action)

        # get spells which should be done as 2 ordinal (abilities)
        spell_actions = get_spells_by_ordinal(actions[2], 2)

        for action in spell_actions:
            add_result_action_ability(action)

        # get spells which should be done as 3 ordinal (damage spells)
        spell_actions = get_spells_by_ordinal(actions[2], 3)

        for action in spell_actions:
            add_result_action_damage_heal(action)

        for action in actions[0]: # attack
            defenders = list() # character : action percent
            for def_action in actions[1]: # defence
                if def_action.whom == action.whom:
                    defenders.append((self.skirmish_users[def_action.who].character, def_action.percent))
            if smarty.is_hit(self.skirmish_users[action.who].character, action.percent, defenders):
                action.is_hit = True
                who_character = self.skirmish_users[action.who].character
                whom_character = self.skirmish_users[action.whom].character
                action.amount = smarty.get_damage(who_character, action.percent, whom_character)
                if smarty.is_critical_hit(who_character, whom_character):
                    action.is_critical = True
                    action.amount *= 1.5
                    whom_character.health -= action.amount
                experience = smarty.get_experience_for_damage(action.amount)
                self.skirmish_users[action.who].character.experience += experience
                action.experience = experience
            else: # not hit - set exp to defenders
                who_character = self.skirmish_users[action.who].character
                whom_character = self.skirmish_users[action.whom].character
                action.amount = smarty.get_damage(who_character, action.percent, whom_character)
                if smarty.is_critical_hit(who_character, whom_character):
                    action.amount *= 1.5
                all_defence = 0
                for defender in defenders:
                    all_defence += defender[0].defence
                experience = smarty.get_experience_for_defence(action.amount)
                for def_action in actions[1]: # defence
                    if def_action.whom == action.whom:
                        def_action.is_hit = True
                        def_action.experience = experience*(self.skirmish_users[def_action.who].character.defence/all_defence)
                        self.skirmish_users[def_action.who].character.experience += def_action.experience

        # get spells which should be done as 4 ordinal (heal spells)
        spell_actions = get_spells_by_ordinal(actions[2], 4)

        for action in spell_actions:
            add_result_action_damage_heal(action)

        # go over result actions and prepare messages
        for action in result_actions:
            if action.is_hit:
                pass

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