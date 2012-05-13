from collections import deque
import smarty

__author__ = 'Pavel Padinker'

class Action:
    def __init__(self, type, args):
        # types are:
        # 0 - character info update
        # 1 -
        # 2 -
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
                            "(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)", name, classID, 1, 1, 1, 1, 1, 1, 1, 0, 1, "", 0)

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
            str(character.wisdom)
        ]
        self.users[name].send_action(Action(0, {"character_info" : ":".join(character_info)}))

    def user_enter(self, user_name, locale):
        if not user_name in self.users:
            self.users[user_name] = UserInfo(None, locale)
        self.send_info(user_name)

    def create_team(self, user_name, team_name):
        self.db.execute("update characters set team_name=%s, rank_in_team=0 where name=%s", team_name, user_name)