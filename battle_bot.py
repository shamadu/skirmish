import copy
import random
from threading import Thread
import time
from users_holder import Action
import items_manager
import smarty
import spells_manager

__author__ = 'PavelP'

class BattleBot(Thread):
    # skirmish action types are:
    # 0 - battle state
    # 1 - add turn div
    # 2 - set skirmish users
    # 3 - can join
    # 4 - can leave
    # 5 - can do turn
    # 6 - can cancel turn
    # 7 - wait for result
    # 8 - reset to initial
    # 9 - message action
    # 10 - add skirmish user
    # 11 - remove skirmish user
    def battle_state_action(self, state):
        return Action(0, {"state" : state})

    def add_turn_div_action(self, user_name, skirmish_users):
        return Action(1, self.div_args(user_name, skirmish_users))

    def can_join_action(self):
        return Action(3, {})

    def can_leave_action(self):
        return Action(4, {})

    def can_do_turn_action(self, user_name, skirmish_users):
        return Action(5, {"turn_info" : skirmish_users[user_name].get_previous_turn_string()})

    def can_cancel_turn_action(self, user_name, skirmish_users):
        return Action(6, {"turn_info" : skirmish_users[user_name].get_previous_turn_string()})

    def wait_for_result_action(self, user_name, skirmish_users):
        return Action(7, {"turn_info" : skirmish_users[user_name].get_previous_turn_string()})

    def reset_to_initial_action(self):
        return Action(8, {})

    def text_action(self, message, locale, *args):
        translated_message = locale.translate(message)
        if args:
            translated_message = translated_message.format(*args)
        return Action(9, {"battle_message" : translated_message})

    def text_spell_action(self, message):
        return Action(9, {"battle_message" : message})

    def div_args(self, user_name, skirmish_users):
        user = skirmish_users[user_name]
        actions = list()
        count = smarty.get_attack_count(user.battle_character.class_id, user.battle_character.level)
        for i in range(count):
            actions.append((0, user.locale.translate(smarty.main_abilities[0])))
        count = smarty.get_defence_count(user.battle_character.class_id, user.battle_character.level)
        for i in range(count):
            actions.append((1, user.locale.translate(smarty.main_abilities[1])))
        count = smarty.get_spell_count(user.battle_character.class_id, user.battle_character.level)
        for i in range(count):
            actions.append((2, smarty.get_ability_name(user.battle_character.class_id, user.locale)))
        actions.append((3, smarty.get_substance_name(user.battle_character.class_id, user.locale)))
        return {
            "actions" : actions,
            "spells" : spells_manager.get_spells(user.battle_character, user.locale)
        }

    def add_skirmish_user_action(self, user_name):
        user = self.location_users[user_name]
        if not user.character.team_name:
            return Action(10, {"skirmish_user" : user.user_name})
        return Action(10, {"skirmish_user" : "%(user_name)s:%(team_name)s" % {"user_name" : user.user_name, "team_name" : user.character.team_name}})

    def remove_skirmish_user_action(self, user_name):
        return Action(11, {"skirmish_user" : user_name})

    def __init__(self, users_holder, db_manager, characters_manager, location):
        Thread.__init__(self)
        self.location_users = users_holder.location_users[location]
        self.battle_users = dict()
        self.battle_characters = list()
        self.characters_manager = characters_manager
        self.db_manager = db_manager
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
        self.dead_users = list()
        self.ran_users = list()
        self.teams = dict() # <team name>:list(team members)

    def reset(self):
        del self.ran_users[:]
        del self.dead_users[:]
        self.battle_users.clear()
        for spell_actions in self.long_affect_victim_spells.values():
            del spell_actions[:]
        for spell_actions in self.long_affect_attacker_spells.values():
            del spell_actions[:]
        for spell_actions in self.long_after_attack_spells.values():
            del spell_actions[:]
        del self.long_spells[:]
        self.phase = -1
        self.counter = 0
        self.send_action_to_users(0, None) # truce started
        del self.battle_characters[:]

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
                if self.can_start():
                    self.phase = 1
            elif self.phase > 0 and self.counter == 1:
                if self.phase == 1: # first round
                    self.game_started()
                self.round_started()
            elif self.phase > 0 and (self.counter == smarty.turn_time
                                     or len(self.ran_users) + self.turn_done_count == len(self.battle_users)):
                self.counter = 0
                self.phase += 1
                self.turn_done_count = 0
                self.process_round_result()
                self.round_ended()
                self.process_game_result()

            self.counter += 1

            time.sleep(1)
            pass

    # can start only if there is no clear advantage of one team
    def can_start(self):
        if len(self.teams) > 1 or None in self.teams.keys() and len(self.teams[None]) > 1: # more than one team or user
            team_levels = list()
            no_team_levels = list()
            for team_name in self.teams.keys(): # team is list
                team = self.teams[team_name]
                if team_name:
                    team_sum_level = 0
                    for member in team:
                        team_sum_level += member.battle_character.level
                    team_levels.append(team_sum_level)
                else:
                    for member in team:
                        no_team_levels.append(member.battle_character.level)
            max_sum_level = 0
            if len(team_levels) > 0:
                max_sum_level = max(team_levels)
            max_character_level = 0
            if len(no_team_levels) > 0:
                max_character_level = max(no_team_levels)
            if max_sum_level > max_character_level:
                team_levels.remove(max_sum_level)
                # 0.5 from sum of levels of the strongest team should be not more than sum of levels of the rest of players
                if max_sum_level*0.5 <= sum(team_levels, sum(no_team_levels)):
                    return True
            else:
                no_team_levels.remove(max_character_level)
                # 0.5 from level of the strongest character should be not more than sum of levels of the rest of players
                if max_character_level*0.5 < sum(team_levels, sum(no_team_levels)):
                    return True
        return False



    def process_round_result(self):
        # collect actions from every user
        skirmish_users_names = self.battle_users.keys()
        random.shuffle(skirmish_users_names)
        actions = { # action type : result action
            0 : list(), # attack
            1 : list(), # defence
            2 : list(), # spell/ability
            3 : list() # regeneration
        }
        for user_name in skirmish_users_names:
            skirmish_user = self.battle_users[user_name]
            if skirmish_user.is_turn_done(): # process user's turn
                for action in skirmish_user.get_turn_info():
                    actions[action.type].append(action)
                skirmish_user.reset_turn()
            elif not user_name in self.ran_users: # if not ran yet - mark as ran now
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

        for user in self.battle_users.values():
            if user.battle_character.health <= 0:
                self.dead_users.append(user.user_name)
                self.battle_users[user.user_name].state = 3 # dead
                if user.battle_character.killer_name:
                    self.add_gold(user.battle_character.killer_name, (user.battle_character.level + 1)*10)
                user.battle_character.killer_name = None
                self.send_text_action_to_users(9, user.user_name) # user is dead
            else:
                self.characters_manager.send_character_info(user.user_name)
        for user in self.battle_users.values():
            if user.battle_character.health <= 0:
                self.remove_from_skirmish(user.user_name)

        for user_name in self.ran_users:
            if user_name not in self.dead_users:
                self.battle_users[user_name].state = 2 # ran
                self.remove_from_skirmish(user_name)
                self.send_text_action_to_users(10, user_name) # user ran
        del self.ran_users[:]

    def process_game_result(self):
        # if there is just users of one team or one user without team - end game
        if len(self.teams) < 2 and (None not in self.teams.keys() or len(self.teams[None]) < 2): # process game result
            if len(self.teams) > 0:
                if None not in self.teams.keys():
                    self.send_text_action_to_users(11, "{0}({1})".format(self.teams.keys()[0], ", ".join(self.battle_users.keys()))) # game win team
                else:
                    self.send_text_action_to_users(12, self.teams[None][0].user_name) # game win user
                for user_name in self.battle_users.keys():
                    self.add_gold(user_name, len(self.battle_characters)*10)
                    self.battle_users[user_name].state = 0 # default
                    self.remove_from_skirmish(user_name)
            else:
                self.send_text_action_to_users(13) # game win nobody

            self.reset()

    # check spells which could affect attack, like phantoms, paralyze, etc.
    def process_affect_attack_spells(self, attack_action):
        who_character = self.battle_users[attack_action.who].battle_character
        whom_character = self.battle_users[attack_action.whom].battle_character
        spell_stop_attack = False
        if attack_action.who in self.long_affect_attacker_spells.keys():
            for spell_action in self.long_affect_attacker_spells[attack_action.who]:
                if not spell_action.is_succeed_attack(who_character, whom_character):
                    spell_stop_attack = True
                    for online_user in self.location_users.values():
                        online_user.send_action(self.text_spell_action(spell_action.get_attack_message(online_user.locale)))
                    break
        if not spell_stop_attack:
            if attack_action.whom in self.long_affect_victim_spells.keys():
                for spell_action in self.long_affect_victim_spells[attack_action.whom]:
                    if not spell_action.is_succeed_attack(who_character, whom_character):
                        spell_stop_attack = True
                        for online_user in self.location_users.values():
                            online_user.send_action(self.text_spell_action(spell_action.get_attack_message(online_user.locale)))
                        break
        return spell_stop_attack

    # check spells which be applied after attack, like mirror, plague, second life, etc.
    def process_after_attack_spells(self, attack_action, damage):
        who_character = self.battle_users[attack_action.who].battle_character
        if attack_action.whom in self.long_after_attack_spells.keys():
            for spell_action in self.long_after_attack_spells[attack_action.whom]:
                spell_action.process_after_attack(who_character, damage)
                self.add_experience(spell_action.who_character.name, spell_action.experience)
                for online_user in self.location_users.values():
                    online_user.send_action(self.text_spell_action(spell_action.get_after_attack_message(online_user.locale)))

    def process_attack_defence_actions(self, attack_actions, defence_actions):
        for action in attack_actions: # attack
            if not self.process_affect_attack_spells(action): # spells didn't help, calculate hit
                defenders = list() # character : action percent
                for def_action in defence_actions: # defence
                    if def_action.whom == action.whom:
                        defenders.append((self.battle_users[def_action.who].battle_character, def_action.percent))
                who_character = self.battle_users[action.who].battle_character
                whom_character = self.battle_users[action.whom].battle_character
                if smarty.is_hit(who_character, action.percent, defenders):
                    damage = smarty.get_damage(who_character, action.percent, whom_character)
                    if smarty.is_critical_hit(who_character, whom_character):
                        self.send_text_action_to_users(8, action.who) # critical hit
                        damage *= 1.5
                    whom_character.health -= damage
                    experience = 0
                    if who_character.name != whom_character.name:
                        experience = smarty.get_experience_for_damage(damage)
                        self.add_experience(who_character.name, experience)
                        if whom_character.health <= 0 and not whom_character.killer_name:
                            whom_character.killer_name = action.who
                    self.succeeded_attack(
                        action.who,
                        action.whom,
                        damage,
                        smarty.apply_hp_colour(whom_character.health, whom_character.full_health),
                        experience,
                        who_character.experience)
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
                            def_character = self.battle_users[def_action.who].battle_character
                            if def_action.who != action.who:
                                def_experience = round(all_experience*(def_character.defence/all_defence))
                                self.add_experience(def_character.name, def_experience)
                            defence_experience.append("<b>{0}</b>[<font class=\"font-exp\">{1}</font>/<font class=\"font-exp\">{2}</font>]".format(def_action.who, def_experience, def_character.experience))
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
            spell_action.init(self.battle_users[turn_action.who].battle_character, self.battle_users[turn_action.whom].battle_character)
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
            spell_action.init(self.battle_users[turn_action.who].battle_character, self.battle_users[turn_action.whom].battle_character)
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
            self.add_experience(spell_action.who_character.name, spell_action.experience)
            for online_user in self.location_users.values():
                online_user.send_action(self.text_spell_action(spell_action.get_message(online_user.locale)))

    def round_start_long_affect_attack_spells(self, spells_container):
        for spell_actions in spells_container.values():
            for spell_action in spell_actions:
                spell_action.round_start()
                self.add_experience(spell_action.who_character.name, spell_action.experience)
                for online_user in self.location_users.values():
                    online_user.send_action(self.text_spell_action(spell_action.get_message(online_user.locale)))

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
            who_character = self.battle_users[turn_action.who].battle_character
            whom_character = self.battle_users[turn_action.whom].battle_character
            spell_action = spells_manager.spells_action_classes[turn_action.spell_id]()
            spell_action.init(who_character, whom_character)
            if spell_action.consume_mana():
                if spell_action.is_hit(turn_action.percent):
                    if type == 1: # damage
                        spell_action.process(turn_action.percent)
                    elif type == 2: # heal
                        spell_action.process(turn_action.percent, whom_character.full_health)
                    self.add_experience(spell_action.who_character.name, spell_action.experience)
                    for online_user in self.location_users.values():
                        online_user.send_action(self.text_spell_action(spell_action.get_message(online_user.locale)))
                    if whom_character.health <= 0 and not whom_character.killer_name:
                        whom_character.killer_name = turn_action.who
                else:
                    self.failed_spell(spell_action)
            else:
                self.failed_spell_low_mana(spell_action)

    def process_regeneration_actions(self, regeneration_actions):
        for action in regeneration_actions:
            who_character = self.battle_users[action.who].battle_character
            who_character.mana += smarty.get_regeneration(who_character)*action.percent
            who_character.mana = min(who_character.mana, self.battle_users[action.who].character.mana)

    def remove_from_skirmish(self, user_name):
        user = self.battle_users[user_name]
        team_name = user.battle_character.team_name
        # remove from battle team
        self.teams[team_name].remove(user)
        if len(self.teams[team_name]) == 0:
            self.teams.pop(team_name)
        self.battle_users[user_name].reset_turn()
        battle_character = user.battle_character
        # add team gold to team
        if battle_character.team_name:
            self.db_manager.change_team_field(team_name, "gold", self.db_manager.get_team_info(team_name).gold + battle_character.team_gold)
            self.characters_manager.send_team_info_to_members(team_name)

        bonus_fields = {
            "experience" : user.character.experience + battle_character.experience,
            "gold" : user.character.gold + battle_character.gold
        }
        level = 0
        while smarty.level_up_experiences[battle_character.level + level] < bonus_fields["experience"]: # then lvl up
            level += 1
        if level > 0:
            bonus_fields.update({
                "level" : battle_character.level + level,
                "strength" : battle_character.strength + level,
                "dexterity" : battle_character.dexterity + level,
                "intellect" : battle_character.intellect + level,
                "wisdom" : battle_character.wisdom + level,
                })
        self.db_manager.change_character_fields_update(battle_character.name, bonus_fields)
        if user_name in self.location_users.keys(): # user still in the same location
            self.send_action_to_user(user_name, self.reset_to_initial_action())
        self.send_action_to_all(self.remove_skirmish_user_action(user_name))
        user.battle_character = None
        self.battle_users.pop(user_name)
        self.characters_manager.send_character_info(user_name)

    def user_join(self, user_name):
        if self.phase == 0 and user_name not in self.battle_users.keys():
            user = self.location_users[user_name]
            # add user to battle_users
            self.battle_users[user_name] = user
            user.state = 1 # is in skirmish
            # create battle_character
            user.battle_character = copy.copy(user.character)
            user.battle_character.experience = 0
            user.battle_character.gold = 0
            user.battle_character.team_gold = 0
            user.battle_character.full_health = user.character.health
            user.battle_character.killer_name = None # who killed this character
            self.battle_characters.append(user.battle_character)
            # send actions
            self.send_action_to_user(user_name, self.can_leave_action())
            self.send_action_to_all(self.add_skirmish_user_action(user_name))

            team_name = user.battle_character.team_name
            if not team_name in self.teams:
                self.teams[team_name] = list()
            self.teams[team_name].append(user)


    def user_leave(self, user_name):
        if user_name in self.battle_users.keys():
            user = self.battle_users[user_name]
            if self.phase == 0:
                # remove from battle team
                team_name = user.battle_character.team_name
                self.teams[team_name].remove(user)
                if len(self.teams[team_name]) == 0:
                    self.teams.pop(team_name)
                # send actions
                self.send_action_to_all(self.remove_skirmish_user_action(user_name))
                self.send_action_to_user(user_name, self.can_join_action())
                user.state = 0 # default
                self.battle_characters.remove(user.battle_character)
                user.battle_character = None
                self.battle_users.pop(user_name)
            elif user.state != 2: # didn't run yet
                if user.is_turn_done(): # if did turn - reset it
                    user.reset_turn()
                    self.turn_done_count -= 1
                self.ran_users.append(user_name)
                user.state = 2 # ran
                self.send_action_to_user(user_name, self.reset_to_initial_action())


    def user_turn(self, user_name, turn_info):
        if self.phase > 0 and user_name in self.battle_users:
            self.turn_done_count += 1
            self.battle_users[user_name].set_turn_string(turn_info)
            self.send_action_to_user(user_name, self.can_cancel_turn_action(user_name, self.battle_users))

    def user_turn_cancel(self, user_name):
        if self.phase > 0:
            self.turn_done_count -= 1
            self.battle_users[user_name].reset_turn()
            self.send_action_to_user(user_name, self.can_do_turn_action(user_name, self.battle_users))

    def user_enter(self, user_name):
        # if registration is in progress
        if self.phase == 0:
            self.send_action_to_user(user_name, self.battle_state_action(smarty.battle_messages[1])) # state is registration
            # and if user is not in skirmish, send "can join" action
            if self.location_users[user_name].state != 1: # TODO: don't allow dead or ran users join battle till some payment
                self.send_action_to_user(user_name, self.can_join_action())
            # and if user is in skirmish, send "can leave" action
            elif self.location_users[user_name].state == 1:
                self.send_action_to_user(user_name, self.can_leave_action())
        # if round is in progress
        elif self.phase > 0:
            self.send_action_to_user(user_name, self.battle_state_action(smarty.battle_messages[2].format(self.phase))) # state is round is in progress
            # user can always leave skirmish
            self.send_action_to_user(user_name, self.can_leave_action())
            if self.location_users[user_name].state == 1:
                self.send_action_to_user(user_name, self.add_turn_div_action(user_name, self.battle_users))
            if self.location_users[user_name].state == 2: # user ran
                self.send_action_to_user(user_name, self.reset_to_initial_action())
                # if it's time to do the turn
            if self.counter < smarty.turn_time:
                # if user is in skirmish and the turn isn't done, send "can do turn" action
                if self.location_users[user_name].state == 1:
                    if not self.battle_users[user_name].is_turn_done():
                        self.send_action_to_user(user_name, self.can_do_turn_action(user_name, self.battle_users))
                    # if user is in skirmish and the turn is done, send "can cancel turn" action
                    else:
                        self.send_action_to_user(user_name, self.can_cancel_turn_action(user_name, self.battle_users))
            # all turns were done and if user is in skirmish and the turn is done, send "can cancel turn" action
            elif self.location_users[user_name].state == 1 and self.battle_users[user_name].is_turn_done():
                self.send_action_to_user(user_name, self.wait_for_result_action(user_name, self.battle_users))
        else: # initial state
            self.send_action_to_user(user_name, self.battle_state_action(smarty.battle_messages[0])) # state is truce

    def registration_started(self):
        self.send_action_to_users(1, None) # registration has been started
        for online_user in self.location_users.values():
            online_user.send_action(self.can_join_action())

    def round_started(self):
        self.send_action_to_users(2, self.phase) # round has been started
        for user_name in self.battle_users.keys():
            self.battle_users[user_name].send_action(self.can_do_turn_action(user_name, self.battle_users))

    def round_ended(self):
        for user_name in self.battle_users.keys():
            self.battle_users[user_name].send_action(self.wait_for_result_action(user_name, self.battle_users))

    def game_started(self):
        for skirmish_user in self.battle_users.keys():
            self.send_action_to_user(skirmish_user, self.add_turn_div_action(skirmish_user, self.battle_users))

    def succeeded_attack(self, who, whom, amount, new_health, experience, full_experience):
        for online_user in self.location_users.values():
            text_action = self.text_action(
                smarty.battle_messages[6],
                online_user.locale,
                who,
                whom,
                items_manager.get_current_weapon_name(self.location_users[who].battle_character, online_user.locale),
                amount,
                new_health,
                experience,
                full_experience)
            online_user.send_action(text_action)

    def failed_attack(self, who, whom, def_experiences):
        for online_user in self.location_users.values():
            text_action = self.text_action(
                smarty.battle_messages[7],
                online_user.locale,
                who,
                whom,
                items_manager.get_current_weapon_name(self.location_users[who].battle_character, online_user.locale),
                def_experiences)
            online_user.send_action(text_action)

    def failed_spell(self, spell_action):
        for online_user in self.location_users.values():
            online_user.send_action(self.text_spell_action(spell_action.get_failed_message(online_user.locale)))

    def failed_spell_low_mana(self, spell_action):
        for online_user in self.location_users.values():
            online_user.send_action(self.text_spell_action(spell_action.get_low_mana_message(online_user.locale)))

    def send_text_action_to_users(self, message_number, *args):
        for online_user in self.location_users.values():
            online_user.send_action(self.text_action(smarty.battle_messages[message_number], online_user.locale, *args))

    def send_action_to_users(self, message_number, *args):
        for online_user in self.location_users.values():
            online_user.send_action(self.battle_state_action(online_user.locale.translate(smarty.battle_messages[message_number]).format(*args)))

    def skirmish_user_added(self, user_name):
        self.send_action_to_user(user_name, self.can_leave_action())
        self.send_action_to_all(self.add_skirmish_user_action(user_name))

    def send_action_to_user(self, user_name, action):
        self.location_users[user_name].send_action(action)

    def send_action_to_all(self, action):
        for online_user in self.location_users.values():
            online_user.send_action(action)

    def add_experience(self, user_name, experience):
        team_name = self.battle_users[user_name].battle_character.team_name
        if team_name:
            team_info = self.db_manager.get_team_info(team_name)
            if team_info.experience_sharing == 0: # no sharing
                self.battle_users[user_name].battle_character.experience += experience
            elif team_info.experience_sharing == 1: # 50% sharing
                self.battle_users[user_name].battle_character.experience += round(experience*0.5)
                experience_for_team_mate =  round(experience*0.5/len(self.teams[team_name]))
                for team_mate in self.teams[team_name]:
                    team_mate.battle_character.experience += experience_for_team_mate
            elif team_info.experience_sharing == 2: # 100% sharing
                experience_for_team_mate =  round(experience/len(self.teams[team_name]))
                for team_mate in self.teams[team_name]:
                    team_mate.battle_character.experience += experience_for_team_mate
        else:
            self.battle_users[user_name].battle_character.experience += experience

    def add_gold(self, user_name, gold):
        team_name = self.battle_users[user_name].battle_character.team_name
        if team_name:
            team_info = self.db_manager.get_team_info(team_name)
            battle_character = self.battle_users[user_name].battle_character
            if team_info.gold_tax == 0: # 10%
                battle_character.team_gold += round(gold*0.1)
                gold = round(gold*0.9)
            elif team_info.gold_tax == 1: # 50%
                battle_character.team_gold += round(gold*0.5)
                gold = round(gold*0.5)
            elif team_info.gold_tax == 2: # 100%
                battle_character.team_gold += gold
                gold = 0

            if team_info.gold_sharing == 0: # no sharing
                battle_character.gold += gold
            elif team_info.gold_sharing == 1: # 50% sharing
                battle_character.gold += round(gold*0.5)
                gold_for_team_mate =  round(gold*0.5/len(self.teams[team_name]))
                for team_mate in self.teams[team_name]:
                    team_mate.battle_character.gold += gold_for_team_mate
            elif team_info.gold_sharing == 2: # 100% sharing
                gold_for_team_mate =  round(gold/len(self.teams[team_name]))
                for team_mate in self.teams[team_name]:
                    team_mate.battle_character.gold += gold_for_team_mate
        else:
            self.battle_users[user_name].battle_character.gold += gold