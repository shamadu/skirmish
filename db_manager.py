import items_manager
import smarty

__author__ = 'PavelP'

class DBManager():
    def __init__(self, db, users_holder):
        self.db = db
        self.online_users = users_holder.online_users
        self.db.execute('create table if not exists characters '
                        '(id integer(11) primary key not null auto_increment unique, '
                        'name text, '
                        'race_id integer, '
                        'class_id integer, '
                        'level integer default 1, '
                        'strength integer default 1, '
                        'dexterity integer default 1, '
                        'intellect integer default 1, '
                        'wisdom integer default 1, '
                        'constitution integer default 1, '
                        'experience bigint default 1, '
                        'gold integer default 1, '
                        'team_name text default null, '
                        'rank_in_team integer default 0, '
        # right_hand, left_hand and all clothes = id of worn item
        # bag = comma-separated text, ids of items in backpack
                        'right_hand text, '
                        'left_hand text, '
                        'head text, '
                        'body text, '
                        'hands text, '
                        'legs text, '
                        'feet text, '
                        'cloak text, '
                        'bag text, '
                        'spells text)')
        self.db.execute("create table if not exists users "
                        "(id integer(11) primary key not null auto_increment unique, "
                        "login text, "
                        "password text,"
                        "location integer default 0)")

        self.db.execute("create table if not exists teams "
                        "(id integer(11) primary key not null auto_increment unique, "
                        "team_name text default null, "
                        'gold_tax integer default 0, '
                        'gold_sharing integer default 0, '
                        "experience_sharing integer default 0)")

    def update_character(self, user_name):
        character = self.get_character(user_name)
        character.health = smarty.get_hp_count(character)
        character.mana = smarty.get_mp_count(character)
        character.attack = smarty.get_attack(character)
        character.defence = smarty.get_defence(character)
        character.magic_attack = smarty.get_magic_attack(character)
        character.magic_defence = smarty.get_magic_defence(character)
        character.armor = smarty.get_armor(character)
        self.online_users[user_name].character = character

    def get_user(self, login):
        return self.db.get("select * from users where login = %s", login)

    def add_user(self, login, password):
        self.db.execute("insert into users (login, password) values (%s, %s)", login, password)

    def update_user_location(self, login, location):
        self.online_users[login].location = location
        self.db.execute("update users set location=%s where login = %s", location, login)

    def get_character(self, name):
        character = self.db.get("select * from characters where name = %s", name)
        if character.team_name:
            character.team_info = self.db.get("select * from teams where team_name = %s", character.team_name)
        return character

    def create_character(self, name, race_id, class_id):
        if not self.get_character(name):
            default_parameters = smarty.get_default_parameters(int(race_id), int(class_id))
            default_stuff = items_manager.get_default_stuff(int(class_id))
            self.db.execute("insert into characters (name, race_id, class_id, strength, dexterity, intellect, wisdom, constitution, "
                            "right_hand, left_hand, head, body, hands, legs, feet, cloak, bag, spells) values "
                            "(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
                , name
                , race_id
                , class_id
                , str(default_parameters[0])
                , str(default_parameters[1])
                , str(default_parameters[2])
                , str(default_parameters[3])
                , str(default_parameters[4])
                , default_stuff[0]
                , default_stuff[1]
                , default_stuff[2]
                , default_stuff[3]
                , default_stuff[4]
                , default_stuff[5]
                , default_stuff[6]
                , default_stuff[7]
                , ""
                , None)

    def remove_character(self, name):
        self.db.execute("delete from characters where name = %s", name)

    def get_team_members(self, team_name):
        return self.db.query("select * from characters where team_name = %s", team_name)

    def create_team(self, user_name, team_name):
        self.db.execute("insert into teams (team_name) values (%s)", team_name)
        self.db.execute("update characters set team_name=%s, rank_in_team=0 where name=%s", team_name, user_name)
        self.update_character(user_name)

    def remove_team(self, team_name):
        self.db.execute("delete from teams where team_name = %s", team_name)
        members = self.get_team_members(team_name)
        # remove team
        for member in members:
            self.change_user_team(member.name, None, 0)

    def change_user_team(self, user_name, team_name, team_rank):
        self.db.execute("update characters set team_name=%s, rank_in_team=%s where name=%s", team_name, team_rank, user_name)

    def change_user_team_update(self, user_name, team_name, team_rank):
        self.db.execute("update characters set team_name=%s, rank_in_team=%s where name=%s", team_name, team_rank, user_name)
        self.update_character(user_name)

    def change_character_field(self, user_name, field_name, field_value):
        self.db.execute("update characters set {0}=%s where name=%s".format(field_name), field_value, user_name)

    def change_character_field_update(self, user_name, field_name, field_value):
        self.change_character_field(user_name, field_name, field_value)
        self.update_character(user_name)

    def change_character_fields(self, user_name, fields):
        if len(fields) > 0:
            fields_str = ", ".join("{0}='{1}'".format(key, str(fields[key])) for key in fields.keys())
            self.db.execute("update characters set {0} where name=%s".format(fields_str), user_name)

    def change_character_fields_update(self, user_name, fields):
        if len(fields) > 0:
            self.change_character_fields(user_name, fields)
            self.update_character(user_name)

