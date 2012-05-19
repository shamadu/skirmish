__author__ = 'PavelP'

class DBManager():
    def __init__(self, db):
        self.db = db
        self.db.execute('create table if not exists characters '
                        '(id integer(11) primary key not null auto_increment unique, '
                        'name text, '
                        'classID integer, '
                        'level integer default 1, '
                        'strength integer default 1, '
                        'dexterity  integer default 1, '
                        'intellect  integer default 1, '
                        'wisdom  integer default 1, '
                        'exp bigint default 1, '
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
                        'left_foot text, '
                        'right_foot text, '
                        'cloak text)')
        self.db.execute("create table if not exists users "
                        "(id integer(11) primary key not null auto_increment unique, "
                        "login text, "
                        "password text)")
        self.db.execute("create table if not exists weapons "
                        "(id integer(11) primary key not null auto_increment unique, "
                        "name text, "
                        "min_dmg float, "
                        "max_dmg float, "
        # required_stats are comma-separated stats in order: strength,dexterity,intellect,wisdom,level
                        "required_stats text not null, "
        # bonus_stats are comma-separated stats in order: strength,dexterity,intellect,wisdom,min_dmg,max_dmg,spell_dmg
                        "bonus_stats text not null, "
                        "price integer, "
                        "description text)")
        self.db.execute("create table if not exists clothes "
                        "(id integer(11) primary key not null auto_increment unique, "
                        "name text, "
                        "required_stats text not null, "
                        "bonus_stats text not null, "
                        "price integer, "
                        "description text)")

    def get_user(self, login):
        return self.db.get("select * from users where login = %s", login)

    def add_user(self, login, password):
        self.db.execute("insert into users (login, password) values (%s, %s)", login, password)

    def get_character(self, name):
        return self.db.get("select * from characters where name = %s", name)

    def create_character(self, name, classID):
        if not self.get_character(name):
            self.db.execute("insert into characters (name, classID, weapon) values (%s, %s, %s)", name, classID, "0")

    def remove_character(self, name):
        self.db.execute("delete from characters where name = %s", name)

    def create_team(self, user_name, team_name):
        self.db.execute("update characters set team_name=%s, rank_in_team=0 where name=%s", team_name, user_name)

    def get_team_members(self, team_name):
        return self.db.query("select * from characters where team_name = %s", team_name)

    def change_team_rank(self, user_name, new_rank):
        self.db.execute("update characters set rank_in_team=%s where name=%s", new_rank, user_name)

    def change_user_team(self, user_name, team_name, team_rank):
        self.db.execute("update characters set team_name=%s, rank_in_team=%s where name=%s", team_name, team_rank, user_name)
