import items_manager
import smarty

__author__ = 'PavelP'

class DBManager():
    def __init__(self, db, actions_manager):
        self.db = db
        self.actions_manager = actions_manager
        self.db.execute('create table if not exists characters '
                        '(id integer(11) primary key not null auto_increment unique, '
                        'name text, '
                        'classID integer, '
                        'level integer default 1, '
                        'strength integer default 1, '
                        'dexterity integer default 1, '
                        'intellect integer default 1, '
                        'wisdom integer default 1, '
                        'constitution integer default 1, '
                        'experience bigint default 1, '
                        'gold integer default 1, '
                        'team_name text default null, '
                        'rank_in_team int default 0, '
        # weapon, shield and all clothes = comma-separated text, first is id of wearing thing, other - in backpack
                        'weapon text, '
                        'shield text, '
                        'head text, '
                        'body text, '
                        'left_hand text, '
                        'right_hand text, '
                        'legs text, '
                        'feet text, '
                        'cloak text, '
                        'spells text)')
        self.db.execute("create table if not exists users "
                        "(id integer(11) primary key not null auto_increment unique, "
                        "login text, "
                        "password text)")

    def update_character(self, user_name):
        character = self.get_character(user_name)
        character.current_weapon_id = int(character.weapon.split(",")[0])
        character.attack = smarty.get_attack(character)
        character.defence = smarty.get_defence(character)
        character.magic_attack = smarty.get_magic_attack(character)
        character.magic_defence = smarty.get_magic_defence(character)
        character.armor = smarty.get_armor(character)
        self.actions_manager.update_character(user_name, character)

    def get_user(self, login):
        return self.db.get("select * from users where login = %s", login)

    def add_user(self, login, password):
        self.db.execute("insert into users (login, password) values (%s, %s)", login, password)

    def get_character(self, name):
        return self.db.get("select * from characters where name = %s", name)

    def create_character(self, name, classID):
        if not self.get_character(name):
            default_parameters = smarty.get_default_parameters(int(classID))
            default_stuff = items_manager.get_default_stuff(int(classID))
            self.db.execute("insert into characters (name, classID, strength, dexterity, intellect, wisdom, constitution, "
                            "weapon, shield, head, body, left_hand, right_hand, legs, feet, cloak, spells) values "
                            "(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
                , name
                , classID
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
                , default_stuff[8]
                , None)

    def remove_character(self, name):
        self.db.execute("delete from characters where name = %s", name)

    def get_team_members(self, team_name):
        return self.db.query("select * from characters where team_name = %s", team_name)

    def create_team(self, user_name, team_name):
        self.db.execute("update characters set team_name=%s, rank_in_team=0 where name=%s", team_name, user_name)
        self.update_character(user_name)

    def change_user_team(self, user_name, team_name, team_rank):
        self.db.execute("update characters set team_name=%s, rank_in_team=%s where name=%s", team_name, team_rank, user_name)
        self.update_character(user_name)

    def change_character_field(self, user_name, field_name, field_value):
        self.db.execute("update characters set {0}=%s where name=%s".format(field_name), field_value, user_name)
        self.update_character(user_name)

    def change_character_fields(self, user_name, fields):
        if len(fields) > 0:
            fields_str = ", ".join("{0}='{1}'".format(key, str(fields[key])) for key in fields.keys())
            self.db.execute("update characters set {0} where name=%s".format(fields_str), user_name)
            self.update_character(user_name)
