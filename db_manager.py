__author__ = 'PavelP'

class DBManager():
    def __init__(self, db):
        self.db = db
        self.db.execute("create table if not exists characters (id integer(11) primary key not null auto_increment unique, "
                        "name text, classID integer, level integer, hp integer, mp integer, strength integer, dexterity  integer, "
                        "intellect  integer, wisdom  integer, exp bigint, gold integer, team_name text, rank_in_team int)")
        self.db.execute("create table if not exists users (id integer(11) primary key not null auto_increment unique, "
                        "login text, password text)")

    def get_user(self, login):
        return self.db.get("select * from users where login = %s", login)

    def add_user(self, login, password):
        self.db.execute("insert into users (login, password) values (%s, %s)", login, password)

    def get_character(self, name):
        return self.db.get("select * from characters where name = %s", name)

    def create_character(self, name, classID):
        if not self.get_character(name):
            self.db.execute("insert into characters (name, classID, level, hp, mp, strength, dexterity, intellect, wisdom, exp, gold, team_name, rank_in_team) values "
                            "(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)", name, classID, 1, 1, 1, 1, 1, 1, 1, 0, 1, None, 0)

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
