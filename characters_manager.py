from collections import deque
import items_manager
from online_users_holder import Action
import smarty

__author__ = 'Pavel Padinker'

# action types are:
# 0 - character info update
# 1 - fill team div with content for creation
# 2 - fill team div with content with team info
# 3 - invitation to team

class UserInfo:
    def __init__(self, callback, locale):
        self.callback = callback
        self.locale = locale
        self.cache = deque()

    def set_callback(self, callback):
        if len(self.cache) != 0 and callback:
            callback(self.cache.popleft())
        else:
            self.callback = callback

    def send_action(self, action):
        if self.callback:
            # to avoid replacement of callback in process of callback call
            callback_tmp = self.callback
            self.callback = None
            callback_tmp(action)
        else:
            self.add_to_cache(action)

    def add_to_cache(self, action):
        self.cache.append(action)

class CharactersManager:
    def __init__(self, db_manager, online_users_holder):
        self.db_manager = db_manager
        self.online_users_holder = online_users_holder

    @property
    def online_users(self):
        return self.online_users_holder.online_users

    def subscribe(self, user_name, callback, locale):
        self.online_users[user_name].set_character_callback(callback)

    def unsubscribe(self, user_name):
        if user_name in self.online_users:
            self.online_users[user_name].set_character_callback(None)

    def send_create_team(self, user_name):
        self.online_users[user_name].send_character_action(Action(2, {}))

    def create_team_info_action(self, team_name):
        return Action(3, {
            "team_name" : team_name,
            # TODO: add team gold in special team table
            "team_gold" : 0,
            "members" : self.get_team_members(team_name)
        })

    def create_invite_action(self, user_name, team_name):
        return Action(4, {
            "user_name" : user_name,
            "team_name" : team_name,
            })

    def send_info(self, user_name):
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
            str(character.exp),
            str(character.gold),
            team_name,
            str(character.rank_in_team)
        ]

        self.online_users[user_name].send_character_action(Action(0, {"character_info" : ":".join(character_info)}))

    def send_stuff(self, user_name):
        character = self.online_users[user_name].character
        locale = self.online_users[user_name].locale

        self.online_users[user_name].send_character_action(Action(1, {
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
        }))

    def user_enter(self, user_name, locale):
        self.send_info(user_name)
        self.send_stuff(user_name)
        character = self.online_users[user_name].character
        if character.team_name:
            # character is in team
            self.send_team_info_to_user(user_name, character.team_name)
        else:
            # character is not in team
            self.send_create_team(user_name)

    def create_team(self, user_name, team_name):
        create_response = {
            "error" : "False",
            "msg" : ""
        }
        if not self.online_users[user_name].character.team_name:
            if len(self.get_team_members(team_name)) == 0:
                self.db_manager.create_team(user_name, team_name)
                self.send_team_info_to_user(user_name, team_name)
                self.send_info(user_name)
            else:
                create_response["error"] = True
                create_response["msg"] = self.online_users[user_name].locale.translate(smarty.error_messages[0])
        else:
            create_response["error"] = True
            create_response["msg"] = self.online_users[user_name].locale.translate(smarty.error_messages[1])

        return create_response

    def send_team_info_to_user(self, user_name, team_name):
        self.online_users[user_name].send_character_action(self.create_team_info_action(team_name))

    def send_team_info_to_members(self, team_name):
        members = self.get_team_members(team_name)
        action = self.create_team_info_action(team_name)
        for member_name in members.keys():
            if member_name in self.online_users.keys():
                self.online_users[member_name].send_character_action(action)

    def send_invite(self, invite_user_name, user_name, team_name):
        self.online_users[invite_user_name].send_character_action(self.create_invite_action(user_name, team_name))

    def get_team_members(self, team_name):
        result = dict()
        members = self.db_manager.get_team_members(team_name)
        for member in members:
            result[member.name] = member.rank_in_team

        return result

    def promote_user(self, user_name, promote_user):
        if user_name != promote_user:
            user_boss = self.online_users[user_name].character
            if user_boss.rank_in_team < 2:
                user_for_promotion = self.online_users[promote_user].character
                if user_boss.team_name == user_for_promotion.team_name and user_for_promotion.rank_in_team > user_boss.rank_in_team:
                    self.db_manager.change_character_field(promote_user, "rank_in_team", user_for_promotion.rank_in_team - 1)
                    self.send_team_info_to_members(user_for_promotion.team_name)
                    self.send_info(promote_user)

    def demote_user(self, user_name, demote_user):
        if user_name != demote_user:
            user_boss = self.online_users[user_name].character
            if user_boss.rank_in_team < 2:
                user_for_demotion = self.online_users[demote_user].character
                if user_boss.team_name == user_for_demotion.team_name and user_for_demotion.rank_in_team > user_boss.rank_in_team and user_for_demotion.rank_in_team != 5:
                    self.db_manager.change_character_field(demote_user, "rank_in_team", user_for_demotion.rank_in_team + 1)
                    self.send_team_info_to_members(user_for_demotion.team_name)
                    self.send_info(demote_user)

    def remove_user_from_team(self, user_name, remove_user_name):
        if user_name != remove_user_name:
            user_boss = self.online_users[user_name].character
            if user_boss.rank_in_team < 2:
                user_for_removing = self.online_users[remove_user_name].character
                if user_boss.team_name == user_for_removing.team_name and user_for_removing.rank_in_team > user_boss.rank_in_team :
                    self.db_manager.change_user_team(remove_user_name, None, 0)
                    self.send_team_info_to_members(user_boss.team_name)
                    self.send_info(remove_user_name)
                    self.send_create_team(remove_user_name)

    def invite_user_to_team(self, user_name, invite_user_name):
        invite_response = {
            "error" : "False",
            "msg" : ""
        }
        user_boss = self.online_users[user_name].character
        if user_boss.rank_in_team < 2:
            user_for_inviting = self.online_users[invite_user_name].character
            if not user_for_inviting.team_name:
                self.send_invite(invite_user_name, user_name, user_boss.team_name)
                invite_response["msg"] = self.online_users[user_name].locale.translate(smarty.error_messages[4])
            else:
                invite_response["error"] = "True"
                invite_response["msg"] = self.online_users[user_name].locale.translate(smarty.error_messages[3]) % {"user_name" : invite_user_name}

        return invite_response

    def user_join_team(self, joined_user, invited_user, team_name):
        user_boss = self.online_users[invited_user].character
        if user_boss.rank_in_team < 2:
            user_for_join = self.online_users[joined_user].character
            if not user_for_join.team_name:
                self.db_manager.change_user_team(joined_user, team_name, 5)
                self.send_team_info_to_members(team_name)
                self.send_info(joined_user)

    def user_leave_team(self, user_name):
        user = self.online_users[user_name].character
        # if user is leader
        if user.rank_in_team == 0:
            members = self.get_team_members(user.team_name)
            # if there are no other leaders
            if members.values().count(0) == 1:
                # remove team
                for member_name in members.keys():
                    self.db_manager.change_user_team(member_name, None, 0)
                    self.send_info(member_name)
                    self.send_create_team(member_name)
                return
        self.db_manager.change_user_team(user_name, None, 0)
        self.send_info(user_name)
        self.send_create_team(user_name)
        self.send_team_info_to_members(user.team_name)

    def put_on_item(self, user_name, thing_id):
        result = False
        int_id = int(thing_id)
        # get type of thing, e.g. weapon, shield, head, etc.
        item_type = items_manager.get_item_type(int_id)
        character = self.online_users[user_name].character
        items = character[item_type].split(",")
        # check if character has thing and can put it on
        if thing_id in items and items_manager.check_item(character, int_id):
            old_item_id = items[0]
            # put it on by changing its place with first one
            thing_pos = items.index(thing_id)
            items[0], items[thing_pos] = items[thing_pos], items[0]
            self.db_manager.change_character_field(user_name, item_type, ",".join(items))
            self.send_stuff(user_name)

            # get bonuses of old thing to subtract them from character
            old_bonuses = items_manager.get_bonuses(int(old_item_id))
            # get bonuses of new thing to add them from character
            bonuses = items_manager.get_bonuses(int_id)
            # add old bonuses not in new ones
            for bonus_name in old_bonuses.keys():
                if not bonus_name in bonuses:
                    bonuses[bonus_name] = - old_bonuses[bonus_name]
                else:
                    bonuses[bonus_name] = bonuses[bonus_name] - old_bonuses[bonus_name]
            # calculate new character stats
            for bonus_name in bonuses.keys():
                bonuses[bonus_name] = character[bonus_name] + bonuses[bonus_name]
            self.db_manager.change_character_fields(user_name, bonuses)
            self.send_info(user_name)
            result = True

        return result

    def buy_item(self, user_name, item_id):
        character = self.online_users[user_name].character
        item = items_manager.items[int(item_id)]
        if character.gold >= item[5]: # if character can buy it
            update_fields = dict()
            update_fields["gold"] = character.gold - item[5]
            item_type = items_manager.get_item_type(item[0])
            update_fields[item_type] = ",".join([character[item_type], item_id])
            self.db_manager.change_character_fields(user_name, update_fields)
            self.send_info(user_name)
            self.send_stuff(user_name)