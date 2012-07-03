from users_holder import Action
import items_manager
import smarty
import spells_manager

__author__ = 'Pavel Padinker'

class CharactersManager:
    # character action types are:
    # 200 - character info
    # 201 - character stuff
    # 202 - create team
    # 203 - can create team
    # 204 - team info
    # 205 - invite to team
    def character_info_action(self, user_name):
        character = self.online_users[user_name].character
        team_name = character.team_name
        if not team_name:
            team_name = ""
        locale = self.online_users[user_name].locale
        character_info = [
            character.name,
            smarty.get_race_name(character.race_id, locale),
            smarty.get_class_name(character.class_id, locale),
            str(character.level),
            str(character.health),
            str(character.mana),
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
            str(smarty.level_up_experiences[character.level]),
            str(character.gold),
            team_name,
            str(character.rank_in_team)
        ]

        # if there is battle character - use it
        if self.online_users[user_name].battle_character:
            battle_character = self.online_users[user_name].battle_character
        else: # use common character
            battle_character = self.online_users[user_name].character
        battle_character_info = [
            str(battle_character.health),
            str(battle_character.mana),
            str(battle_character.strength),
            str(battle_character.dexterity),
            str(battle_character.intellect),
            str(battle_character.wisdom),
            str(battle_character.constitution),
            str(battle_character.attack),
            str(battle_character.defence),
            str(battle_character.magic_attack),
            str(battle_character.magic_defence),
            str(battle_character.armor),
            str(battle_character.experience),
            str(battle_character.gold)
        ]
        return Action(200, {"character_info" : ":".join(character_info), "battle_character_info" : ":".join(battle_character_info)})

    def character_stuff_action(self, user_name):
        character = self.online_users[user_name].character
        locale = self.online_users[user_name].locale
        return Action(201, items_manager.get_items(character, locale))

    def character_spells_action(self, user_name):
        character = self.online_users[user_name].character
        locale = self.online_users[user_name].locale
        return Action(202, {
            "spells" : spells_manager.get_spells(character, locale),
            "spells_to_learn" : spells_manager.get_spells_to_learn(character, locale),
            "substance_name" : smarty.get_substance_name(character.class_id, locale)
        })

    def can_create_team_action(self):
        return Action(203, {})

    def team_info_action(self, team_info):
        return Action(204, {
            "team_name" : team_info.team_name,
            "team_gold" : team_info.gold,
            "members" : self.get_team_members(team_info.team_name)
        })

    def invite_action(self, user_name, team_name):
        return Action(205, {
            "user_name" : user_name,
            "team_name" : team_name,
            })

    def __init__(self, db_manager, users_holder):
        self.db_manager = db_manager
        self.online_users = users_holder.online_users

    def create_team(self, user_name, team_name):
        create_response = {
            "error" : "False",
            "msg" : ""
        }
        if not self.online_users[user_name].character.team_name:
            if len(self.get_team_members(team_name)) == 0:
                self.db_manager.create_team(user_name, team_name)
                self.send_team_info_to_user(user_name)
                self.send_character_info(user_name)
            else:
                create_response["error"] = True
                create_response["msg"] = self.online_users[user_name].locale.translate(smarty.error_messages[0])
        else:
            create_response["error"] = True
            create_response["msg"] = self.online_users[user_name].locale.translate(smarty.error_messages[1])

        return create_response

    def get_team_members(self, team_name):
        result = dict()
        members = self.db_manager.get_team_members(team_name)
        for member in members:
            result[member["name"]] = member["rank_in_team"]

        return result

    def promote_user(self, user_name, promote_user):
        if user_name != promote_user:
            user_boss = self.online_users[user_name].character
            if user_boss.rank_in_team < 2: # can promote
                if promote_user in self.online_users.keys(): # promote user is online
                    user_for_promotion = self.online_users[promote_user].character
                    if user_boss.team_name == user_for_promotion.team_name and user_for_promotion.rank_in_team > user_boss.rank_in_team:
                        self.db_manager.change_character_field_update(promote_user, "rank_in_team", user_for_promotion.rank_in_team - 1)
                        self.send_team_info_to_members(user_for_promotion.team_name)
                        self.send_character_info(promote_user)
                else: # promote user if offline
                    user_for_promotion = self.db_manager.get_character(promote_user)
                    if user_boss.team_name == user_for_promotion.team_name and user_for_promotion.rank_in_team > user_boss.rank_in_team:
                        self.db_manager.change_character_field(promote_user, "rank_in_team", user_for_promotion.rank_in_team - 1)
                        self.send_team_info_to_members(user_for_promotion.team_name)

    def demote_user(self, user_name, demote_user):
        if user_name != demote_user:
            user_boss = self.online_users[user_name].character
            if user_boss.rank_in_team < 2:
                if demote_user in self.online_users.keys(): # demote user is online
                    user_for_demotion = self.online_users[demote_user].character
                    if user_boss.team_name == user_for_demotion.team_name and user_for_demotion.rank_in_team > user_boss.rank_in_team and user_for_demotion.rank_in_team != 5:
                        self.db_manager.change_character_field_update(demote_user, "rank_in_team", user_for_demotion.rank_in_team + 1)
                        self.send_team_info_to_members(user_for_demotion.team_name)
                        self.send_character_info(demote_user)
                else: # demote user if offline
                    user_for_demotion = self.db_manager.get_character(demote_user)
                    if user_boss.team_name == user_for_demotion.team_name and user_for_demotion.rank_in_team > user_boss.rank_in_team and user_for_demotion.rank_in_team != 5:
                        self.db_manager.change_character_field(demote_user, "rank_in_team", user_for_demotion.rank_in_team + 1)
                        self.send_team_info_to_members(user_for_demotion.team_name)

    def remove_user_from_team(self, user_name, remove_user_name):
        if user_name != remove_user_name:
            user_boss = self.online_users[user_name].character
            if user_boss.rank_in_team < 2:
                if remove_user_name in self.online_users.keys(): # demote user is online
                    user_for_removing = self.online_users[remove_user_name].character
                    if user_boss.team_name == user_for_removing.team_name and user_for_removing.rank_in_team > user_boss.rank_in_team :
                        self.db_manager.change_user_team_update(remove_user_name, None, 0)
                        self.send_team_info_to_members(user_boss.team_name)
                        self.send_character_info(remove_user_name)
                        self.send_can_create_team(remove_user_name)
                else: # demote user if offline
                    user_for_removing = self.db_manager.get_character(remove_user_name)
                    if user_boss.team_name == user_for_removing.team_name and user_for_removing.rank_in_team > user_boss.rank_in_team :
                        self.db_manager.change_user_team(remove_user_name, None, 0)
                        self.send_team_info_to_members(user_boss.team_name)

    def invite_user_to_team(self, user_name, invite_user_name):
        invite_response = {
            "error" : "False",
            "msg" : ""
        }
        user_boss = self.online_users[user_name].character
        if user_boss.team_name and user_boss.rank_in_team < 2:
            user_for_inviting = self.online_users[invite_user_name].character
            if not user_for_inviting.team_name:
                self.send_invite(invite_user_name, user_name, user_boss.team_name)
                invite_response["msg"] = self.online_users[user_name].locale.translate(smarty.error_messages[4])
            else:
                invite_response["error"] = "True"
                invite_response["msg"] = self.online_users[user_name].locale.translate(smarty.error_messages[3]) % {"user_name" : invite_user_name}
        else:
            invite_response["error"] = "True"
            invite_response["msg"] = self.online_users[user_name].locale.translate(smarty.error_messages[5])

        return invite_response

    def user_join_team(self, joined_user, invited_user, team_name):
        user_boss = self.online_users[invited_user].character
        if user_boss.rank_in_team < 2:
            user_for_join = self.online_users[joined_user].character
            if not user_for_join.team_name:
                self.db_manager.change_user_team_update(joined_user, team_name, 5)
                self.send_team_info_to_members(team_name)
                self.send_character_info(joined_user)

    def user_leave_team(self, user_name):
        user = self.online_users[user_name].character
        # if user is leader
        if user.rank_in_team == 0:
            members = self.get_team_members(user.team_name)
            self.db_manager.remove_team(user.team_name)# remove team
            # send info to online members
            for member_name in members.keys():
                if member_name in self.online_users.keys():
                    self.send_character_info(member_name)
                    self.send_can_create_team(member_name)
        else:
            self.db_manager.change_user_team_update(user_name, None, 0)
            self.send_character_info(user_name)
            self.send_can_create_team(user_name)
            self.send_team_info_to_members(user.team_name)

    def put_on_item(self, user_name, item_id):
        result = False
        int_id = int(item_id)
        # get type of thing, e.g. right_hand, left_hand, head, etc.
        item_type = items_manager.get_item_type(int_id)
        character = self.online_users[user_name].character
        bag_items = character.bag.split(",")
        # check if character has thing and can put it on
        if item_id in bag_items and items_manager.check_item(character, int_id):
            thing_pos = bag_items.index(item_id)
            # remember old bonuses of old item if it was worn
            old_bonuses = {}
            if character[item_type]: # something was wearing - exchange it with item from bag
                old_bonuses = items_manager.get_bonuses(int(character[item_type]))
                character[item_type], bag_items[thing_pos] = bag_items[thing_pos], character[item_type]
            else: # nothing was wearing, remove item from bag
                character[item_type] = bag_items[thing_pos]
                bag_items.pop(thing_pos)
            self.db_manager.change_character_field_update(user_name, "bag", ",".join(bag_items))
            self.db_manager.change_character_field_update(user_name, item_type, character[item_type])
            self.send_character_stuff(user_name)

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
            self.db_manager.change_character_fields_update(user_name, bonuses)
            self.send_character_info(user_name)
            result = True

        return result

    def take_off_item(self, user_name, item_id):
        int_id = int(item_id)
        # get type of thing, e.g. right_hand, left_hand, head, etc.
        item_type = items_manager.get_item_type(int_id)
        character = self.online_users[user_name].character
        # check if character has thing and worn it
        if item_id == character[item_type]:
            # remember old bonuses of old item if it was worn
            bonuses = items_manager.get_bonuses(int_id)
            # add old bonuses not in new ones
            for bonus_name in bonuses.keys():
                bonuses[bonus_name] = character[bonus_name] - bonuses[bonus_name]
            self.db_manager.change_character_fields_update(user_name, bonuses)
            self.send_character_info(user_name)

            if character.bag: # something is in the bag
                self.db_manager.change_character_field_update(user_name, "bag", ",".join([character.bag, item_id]))
            else: # nothing is in the bag
                self.db_manager.change_character_field_update(user_name, "bag", item_id)
            self.db_manager.change_character_field_update(user_name, item_type, "")
            self.send_character_stuff(user_name)


    def buy_item(self, user_name, item_id):
        character = self.online_users[user_name].character
        item = items_manager.items[int(item_id)]
        if character.gold >= item.price: # if character can buy it
            update_fields = dict()
            update_fields["gold"] = character.gold - item.price
            if not character.bag:
                update_fields["bag"] = item_id
            else:
                update_fields["bag"] = ",".join([character.bag, item_id])
            self.db_manager.change_character_fields_update(user_name, update_fields)
            self.send_character_info(user_name)
            self.send_character_stuff(user_name)

    def learn_spell(self, user_name, spell_id):
        character = self.online_users[user_name].character
        spell = spells_manager.spells[int(spell_id)]
        if character.gold >= spell.price: # if character can buy it
            update_fields = dict()
            update_fields["gold"] = character.gold - spell.price
            if character.spells:
                update_fields["spells"] = ",".join([character.spells, spell_id])
            else:
                update_fields["spells"] = spell_id
            self.db_manager.change_character_fields_update(user_name, update_fields)
            self.send_character_spells(user_name)
            self.send_character_info(user_name)

    def user_enter(self, user_name):
        self.send_character_info(user_name)
        self.send_character_stuff(user_name)
        self.send_character_spells(user_name)
        character = self.online_users[user_name].character
        if character.team_name:
            # character is in team
            self.send_team_info_to_user(user_name)
        else:
            # character is not in team
            self.send_can_create_team(user_name)

    def send_can_create_team(self, user_name):
        self.online_users[user_name].send_action(self.can_create_team_action())

    def send_character_info(self, user_name):
        self.online_users[user_name].send_action(self.character_info_action(user_name))

    def send_character_stuff(self, user_name):
        self.online_users[user_name].send_action(self.character_stuff_action(user_name))

    def send_character_spells(self, user_name):
        self.online_users[user_name].send_action(self.character_spells_action(user_name))

    def send_team_info_to_user(self, user_name):
        team_name = self.online_users[user_name].character.team_name
        self.online_users[user_name].send_action(self.team_info_action(self.db_manager.get_team_info(team_name)))

    def send_team_info_to_members(self, team_name):
        team_members = self.get_team_members(team_name)
        for member_name in team_members.keys():
            if member_name in self.online_users.keys():
                self.online_users[member_name].send_action(self.team_info_action(self.db_manager.get_team_info(team_name)))

    def send_invite(self, invite_user_name, user_name, team_name):
        self.online_users[invite_user_name].send_action(self.invite_action(user_name, team_name))

    def change_gold_tax(self, user_name, strategy_id_str):
        team_name = self.online_users[user_name].character.team_name
        self.db_manager.change_team_field(team_name, "gold_tax", int(strategy_id_str))
        self.send_team_info_to_members(team_name)

    def change_gold_sharing(self, user_name, strategy_id_str):
        team_name = self.online_users[user_name].character.team_name
        self.db_manager.change_team_field(team_name, "gold_sharing", int(strategy_id_str))
        self.send_team_info_to_members(team_name)

    def change_experience_sharing(self, user_name, strategy_id_str):
        team_name = self.online_users[user_name].character.team_name
        self.db_manager.change_team_field(team_name, "experience_sharing", int(strategy_id_str))
        self.send_team_info_to_members(team_name)
