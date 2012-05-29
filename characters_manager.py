import items_manager
import smarty
import spells_manager

__author__ = 'Pavel Padinker'

class CharactersManager:
    def __init__(self, db_manager, actions_manager):
        self.db_manager = db_manager
        self.actions_manager = actions_manager

    @property
    def online_users(self):
        return self.actions_manager.online_users

    def create_team(self, user_name, team_name):
        create_response = {
            "error" : "False",
            "msg" : ""
        }
        if not self.online_users[user_name].character.team_name:
            if len(self.get_team_members(team_name)) == 0:
                self.db_manager.create_team(user_name, team_name)
                self.actions_manager.send_team_info_to_user(user_name, self.get_team_members(team_name))
                self.actions_manager.send_character_info(user_name)
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
            result[member.name] = member.rank_in_team

        return result

    def promote_user(self, user_name, promote_user):
        if user_name != promote_user:
            user_boss = self.online_users[user_name].character
            if user_boss.rank_in_team < 2:
                user_for_promotion = self.online_users[promote_user].character
                if user_boss.team_name == user_for_promotion.team_name and user_for_promotion.rank_in_team > user_boss.rank_in_team:
                    self.db_manager.change_character_field_update(promote_user, "rank_in_team", user_for_promotion.rank_in_team - 1)
                    self.actions_manager.send_team_info_to_members(self.get_team_members(user_for_promotion.team_name))
                    self.actions_manager.send_character_info(promote_user)

    def demote_user(self, user_name, demote_user):
        if user_name != demote_user:
            user_boss = self.online_users[user_name].character
            if user_boss.rank_in_team < 2:
                user_for_demotion = self.online_users[demote_user].character
                if user_boss.team_name == user_for_demotion.team_name and user_for_demotion.rank_in_team > user_boss.rank_in_team and user_for_demotion.rank_in_team != 5:
                    self.db_manager.change_character_field_update(demote_user, "rank_in_team", user_for_demotion.rank_in_team + 1)
                    self.actions_manager.send_team_info_to_members(self.get_team_members(user_for_demotion.team_name))
                    self.actions_manager.send_character_info(demote_user)

    def remove_user_from_team(self, user_name, remove_user_name):
        if user_name != remove_user_name:
            user_boss = self.online_users[user_name].character
            if user_boss.rank_in_team < 2:
                user_for_removing = self.online_users[remove_user_name].character
                if user_boss.team_name == user_for_removing.team_name and user_for_removing.rank_in_team > user_boss.rank_in_team :
                    self.db_manager.change_user_team(remove_user_name, None, 0)
                    self.actions_manager.send_team_info_to_members(self.get_team_members(user_boss.team_name))
                    self.actions_manager.send_character_info(remove_user_name)
                    self.actions_manager.send_can_create_team(remove_user_name)

    def invite_user_to_team(self, user_name, invite_user_name):
        invite_response = {
            "error" : "False",
            "msg" : ""
        }
        user_boss = self.online_users[user_name].character
        if user_boss.rank_in_team < 2:
            user_for_inviting = self.online_users[invite_user_name].character
            if not user_for_inviting.team_name:
                self.actions_manager.send_invite(invite_user_name, user_name, user_boss.team_name)
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
                self.actions_manager.send_team_info_to_members(self.get_team_members(team_name))
                self.actions_manager.send_character_info(joined_user)

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
                    self.actions_manager.send_character_info(member_name)
                    self.actions_manager.send_can_create_team(member_name)
                return
        self.db_manager.change_user_team(user_name, None, 0)
        self.actions_manager.send_character_info(user_name)
        self.actions_manager.send_can_create_team(user_name)
        self.actions_manager.send_team_info_to_members(self.get_team_members(user.team_name))

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
            self.db_manager.change_character_field_update(user_name, item_type, ",".join(items))
            self.actions_manager.send_character_stuff(user_name)

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
            self.db_manager.change_character_fields_update(user_name, bonuses)
            self.actions_manager.send_character_info(user_name)
            result = True

        return result

    def buy_item(self, user_name, item_id):
        character = self.online_users[user_name].character
        item = items_manager.items[int(item_id)]
        if character.gold >= item.price: # if character can buy it
            update_fields = dict()
            update_fields["gold"] = character.gold - item.price
            item_type = items_manager.get_item_type(item.id)
            update_fields[item_type] = ",".join([character[item_type], item_id])
            self.db_manager.change_character_fields_update(user_name, update_fields)
            self.actions_manager.send_character_info(user_name)
            self.actions_manager.send_character_stuff(user_name)

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
            self.actions_manager.send_character_spells(user_name)
            self.actions_manager.send_character_info(user_name)

    def subscribe(self, user_name, callback):
        self.online_users[user_name].set_character_callback(callback)

    def unsubscribe(self, user_name):
        if user_name in self.online_users:
            self.online_users[user_name].set_character_callback(None)

    def user_enter(self, user_name):
        self.actions_manager.user_enter_characters_manager(user_name, self.get_team_members(self.online_users[user_name].character.team_name))
