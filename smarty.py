__author__ = 'Pavel Padinker'

classes = {
    0 : 'Warrior',
    1 : 'Guardian',
    2 : 'Archer',
    3 : 'Rogue',
    4 : 'Mage',
    5 : 'Priest',
    6 : 'Warlock',
    7 : 'Necromancer',
    }

spells = {
    # warrior
    0 : {
        1 : {"Berserk Fury", "Disarmament"}
    },
    # guardian
    1 : {
        1 : {"Armor", "Shield Block"}
    },
    # archer
    2 : {
        1 : {"Evasion", "Berserk Fury"}
    },
    # rogue
    3 : {
        1 : {"Evasion", "Trip"}
    },
    # mage
    4 : {
        1 : {"Frost Needle", "Fire Spark"}
    },
    # priest
    5 : {
        1 : {"Prayer for Attack", "Prayer for Protection"}
    },
    # warlock
    6 : {
        1 : {"Curse of Weakness", "Leech Life"}
    },
    # necromancer
    7 : {
        1 : {"Infection", "Stench"}
    }
    }

def get_classes():
    return classes

def get_class_name(classID):
    return classes[classID]

def get_attack_count(classID, level):
    attack_count = 1
    if 3 == classID:
        if level > 5:
            attack_count = 2
    elif 2 == classID:
        if level > 7:
            attack_count = 4
        elif level > 5:
            attack_count = 3
        elif level > 3:
            attack_count = 2

    return attack_count

def get_defence_count(classID, level):
    defence_count = 1
    if 0 == classID:
        if level > 7:
            defence_count = 3
        elif level > 5:
            defence_count = 2
    elif 1 == classID:
        if level > 7:
            defence_count = 4
        elif level > 5:
            defence_count = 3
        elif level > 3:
            defence_count = 2

    return defence_count

def get_spell_count(classID, level):
    spell_count = 1
    # TODO: add level condition - 4 or 5 or smth else
    if 5 == classID or 6 == classID:
        spell_count = 2

    return spell_count

def get_spells(classID, level):
    result = list()
    for enough_level in range(level):
        result += spells[classID][enough_level + 1]
    return result

def get_ability_name(classID):
    ability_name = ""
    if classID < 4:
        ability_name = "skill"
    else:
        ability_name = "spell"

    return ability_name

def get_substance_name(classID):
    substance_name = ""
    if classID < 4:
        substance_name = "energy"
    else:
        substance_name = "mana"

    return substance_name
