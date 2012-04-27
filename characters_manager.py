__author__ = 'Pavel Padinker'

class CharactersManager:
    def __init__(self, db):
        self.db = db
        self.db.execute("create table if not exists characters (id integer(11) primary key not null auto_increment unique, "
                        "name text, char_class integer, level integer, hp integer, mp integer, strength integer, dexterity  integer, "
                        "intellect  integer, wisdom  integer)")
        self.classes = {
            0 : 'Warrior',
            1 : 'Guardian',
            2 : 'Archer',
            3 : 'Rogue',
            4 : 'Mage',
            5 : 'Priest',
            6 : 'Warlock',
            7 : 'Necromancer',
            }


    def get(self, name):
            return self.db.get("select * from characters where name = %s", name)

    def create(self, name, classID):
        self.db.execute("insert into characters (name, char_class, level, hp, mp, strength, dexterity, intellect, wisdom) values "
                        "(%s, %s, %s, %s, %s, %s, %s, %s, %s)", name, classID, 1, 1, 1, 1, 1, 1, 1)

    def remove(self, name):
        self.db.execute("delete from characters where name = %s", name)

    def get_classes(self):
        return self.classes

    def get_info(self, name):
    # return character info
        character = self.get(name)
        character_info = {
            'name' : character.name,
            'char_class' : character.char_class,
            'level' : character.level,
            'hp' : character.hp,
            'mp' : character.mp,
            'strength' : character.strength,
            'dexterity' : character.dexterity,
            'intellect' : character.intellect,
            'wisdom' : character.wisdom
        }

        character_info['char_class'] = {
            0 : 'Warrior',
            1 : 'Guardian',
            2 : 'Archer',
            3 : 'Rogue',
            4 : 'Mage',
            5 : 'Priest',
            6 : 'Warlock',
            7 : 'Necromancer',
            }[character_info['char_class']]

        return character_info

def main():
    pass

if __name__ == "__main__":
    main()