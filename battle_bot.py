import copy
import random
from threading import Thread
import time
import items_manager
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
        self.long_spells = list()
        self.long_affect_victim_spells = dict()
        self.long_affect_attacker_spells = dict()
        self.long_after_attack_spells = dict()
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
        for spell_actions in self.long_affect_victim_spells.values():
            del spell_actions[:]
        for spell_actions in self.long_affect_attacker_spells.values():
            del spell_actions[:]
        for spell_actions in self.long_after_attack_spells.values():
            del spell_actions[:]
        del self.long_spells[:]
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
                else:
                    self.game_cant_start()
            elif self.phase > 0 and self.counter == 1:
                if self.phase == 1: # first round
                    self.game_started()
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
            else: # remove users from skirmish
                self.ran_users.append(user_name)

        # get and process spells with type 4 - Buf/debuf, over time heal and damage, etc.
        self.apply_long_spells(actions[2])
        self.round_start_long_spells()

        # get and process spells with type 3 - over time spells which affects victim of attack
        self.apply_long_affect_attack_spells(self.get_spells_by_type(actions[2], 3), self.long_affect_victim_spells)
        self.round_start_long_affect_attack_spells(self.long_affect_victim_spells)

        # get and process spells with type 5 - over time spells which affects attacker
        self.apply_long_affect_attack_spells(self.get_spells_by_type(actions[2], 5), self.long_affect_attacker_spells)
        self.round_start_long_affect_attack_spells(self.long_affect_attacker_spells)

        # get and process spells with type 6 - over time spells which affects attacker
        self.apply_long_affect_attack_spells(self.get_spells_by_type(actions[2], 6), self.long_after_attack_spells)
        self.round_start_long_affect_attack_spells(self.long_after_attack_spells)

        # direct damage
        self.process_direct_spell_actions(actions[2], 1)

        self.process_attack_defence_actions(actions[0], actions[1])

        # direct heal
        self.process_direct_spell_actions(actions[2], 2)

        self.process_regeneration_actions(actions[3])

        self.round_end_long_spells()
        self.round_end_long_affect_attack_spells(self.long_affect_victim_spells)
        self.round_end_long_affect_attack_spells(self.long_affect_attacker_spells)
        self.round_end_long_affect_attack_spells(self.long_after_attack_spells)

        for user in self.skirmish_users.values():
            if user.character.health <= 0:
                self.dead_users[user.user_name] = user
                self.remove_from_skirmish(user.user_name)
                self.user_is_dead(user.user_name)
                if user.user_name in self.victims.keys():
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

    # check spells which could affect attack, like phantoms, paralyze, etc.
    def process_affect_attack_spells(self, attack_action):
        who_character = self.skirmish_users[attack_action.who].character
        whom_character = self.skirmish_users[attack_action.whom].character
        spell_stop_attack = False
        if attack_action.who in self.long_affect_attacker_spells.keys():
            for spell_action in self.long_affect_attacker_spells[attack_action.who]:
                if not spell_action.is_succeed_attack(who_character, whom_character):
                    spell_stop_attack = True
                    for online_user in self.location_users.values():
                        online_user.send_skirmish_action(self.actions_manager.text_spell_action(spell_action.get_attack_message(online_user.locale)))
                    break
        if not spell_stop_attack:
            if attack_action.whom in self.long_affect_victim_spells.keys():
                for spell_action in self.long_affect_victim_spells[attack_action.whom]:
                    if not spell_action.is_succeed_attack(who_character, whom_character):
                        spell_stop_attack = True
                        for online_user in self.location_users.values():
                            online_user.send_skirmish_action(self.actions_manager.text_spell_action(spell_action.get_attack_message(online_user.locale)))
                        break
        return spell_stop_attack

    # check spells which be applied after attack, like mirror, plague, second life, etc.
    def process_after_attack_spells(self, attack_action, damage):
        who_character = self.skirmish_users[attack_action.who].character
        if attack_action.whom in self.long_after_attack_spells.keys():
            for spell_action in self.long_after_attack_spells[attack_action.whom]:
                spell_action.process_after_attack(who_character, damage)
                for online_user in self.location_users.values():
                    online_user.send_skirmish_action(self.actions_manager.text_spell_action(spell_action.get_after_attack_message(online_user.locale)))

    def process_attack_defence_actions(self, attack_actions, defence_actions):
        for action in attack_actions: # attack
            if not self.process_affect_attack_spells(action): # spells didn't help, calculate hit
                defenders = list() # character : action percent
                for def_action in defence_actions: # defence
                    if def_action.whom == action.whom:
                        defenders.append((self.skirmish_users[def_action.who].character, def_action.percent))
                who_character = self.skirmish_users[action.who].character
                whom_character = self.skirmish_users[action.whom].character
                if smarty.is_hit(who_character, action.percent, defenders):
                    damage = smarty.get_damage(who_character, action.percent, whom_character)
                    if smarty.is_critical_hit(who_character, whom_character):
                        self.critical_hit(action.who)
                        damage *= 1.5
                    whom_character.health -= damage
                    experience = 0
                    if who_character.name != whom_character.name:
                        experience = smarty.get_experience_for_damage(damage)
                        who_character.experience += experience
                        if whom_character.health <= 0 and not action.whom in self.victims.keys():
                            self.victims[action.whom] = action.who
                    self.succeeded_attack(action.who, action.whom, damage, whom_character.health, experience, who_character.experience)
                    self.process_after_attack_spells(action, damage)
                else: # not hit - set exp to defenders
                    damage = smarty.get_damage(who_character, action.percent, whom_character)
                    if smarty.is_critical_hit(who_character, whom_character):
                        damage *= 1.5
                    all_defence = 0
                    for defender in defenders:
                        if who_character.name != defender[0].name:
                            all_defence += defender[0].defence
                    all_experience = smarty.get_experience_for_defence(damage)
                    defence_experience = list()
                    for def_action in defence_actions: # defence
                        if def_action.whom == action.whom:
                            def_experience = 0
                            def_character = self.skirmish_users[def_action.who].character
                            if def_action.who != action.who:
                                def_experience = all_experience*(def_character.defence/all_defence)
                                def_character.experience += def_experience
                            defence_experience.append("{0}[{1}/{2}]".format(def_action.who, def_experience, def_character.experience))
                    self.failed_attack(action.who, action.whom, ",".join(defence_experience))

    def get_spells_by_type(self, turn_actions, type):
        spell_actions = list()
        for action in turn_actions:
            if spells_manager.spells[action.spell_id].type == type:
                spell_actions.append(action)
        return spell_actions

    def apply_long_spells(self, spell_actions):
        turn_actions = self.get_spells_by_type(spell_actions, 4)
        for turn_action in turn_actions:
            spell_action = spells_manager.spells_action_classes[turn_action.spell_id]()
            spell_action.init(self.skirmish_users[turn_action.who].character, self.skirmish_users[turn_action.whom].character)
            if spell_action.consume_mana():
                if spell_action.is_hit(turn_action.percent):
                    self.long_spells.append(spell_action)
                else:
                    self.failed_spell(spell_action)
            else:
                self.failed_spell_low_mana(spell_action)

    def apply_long_affect_attack_spells(self, spell_actions, spells_container):
        for turn_action in spell_actions:
            spell_action = spells_manager.spells_action_classes[turn_action.spell_id]()
            spell_action.init(self.skirmish_users[turn_action.who].character, self.skirmish_users[turn_action.whom].character)
            if spell_action.consume_mana():
                if spell_action.is_hit(turn_action.percent):
                    whom_name = spell_action.whom_character.name
                    if not whom_name in spells_container.keys():
                        spells_container[whom_name] = list()
                    position = len(spells_container[whom_name]) # insert at the end if there is no the same spell. Replace the same spell otherwise
                    for i in range(len(spells_container[whom_name])):
                        if spells_container[whom_name][i].spell_info.id == spell_action.spell_info.id:
                            spells_container[whom_name][i].on_effect_end()
                            spells_container[whom_name].pop(i)
                            position = i
                            break
                    spells_container[whom_name].insert(position, spell_action)
                else:
                    self.failed_spell(spell_action)
            else:
                self.failed_spell_low_mana(spell_action)

    def round_start_long_spells(self):
        for spell_action in self.long_spells:
            spell_action.round_start()
            for online_user in self.location_users.values():
                online_user.send_skirmish_action(self.actions_manager.text_spell_action(spell_action.get_message(online_user.locale)))

    def round_start_long_affect_attack_spells(self, spells_container):
        for spell_actions in spells_container.values():
            for spell_action in spell_actions:
                spell_action.round_start()
                for online_user in self.location_users.values():
                    online_user.send_skirmish_action(self.actions_manager.text_spell_action(spell_action.get_message(online_user.locale)))

    def round_end_long_spells(self):
        for spell_action in self.long_spells:
            if spell_action.round_end():
                self.long_spells.remove(spell_action)

    def round_end_long_affect_attack_spells(self, spells_container):
        for spell_actions in spells_container.values():
            for spell_action in spell_actions:
                if spell_action.round_end():
                    spells_container[spell_action.whom_character.name].remove(spell_action)

    def process_direct_spell_actions(self, spell_actions, type):
        turn_actions = self.get_spells_by_type(spell_actions, type)
        for turn_action in turn_actions:
            spell_action = spells_manager.spells_action_classes[turn_action.spell_id]()
            spell_action.init(self.skirmish_users[turn_action.who].character, self.skirmish_users[turn_action.whom].character)
            if spell_action.consume_mana():
                if spell_action.is_hit(turn_action.percent):
                    if type == 1: # damage
                        spell_action.process(turn_action.percent)
                    elif type == 2: # heal
                        spell_action.process(turn_action.percent, self.characters[turn_action.whom].health)
                    for online_user in self.location_users.values():
                        online_user.send_skirmish_action(self.actions_manager.text_spell_action(spell_action.get_message(online_user.locale)))
                    if self.skirmish_users[turn_action.whom].character.health <= 0 and not turn_action.whom in self.victims.keys():
                        self.victims[turn_action.whom] = turn_action.who
                else:
                    self.failed_spell(spell_action)
            else:
                self.failed_spell_low_mana(spell_action)

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
        if self.phase > 0 and user_name in self.skirmish_users:
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
        for skirmish_user in self.skirmish_users.values():
            skirmish_user.reset_turn()

    def round_ended(self):
        self.send_text_action_to_users(self.location_users, 3, self.phase) # round has been ended
        self.actions_manager.round_ended(self.skirmish_users)

    def game_started(self):
        self.actions_manager.game_started(self.skirmish_users)
        for user_name in self.skirmish_users.keys():
            self.characters[user_name] = copy.copy(self.skirmish_users[user_name].character)
            self.skirmish_users[user_name].character.experience = 0
            self.skirmish_users[user_name].character.gold = 0

    def game_ended(self):
        for user_name in self.skirmish_users.keys():
            self.db_manager.change_character_field(user_name, "experience", self.characters[user_name].experience + self.skirmish_users[user_name].character.experience)
            self.db_manager.change_character_field(user_name, "gold", self.characters[user_name].gold + self.skirmish_users[user_name].character.gold)
            self.skirmish_users[user_name].reset_turn()
        self.send_text_action_to_users(self.location_users, 4, None) # game has been ended

    def game_cant_start(self):
        self.send_text_action_to_users(self.location_users, 5, None) # game can't be started, not enough players

    def succeeded_attack(self, who, whom, amount, new_health, experience, full_experience):
        for online_user in self.location_users.values():
            text_action = self.actions_manager.text_action(
                smarty.battle_messages[6],
                online_user.locale,
                who,
                whom,
                items_manager.get_current_weapon_name(self.location_users[who].character, online_user.locale),
                amount,
                new_health,
                experience,
                full_experience)
            online_user.send_skirmish_action(text_action)

    def failed_attack(self, who, whom, def_experiences):
        for online_user in self.location_users.values():
            text_action = self.actions_manager.text_action(
                smarty.battle_messages[7],
                online_user.locale,
                who,
                whom,
                items_manager.get_current_weapon_name(self.location_users[who].character, online_user.locale),
                def_experiences)
            online_user.send_skirmish_action(text_action)

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

    def failed_spell(self, spell_action):
        for online_user in self.location_users.values():
            online_user.send_skirmish_action(self.actions_manager.text_spell_action(spell_action.get_failed_message(online_user.locale)))

    def failed_spell_low_mana(self, spell_action):
        for online_user in self.location_users.values():
            online_user.send_skirmish_action(self.actions_manager.text_spell_action(spell_action.get_low_mana_message(online_user.locale)))

    def send_text_action_to_users(self, online_users, message_number, *args):
        for online_user in online_users.values():
            online_user.send_skirmish_action(self.actions_manager.text_action(smarty.battle_messages[message_number], online_user.locale, *args))
