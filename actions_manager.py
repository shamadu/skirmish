from collections import OrderedDict, deque
import items_manager
from online_users import OnlineUserInfo
import smarty

__author__ = 'PavelP'

class Action:
    def __init__(self, type, args):
        self.type = type
        self.args = args
        self.args["type"] = type

class ActionsManager:
    def __init__(self):
        self.online_users = dict()
        self.location_users = {
            "En" : dict(),
            "Ru" : dict()
            }
        self.users_manager = None
        self.characters_manager = None
        self.battle_manager = None

    # user action types are:
    # 0 - show all online and skirmish users
    # 1 - add new user
    # 2 - remove online user
    # 3 - add skirmish users
    # 4 - remove skirmish users
    def initial_users_action(self, online_users, skirmish_users):
        online_user_non_skirmish = list()
        for user_name in online_users.keys():
            if user_name not in skirmish_users.keys():
                online_user_non_skirmish.append(user_name)
        skirmish_users_list = list()
        for user_name in skirmish_users:
            if not skirmish_users[user_name].character.team_name:
                skirmish_users_list.append(user_name)
            else:
                skirmish_users_list.append("%(user_name)s:%(team_name)s" % {"user_name" : user_name, "team_name" : skirmish_users[user_name].character.team_name})
        return Action(0, {"online_users" : ','.join(online_user_non_skirmish), "skirmish_users" : ','.join(skirmish_users_list)})

    def user_online_action(self, user_name):
        return Action(1, {"user" : user_name})

    def user_offline_action(self, user_name):
        return Action(2, {"user" : user_name})

    def add_skirmish_user_action(self, user_name):
        user = self.online_users[user_name]
        if not user.character.team_name:
            return Action(3, {"skirmish_user" : user.user_name})
        return Action(3, {"skirmish_user" : "%(user_name)s:%(team_name)s" % {"user_name" : user.user_name, "team_name" : user.character.team_name}})

    def remove_skirmish_user_action(self, user_name):
        user = self.online_users[user_name]
        if not user.character.team_name:
            return Action(4, {"skirmish_user" : user.user_name})
        return Action(4, {"skirmish_user" : "%(user_name)s:%(team_name)s" % {"user_name" : user.user_name, "team_name" : user.character.team_name}})

    # skirmish action types are:
    # 3 - can join
    # 4 - can leave
    # 5 - can do turn
    # 6 - can cancel turn
    # 7 - wait for result
    # 8 - reset to initial
    # 9 - message action
    def can_join_action(self):
        return Action(3, {})

    def can_leave_action(self):
        return Action(4, {})

    def can_do_turn_action(self, user_name, skirmish_users):
        return Action(5, self.div_args(user_name, skirmish_users))

    def can_cancel_turn_action(self, user_name, skirmish_users):
        return Action(6, self.div_args(user_name, skirmish_users))

    def wait_for_result_action(self, user_name, skirmish_users):
        return Action(7, self.div_args(user_name, skirmish_users))

    def reset_to_initial_action(self):
        return Action(8, {})

    def text_action(self, message_number, args=None):
        if not args:
            args = {}
        args["message_number"] = message_number

        return Action(9, args)

    def div_args(self, user_name, skirmish_users):
        user = skirmish_users[user_name]
        actions = OrderedDict()
        actions[0] = user.locale.translate(smarty.main_abilities[0]), smarty.get_attack_count(user.character.classID, user.character.level)
        actions[1] = user.locale.translate(smarty.main_abilities[1]), smarty.get_defence_count(user.character.classID, user.character.level)
        actions[2] = smarty.get_ability_name(user.character.classID, user.locale) , smarty.get_spell_count(user.character.classID, user.character.level)
        actions[3] = smarty.get_substance_name(user.character.classID, user.locale) , 0
        return {
            "actions" : actions,
            "users" : skirmish_users.keys(),
            "spells" : smarty.get_spells(user.character, user.locale),
            "turn_info" : user.get_turn_info()
        }

    # character action types are:
    # 0 - character info
    # 1 - character stuff
    # 2 - create team
    # 3 - team info
    # 4 - invite to team
    def character_info_action(self, user_name):
        character = self.online_users[user_name].character
        team_name = character.team_name
        if not team_name:
            team_name = ""
        locale = self.online_users[user_name].locale
        character_info = [
            character.name,
            smarty.get_class_name(character.classID, locale),
            str(character.level),
            str(smarty.get_hp_count(character)),
            str(smarty.get_mp_count(character)),
            str(character.strength),
            str(character.dexterity),
            str(character.intellect),
            str(character.wisdom),
            str(character.constitution),
            str(character.attack),
            str(character.defence),
            str(character.magic_attack),
            str(character.magic_defence),
            str(character.armor),
            str(character.experience),
            str(character.gold),
            team_name,
            str(character.rank_in_team)
            ]
        return Action(0, {"character_info" : ":".join(character_info)})

    def character_stuff_action(self, user_name):
        character = self.online_users[user_name].character
        locale = self.online_users[user_name].locale
        return Action(1, {
            # <id1>:<name1>,<id2>:<name2>:...
            "weapon" : ",".join("%s" % ":".join([str(thing[0]), thing[1]]) for thing in items_manager.get_items(character.weapon, locale)),
            "shield" : ",".join("%s" % ":".join([str(thing[0]), thing[1]]) for thing in items_manager.get_items(character.shield, locale)),
            "head" : ",".join("%s" % ":".join([str(thing[0]), thing[1]]) for thing in items_manager.get_items(character.head, locale)),
            "body" : ",".join("%s" % ":".join([str(thing[0]), thing[1]]) for thing in items_manager.get_items(character.body, locale)),
            "left_hand" : ",".join("%s" % ":".join([str(thing[0]), thing[1]]) for thing in items_manager.get_items(character.left_hand, locale)),
            "right_hand" : ",".join("%s" % ":".join([str(thing[0]), thing[1]]) for thing in items_manager.get_items(character.right_hand, locale)),
            "legs" : ",".join("%s" % ":".join([str(thing[0]), thing[1]]) for thing in items_manager.get_items(character.legs, locale)),
            "feet" : ",".join("%s" % ":".join([str(thing[0]), thing[1]]) for thing in items_manager.get_items(character.feet, locale)),
            "cloak" : ",".join("%s" % ":".join([str(thing[0]), thing[1]]) for thing in items_manager.get_items(character.cloak, locale))
        })

    def can_create_team_action(self):
        return Action(2, {})

    def team_info_action(self, team_members):
        return Action(3, {
            "team_name" : self.online_users[team_members.keys()[0]].character.team_name,
            # TODO: add team gold in special team table
            "team_gold" : 0,
            "members" : team_members
        })

    def invite_action(self, user_name, team_name):
        return Action(4, {
            "user_name" : user_name,
            "team_name" : team_name,
            })

    def send_can_create_team(self, user_name):
        self.online_users[user_name].send_character_action(self.can_create_team_action())

    def send_character_info(self, user_name):
        self.online_users[user_name].send_character_action(self.character_info_action(user_name))

    def send_character_stuff(self, user_name):
        self.online_users[user_name].send_character_action(self.character_stuff_action(user_name))

    def send_team_info_to_user(self, user_name, team_members):
        self.online_users[user_name].send_character_action(self.team_info_action(team_members))

    def send_team_info_to_members(self, team_members):
        action = self.team_info_action(team_members)
        for member_name in team_members.keys():
            if member_name in self.online_users.keys():
                self.online_users[member_name].send_character_action(action)

    def send_invite(self, invite_user_name, user_name, team_name):
        self.online_users[invite_user_name].send_character_action(self.invite_action(user_name, team_name))

# users callbacks
    def add_online_user(self, user_name, locale):
        online_users = self.location_users["En"]
        self.send_user_action_to_all(online_users, self.user_online_action(user_name))
        self.online_users[user_name] = OnlineUserInfo(user_name, locale)
        self.location_users["En"][user_name] = self.online_users[user_name]

    def remove_online_user(self, user_name):
        online_users = self.location_users[self.online_users[user_name].location]
        self.send_user_action_to_all(online_users, self.user_offline_action(user_name))
        self.online_users.pop(user_name)

    def change_location(self, user_name, location):
        online_users = self.location_users[self.online_users[user_name].location]
        self.send_user_action_to_all(online_users, self.user_offline_action(user_name))
        self.send_user_action_to_all(self.location_users[location], self.user_online_action(user_name))
        self.location_users[self.online_users[user_name].location].pop(user_name)
        self.location_users[location][user_name] = self.online_users[user_name]

    def user_logout(self, user_name):
        if user_name in self.online_users.keys():
            self.remove_online_user(user_name)

# character callbacks
    def update_character(self, user_name, character):
        self.online_users[user_name].character = character

# skirmish callbacks
    def skirmish_user_added(self, user_name):
        online_users = self.location_users[self.online_users[user_name].location]
        self.send_skirmish_action_to_user(user_name, self.can_leave_action())
        self.send_user_action_to_all(online_users, self.add_skirmish_user_action(user_name))

    def skirmish_user_removed(self, location, user_name):
        online_users = self.location_users[location]
        if self.online_users[user_name].location == location: # user still in the same location
            self.send_skirmish_action_to_user(user_name, self.reset_to_initial_action())
        self.send_user_action_to_all(online_users, self.remove_skirmish_user_action(user_name))

    def skirmish_user_left(self, user_name):
        online_users = self.location_users[self.online_users[user_name].location]
        self.send_skirmish_action_to_user(user_name, self.can_join_action())
        self.send_user_action_to_all(online_users, self.remove_skirmish_user_action(user_name))

    def registration_started(self, location):
        online_users = self.location_users[location]
        self.send_skirmish_action_to_all(online_users, self.text_action(0)) # registration has been started
        self.send_skirmish_action_to_all(online_users, self.can_join_action())

    def registration_ended(self, location):
        online_users = self.location_users[location]
        self.send_skirmish_action_to_all(online_users, self.text_action(1)) # registration has been ended

    def round_started(self, number, location, skirmish_users):
        online_users = self.location_users[location]
        self.send_skirmish_action_to_all(online_users, self.text_action(2, {"round" : number})) # round has been started
        for user_name in skirmish_users.keys():
            skirmish_users[user_name].send_skirmish_action(self.can_do_turn_action(user_name, skirmish_users))

    def round_ended(self, number, location, skirmish_users):
        online_users = self.location_users[location]
        self.send_skirmish_action_to_all(online_users, self.text_action(3, {"round" : number})) # round has been ended
        for user_name in skirmish_users.keys():
            skirmish_users[user_name].send_skirmish_action(self.wait_for_result_action(user_name, skirmish_users))

    def game_ended(self, location):
        online_users = self.location_users[location]
        self.send_skirmish_action_to_all(online_users, self.text_action(4)) # game has been ended

    def game_cant_start(self, location):
        online_users = self.location_users[location]
        self.send_skirmish_action_to_all(online_users, self.text_action(5)) # game can't be started, not enough players

    def user_did_turn(self, user_name, skirmish_users):
        self.send_skirmish_action_to_user(user_name, self.can_cancel_turn_action(user_name, skirmish_users))

    def user_cancel_turn(self, user_name, skirmish_users):
        self.send_skirmish_action_to_user(user_name, self.can_do_turn_action(user_name, skirmish_users))

# util methods
    def send_user_action_to_all(self, online_users, action):
        for online_user in online_users.values():
            online_user.send_user_action(action)

    def send_skirmish_action_to_all(self, online_users, action):
        for online_user in online_users.values():
            online_user.send_skirmish_action(action)

    def send_skirmish_action_to_user(self, user_name, action):
        if user_name in self.online_users.keys():
            self.online_users[user_name].send_skirmish_action(action)

    def user_enter(self, user_name):
        self.online_users[user_name].user_cache = deque()
        self.online_users[user_name].skirmish_cache = deque()
        self.online_users[user_name].character_cache = deque()
        # this sequence is important!
        self.users_manager.user_enter(user_name)
        self.characters_manager.user_enter(user_name)
        self.battle_manager.user_enter(user_name)

    def user_enter_users_manager(self, user_name):
        # TODO: skirmish users could differs for different battle bots
        location = self.online_users[user_name].location
        online_users = self.location_users[location]
        skirmish_users = self.battle_manager.battle_bots[location].skirmish_users
        self.online_users[user_name].send_user_action(self.initial_users_action(online_users, skirmish_users))

    def user_enter_battle_bot(self, user_name, phase, counter, skirmish_users):
        # if registration is in progress
        if phase == 0:
            # and if user is not in skirmish, send "can join" action
            if not user_name in skirmish_users.keys():
                self.send_skirmish_action_to_user(user_name, self.can_join_action())
            # and if user is in skirmish, send "can leave" action
            else:
                self.send_skirmish_action_to_user(user_name, self.can_leave_action())
        # if round is in progress
        elif phase > 0:
            # if it's time to do the turn
            if counter < smarty.turn_time:
                # and if user is in skirmish and the turn isn't done, send "can do turn" action
                if user_name in skirmish_users and not skirmish_users[user_name].is_turn_done():
                    self.send_skirmish_action_to_user(user_name, self.can_do_turn_action(user_name, skirmish_users))
                # and if user is in skirmish and the turn is done, send "can cancel turn" action
                elif user_name in skirmish_users and skirmish_users[user_name].is_turn_done():
                    self.send_skirmish_action_to_user(user_name, self.can_cancel_turn_action(user_name, skirmish_users))
            # all turns were done and if user is in skirmish and the turn is done, send "can cancel turn" action
            elif user_name in skirmish_users and skirmish_users[user_name].is_turn_done():
                self.send_skirmish_action_to_user(user_name, self.wait_for_result_action(user_name, skirmish_users))

    def user_enter_characters_manager(self, user_name, team_members):
        self.send_character_info(user_name)
        self.send_character_stuff(user_name)
        character = self.online_users[user_name].character
        if character.team_name:
            # character is in team
            self.send_team_info_to_user(user_name, team_members)
        else:
            # character is not in team
            self.send_can_create_team(user_name)
