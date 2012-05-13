from collections import deque
import smarty

__author__ = 'Pavel Padinker'

class Action:
    def __init__(self, type, args):
        # types are:
        # 0 - character info update
        # 1 - fill team div with content for creation
        # 2 - fill team div with content with team info
        self.type = type
        self.args = args
        self.args["type"] = type

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
    def __init__(self, db):
        self.db = db
        self.db.execute("create table if not exists characters (id integer(11) primary key not null auto_increment unique, "
                        "name text, classID integer, level integer, hp integer, mp integer, strength integer, dexterity  integer, "
                        "intellect  integer, wisdom  integer, exp bigint, gold integer, team_name text, rank_in_team text)")
        self.users = dict()

    def subscribe(self, user_name, callback, locale):
        if not user_name in self.users:
            self.users[user_name] = UserInfo(callback, locale)
        else:
            self.users[user_name].set_callback(callback)

    def unsubscribe(self, user_name):
        self.users[user_name].set_callback(None)

    def get_character(self, name):
        return self.db.get("select * from characters where name = %s", name)

    def create_character(self, name, classID):
        if not self.get_character(name):
            self.db.execute("insert into characters (name, classID, level, hp, mp, strength, dexterity, intellect, wisdom, exp, gold, team_name, rank_in_team) values "
                            "(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)", name, classID, 1, 1, 1, 1, 1, 1, 1, 0, 1, None, 0)

    def remove_character(self, name):
        self.db.execute("delete from characters where name = %s", name)

    def send_info(self, name):
        # return character info
        character = self.get_character(name)
        character_info = [
            character.name,
            smarty.get_class_name(self.users[name].locale, character.classID),
            str(character.level),
            str(character.hp),
            str(character.mp),
            str(character.strength),
            str(character.dexterity),
            str(character.intellect),
            str(character.wisdom),
            str(character.exp),
            str(character.gold),
            character.team_name,
            str(character.rank_in_team)
        ]
        self.users[name].send_action(Action(0, {"character_info" : ":".join(character_info)}))

    def user_enter(self, user_name, locale):
        if not user_name in self.users:
            self.users[user_name] = UserInfo(None, locale)
        self.send_info(user_name)
        character = self.get_character(user_name)
        if character.team_name:
            # character is in team
            self.send_team_info(user_name, character.team_name)
        else:
            # character is not in team
            self.send_create_team(user_name)

    def create_team(self, user_name, team_name):
        create_response = {
            "error" : "False",
            "msg" : ""
        }
        if not self.get_character(user_name).team_name:
            if len(self.get_team_members(team_name)) == 0:
                self.db.execute("update characters set team_name=%s, rank_in_team=0 where name=%s", team_name, user_name)
                self.send_team_info(user_name, team_name)
            else:
                create_response["error"] = True
                create_response["msg"] = self.users[user_name].locale.translate(smarty.error_messages[0])
        else:
            create_response["error"] = True
            create_response["msg"] = self.users[user_name].locale.translate(smarty.error_messages[1])

        return create_response

    def send_create_team(self, user_name):
        self.users[user_name].send_action(Action(1, {}))

    def send_team_info(self, user_name, team_name):
        self.users[user_name].send_action(Action(2, {
            "team_name" : team_name,
            # TODO: add team gold in special team table
            "team_gold" : 0,
            "members" : self.get_team_members(team_name)
        }))

    def get_team_members(self, team_name):
        result = dict()
        members = self.db.query("select * from characters where team_name = %s", team_name)
        for member in members:
            result[member.name] = member.rank_in_team

        return result

    def promote_user(self, user_name, promote_user):
        pass

    def demote_user(self, user_name, demote_user):
        pass

    def remove_user_from_team(self, user_name, remove_user_name):
        pass