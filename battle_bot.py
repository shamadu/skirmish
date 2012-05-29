import random
from threading import Thread
import time
import smarty
import spells_manager

__author__ = 'PavelP'

class BattleBot(Thread):
    def __init__(self, actions_manager, db_manager, location):
        Thread.__init__(self)
        self.actions_manager = actions_manager
        self.db_manager = db_manager
        self.skirmish_users = dict()
        self.dead_users = dict()
        self.ran_users = dict()
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
        self.ran_users = list()
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
        ordered_actions = list()
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
                    actions[action.type].append(action)
                self.skirmish_users[user_name].reset_turn()
            else: # remove users from skirmish
                self.ran_users.append(user_name)

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
            ordered_actions.append(action)

        # TODO: increase parameters or do something else with characters
        def add_result_action_ability(action):
            if self.skirmish_users[action.who].character.mana >= spells_manager.spells[action.spell_id].mana:
                self.skirmish_users[action.who].character.mana -= spells_manager.spells[action.spell_id].mana
                if smarty.is_ability_passed(self.skirmish_users[action.who].character, action.percent, self.skirmish_users[action.whom].character):
                    action.is_hit = True
            else:
                action.is_low_mana = True
            ordered_actions.append(action)

        # TODO: optimize algorithm and add long spells effect (store them on character)
        def add_result_action_damage_heal(action):
            spell = spells_manager.spells[action.spell_id]
            if self.skirmish_users[action.who].character.mana >= spell.mana:
                self.skirmish_users[action.who].character.mana -= spell.mana
                if smarty.is_magical_hit(self.skirmish_users[action.who].character, action.percent, self.skirmish_users[action.whom].character):
                    action.is_hit = True
                    who_character = self.skirmish_users[action.who].character
                    whom_character = self.skirmish_users[action.whom].character
                    action.amount = smarty.get_magical_damage(spell, who_character, who_character.percent, whom_character)
                    if smarty.is_critical_magic_hit(who_character, whom_character):
                        action.is_critical = True
                        action.amount *= 1.5
                    if spell.ordinal == 3: # damage
                        whom_character.health -= action.amount
                    elif spell.ordinal == 4: # heal:
                        whom_character.health += action.amount
            else:
                action.is_low_mana = True
            ordered_actions.append(action)

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
            who_character = self.skirmish_users[action.who].character
            whom_character = self.skirmish_users[action.whom].character
            if smarty.is_hit(who_character, action.percent, defenders):
                amount = smarty.get_damage(who_character, action.percent, whom_character)
                if smarty.is_critical_hit(who_character, whom_character):
                    self.actions_manager.critical_hit(self.location, action.who)
                    amount *= 1.5
                whom_character.health -= amount
                experience = smarty.get_experience_for_damage(amount)
                who_character.experience += experience
                self.db_manager.change_character_field(who_character.name, "experience", who_character.experience)
                self.actions_manager.succeeded_attack(self.location, action.who, action.whom, amount, whom_character.health, experience)
            else: # not hit - set exp to defenders
                amount = smarty.get_damage(who_character, action.percent, whom_character)
                if smarty.is_critical_hit(who_character, whom_character):
                    amount *= 1.5
                all_defence = 0
                for defender in defenders:
                    all_defence += defender[0].defence
                all_experience = smarty.get_experience_for_defence(amount)
                defence_experience = list()
                for def_action in actions[1]: # defence
                    if def_action.whom == action.whom:
                        def_experience = all_experience*(self.skirmish_users[def_action.who].character.defence/all_defence)
                        who_character.experience += def_experience
                        self.db_manager.change_character_field(who_character.name, "experience", who_character.experience)
                        defence_experience.append("{0}[{1}]".format(def_action.who, def_experience))
                self.actions_manager.failed_attack(self.location, action, ",".join(defence_experience))

        # get spells which should be done as 4 ordinal (heal spells)
        spell_actions = get_spells_by_ordinal(actions[2], 4)

        for action in spell_actions:
            add_result_action_damage_heal(action)

        for user in self.skirmish_users.values():
            if user.character.health <= 0:
                self.dead_users[user.user_name] = user
                self.remove_from_skirmish(user.user_name)
                self.actions_manager.user_is_dead(self.location, user.user_name)
                self.db_manager.update_character(user.user_name)
            self.actions_manager.send_character_info(user.user_name)

        for user_name in self.ran_users:
            self.ran_users[user_name] = self.skirmish_users[user_name]
            self.remove_from_skirmish(user_name)
            self.actions_manager.user_ran(self.location, user_name)

        # if there is just users of one team - end game
        # count teams of users
        teams = list()
        users_no_team = list()
        for user in self.skirmish_users.values():
            if user.character.team_name:
                if user.character.team_name not in teams:
                    teams.append(user.character.team_name)
            else:
                users_no_team.append(user.user_name)


        if (len(teams) < 2 and len(users_no_team) == 0) or (len(teams) == 0 and len(users_no_team) < 2): # process game result
            self.actions_manager.game_ended(self.location)
            if len(teams) == 1:
                self.actions_manager.game_win_team(self.location, "{0}({1})".format(teams[0], ",".join(self.skirmish_users.keys())))
            elif len(users_no_team) == 1:
                self.actions_manager.game_win_user(self.location, "{0}".format(users_no_team[0]))
            else:
                self.actions_manager.game_win_nobody(self.location)
            for user_name in self.skirmish_users.keys():
                self.remove_from_skirmish(user_name)
            self.phase = -1
            self.counter = 0

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