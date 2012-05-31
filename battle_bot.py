import copy
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
        self.location = location
        self.location_users = actions_manager.location_users[location]
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
        self.spell_actions = {
            4 : list()
        }
        self.turn_done_count = 0
        self.dead_users = dict()
        self.ran_users = list()
        self.characters = dict()
        self.victims = dict()

    def reset(self):
        del self.ran_users[:]
        self.dead_users.clear()
        self.characters.clear()
        self.skirmish_users.clear()
        self.spell_actions.clear()
        self.victims.clear()
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
                self.registration_started()
            elif self.phase == 0 and self.counter == smarty.registration_time:
                # registration end
                self.counter = 0
                if len(self.skirmish_users) > 1:
                    self.phase = 1
                    self.registration_ended()
                    self.game_started()
                else:
                    self.game_cant_start()
            elif self.phase > 0 and self.counter == 1:
                self.round_started()
            elif self.phase > 0 and (self.counter == smarty.turn_time or self.turn_done_count == len(self.skirmish_users)):
                self.counter = 0
                self.phase += 1
                self.turn_done_count = 0
                self.process_round_result()
                self.round_ended()
                self.process_game_result()

            self.counter += 1

            time.sleep(1)
            pass

    # special spell result - who_name, whom_name, is_hit, is_critical, spell, amount, exp
    # damage spell result - who_name, whom_name, is_hit, is_critical, spell, amount, exp
    # ability result - who_name, whom_name, is_hit, amount, exp
    # attack result - who_name, whom_name, is_hit, is_critical, damage, exp
    # heal spell result - damage spell result
    def process_round_result(self):
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

        def get_spells_by_type(actions, type):
            spell_actions = list()
            for action in actions:
                if spells_manager.spells[action.spell_id].type == type:
                    spell_actions.append(action)
            return spell_actions

        # get and process spells with type 4 - Buf/debuf
        self.apply_buf_spells(get_spells_by_type(actions[2], 4))
        self.round_start_buf_spells()

        #        self.process_direct_spell_actions(spell_actions)

        self.process_attack_defence_actions(actions[0], actions[1])

        self.process_regeneration_actions(actions[3])

        self.round_end_buf_spells()

        for user in self.skirmish_users.values():
            if user.character.health <= 0:
                self.dead_users[user.user_name] = user
                self.remove_from_skirmish(user.user_name)
                self.user_is_dead(user.user_name)
                self.characters[self.victims[user.user_name]].gold += user.character.level + 1
            else:
                self.actions_manager.send_character_info(user.user_name)

        for user_name in self.ran_users:
            if user_name not in self.dead_users.keys():
                self.remove_from_skirmish(user_name)
                self.user_ran(user_name)

    def process_game_result(self):
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
            self.game_ended()
            if len(teams) == 1:
                self.game_win_team("{0}({1})".format(teams[0], ",".join(self.skirmish_users.keys())))
            elif len(users_no_team) == 1:
                self.game_win_user("{0}".format(users_no_team[0]))
            else:
                self.game_win_nobody()
            for user_name in self.skirmish_users.keys():
                self.remove_from_skirmish(user_name)

            self.reset()

    def process_attack_defence_actions(self, attack_actions, defence_actions):
        for action in attack_actions: # attack
            defenders = list() # character : action percent
            for def_action in defence_actions: # defence
                if def_action.whom == action.whom:
                    defenders.append((self.skirmish_users[def_action.who].character, def_action.percent))
            who_character = self.skirmish_users[action.who].character
            whom_character = self.skirmish_users[action.whom].character
            if smarty.is_hit(who_character, action.percent, defenders):
                amount = smarty.get_damage(who_character, action.percent, whom_character)
                if smarty.is_critical_hit(who_character, whom_character):
                    self.critical_hit(action.who)
                    amount *= 1.5
                whom_character.health -= amount
                experience = 0
                if who_character.name != whom_character.name:
                    experience = smarty.get_experience_for_damage(amount)
                    who_character.experience += experience
                    if whom_character.health <= 0 and not action.whom in self.victims.keys():
                        self.victims[action.whom] = action.who
                self.succeeded_attack(action.who, action.whom, amount, whom_character.health, experience, who_character.experience)
            else: # not hit - set exp to defenders
                amount = smarty.get_damage(who_character, action.percent, whom_character)
                if smarty.is_critical_hit(who_character, whom_character):
                    amount *= 1.5
                all_defence = 0
                for defender in defenders:
                    if who_character.name != defender[0].name:
                        all_defence += defender[0].defence
                all_experience = smarty.get_experience_for_defence(amount)
                defence_experience = list()
                for def_action in defence_actions: # defence
                    if def_action.whom == action.whom:
                        def_experience = 0
                        if def_action.who != action.who:
                            def_experience = all_experience*(self.skirmish_users[def_action.who].character.defence/all_defence)
                            who_character.experience += def_experience
                        defence_experience.append("{0}[{1}/{2}]".format(def_action.who, def_experience, who_character.experience))
                self.failed_attack(action.who, action.whom, ",".join(defence_experience))

    def apply_buf_spells(self, turn_actions):
        for turn_action in turn_actions:
            spell = spells_manager.spells[turn_action.spell_id]
            who_character = self.skirmish_users[turn_action.who].character
            whom_character = self.skirmish_users[turn_action.whom].character
            if who_character.mana >= spell.mana:
                who_character.mana -= spell.mana
                if smarty.is_magical_hit(who_character, turn_action.percent, whom_character):
                    spell_action = spells_manager.spells_action_classes[turn_action.spell_id]()
                    spell_action.apply(self.skirmish_users[turn_action.who].character, self.skirmish_users[turn_action.whom].character)
                    self.spell_actions[4].append(spell_action)
                else:
                    self.failed_spell(turn_action.who, turn_action.whom, spell)
            else:
                self.failed_spell_low_mana(turn_action.who, turn_action.whom, spell)

    def round_start_buf_spells(self):
        for spell_action in self.spell_actions[4]:
            spell_action.round_start()
            for online_user in self.location_users.values():
                online_user.send_skirmish_action(self.actions_manager.text_spell_action(spell_action.get_message(online_user.locale)))

    def round_end_buf_spells(self):
        for spell_action in self.spell_actions[4]:
            if spell_action.round_end():
                self.spell_actions[4].remove(spell_action)

        # TODO: optimize algorithm and add long spells effect (store them on character)
    def process_direct_spell_actions(self, actions):
        for action in actions:
            spell = spells_manager.spells[action.spell_id]
            if self.skirmish_users[action.who].character.mana >= spell.mana:
                self.skirmish_users[action.who].character.mana -= spell.mana
                if smarty.is_magical_hit(self.skirmish_users[action.who].character, action.percent, self.skirmish_users[action.whom].character):
                    who_character = self.skirmish_users[action.who].character
                    whom_character = self.skirmish_users[action.whom].character
                    amount = smarty.get_magical_damage(spell, who_character, who_character.percent, whom_character)
                    if smarty.is_critical_magic_hit(who_character, whom_character):
                        amount *= 1.5
                    experience = 0
                    if spell.ordinal == 3: # damage
                        whom_character.health -= amount
                        if who_character.name != whom_character.name:
                            experience = smarty.get_experience_for_spell_damage(amount)
                            who_character.experience += experience
                        # TODO:  self.actions_manager.succeeded_magical_attack(action.who, action.whom, amount, whom_character.health, experience)
                    elif spell.ordinal == 4: # heal:
                        whom_character.health += amount
                        experience = smarty.get_experience_for_spell_damage(amount)
                        who_character.experience += experience
                        # TODO: self.actions_manager.succeeded_magical_attack(action.who, action.whom, amount, whom_character.health, experience)
                else:
                    self.failed_spell(action.who, action.whom, spell)
            else:
                self.failed_spell_low_mana(action.who, action.whom, spell)

    def process_regeneration_actions(self, regeneration_actions):
        for action in regeneration_actions:
            who_character = self.skirmish_users[action.who].character
            who_character.mana += smarty.get_regeneration(who_character)*action.percent

    def remove_from_skirmish(self, user_name):
        self.db_manager.change_character_field_update(user_name, "experience", self.characters[user_name].experience + self.skirmish_users[user_name].character.experience)
        self.actions_manager.send_character_info(user_name)
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

    def registration_started(self):
        self.send_text_action_to_users(self.location_users, 0, None) # registration has been started
        self.actions_manager.registration_started(self.location_users)

    def registration_ended(self):
        self.send_text_action_to_users(self.location_users, 1, None) # registration has been ended

    def round_started(self):
        self.send_text_action_to_users(self.location_users, 2, self.phase) # round has been started
        self.actions_manager.round_started(self.skirmish_users)

    def round_ended(self):
        self.send_text_action_to_users(self.location_users, 3, self.phase) # round has been ended
        self.actions_manager.round_ended(self.skirmish_users)

    def game_started(self):
        for user_name in self.skirmish_users.keys():
            self.characters[user_name] = copy.copy(self.skirmish_users[user_name].character)
            self.skirmish_users[user_name].character.experience = 0
            self.skirmish_users[user_name].character.gold = 0

    def game_ended(self):
        for user_name in self.skirmish_users.keys():
            self.db_manager.change_character_field(user_name, "experience", self.characters[user_name].experience + self.skirmish_users[user_name].character.experience)
            self.db_manager.change_character_field(user_name, "gold", self.characters[user_name].gold + self.skirmish_users[user_name].character.gold)
        self.send_text_action_to_users(self.location_users, 4, None) # game has been ended

    def game_cant_start(self):
        self.send_text_action_to_users(self.location_users, 5, None) # game can't be started, not enough players

    def succeeded_attack(self, who, whom, amount, new_health, experience, full_experience):
        self.send_text_action_to_users(self.location_users, 6, who, whom, amount, new_health, experience, full_experience)

    def failed_attack(self, who, whom, def_experiences):
        self.send_text_action_to_users(self.location_users, 7, who, whom, def_experiences)

    def critical_hit(self, who):
        self.send_text_action_to_users(self.location_users, 8, who)

    def user_is_dead(self, who):
        self.send_text_action_to_users(self.location_users, 9, who)

    def user_ran(self, who):
        self.send_text_action_to_users(self.location_users, 10, who)

    def game_win_team(self, who):
        self.send_text_action_to_users(self.location_users, 11, who)

    def game_win_user(self, who):
        self.send_text_action_to_users(self.location_users, 12, who)

    def game_win_nobody(self):
        self.send_text_action_to_users(self.location_users, 13)

    def failed_spell(self, who, whom, spell):
        for online_user in self.location_users.values():
            online_user.send_skirmish_action(self.actions_manager.text_action(smarty.battle_messages[14], online_user.locale, who, whom, spell.translate(self.online_users[who].locale).name))

    def failed_spell_low_mana(self, who, whom, spell):
        for online_user in self.location_users.values():
            online_user.send_skirmish_action(self.actions_manager.text_action(smarty.battle_messages[15], online_user.locale, who, whom, spell.translate(self.online_users[who].locale).name))

    def send_text_action_to_users(self, online_users, message_number, *args):
        for online_user in online_users.values():
            online_user.send_skirmish_action(self.actions_manager.text_action(smarty.battle_messages[message_number], online_user.locale, *args))
