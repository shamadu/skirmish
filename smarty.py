# -*- coding: utf-8 -*-

from collections import OrderedDict

__author__ = 'Pavel Padinker'

_ = lambda s: s

rest_time = 1
registration_time = 5
turn_time = 25

team_ranks = {
    0 : "Leader",
    1 : "Officer",
    2 : "Helper",
    3 : "",
    4 : "",
    5 : ""
}

error_messages = {
    0 : _("Team with this name already exists"),
    1 : _("Character already has team"),
    2 : _("Can't log in, wrong login or password"),
    3 : _("You can't invite %(user_name)s. This user already has a team"),
    4 : _("Invitation has been sent")
}

locales = OrderedDict([
    ("en_US", "English"),
    ("ru", u"Русский")
])

classes = {
    0 : _('Warrior'),
    1 : _('Guardian'),
    2 : _('Archer'),
    3 : _('Rogue'),
    4 : _('Mage'),
    5 : _('Priest'),
    6 : _('Warlock'),
    7 : _('Necromancer'),
    }

ability_names = [
    _("Skill"),
    _("Spell")
]


substance_names = [
    _("Energy"),
    _("Mana")
]

main_abilities = [
    _("Attack"),
    _("Defence")
]

spells = {
    # warrior
    0 : {
        1 : {_("Berserk Fury"), _("Disarmament")}
    },
    # guardian
    1 : {
        1 : {_("Armor"), _("Shield Block")}
    },
    # archer
    2 : {
        1 : {_("Evasion"), _("Berserk Fury")}
    },
    # rogue
    3 : {
        1 : {_("Evasion"), _("Trip")}
    },
    # mage
    4 : {
        1 : {_("Frost Needle"), _("Fire Spark")}
    },
    # priest
    5 : {
        1 : {_("Prayer for Attack"), _("Prayer for Protection")}
    },
    # warlock
    6 : {
        1 : {_("Curse of Weakness"), _("Leech Life")}
    },
    # necromancer
    7 : {
        1 : {_("Infection"), _("Stench")}
    }
    }

# means that 0-99 are weapons, 100 - no shield, 101-199 are shields, 200 - empty head, 201-299 are helmets, etc.
build_id = lambda type, id: 100*type + id

things = {
    #   id : [id, name, required_stats, bonus_stats, price, description, min_damage, max_damage, ]
    # required_stats is a list of stats in order:
    # 0 - level,
    # 1 - strength,
    # 2 - dexterity,
    # 3 - intellect,
    # 4 - wisdom
    # bonus_stats is a list of stats in order:
    # 0 - strength,
    # 1 - dexterity,
    # 2 - intellect,
    # 3 - wisdom,
    # 4 - min_dmg,
    # 5 - max_dmg,
    # 6 - spell_dmg
    #weapons
    build_id(0, 0) : [build_id(0, 0), _("Knife"), [0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0], 0, _("Knife is basic weapon, everybody has it"), 0.2, 0.3],
    build_id(0, 1) : [build_id(0, 1), _("Stone"), [1, 0, 0, 0, 0], [1, 1, 0, 0, 0, 0, 0], 15, _("Sharpened stone is the weapon of real barbarian"), 0.4, 0.5],
    #   id : [id, name, required_stats, bonus_stats, price, description]
    # required_stats are comma-separated stats in order: strength,dexterity,intellect,wisdom,level
    # bonus_stats are comma-separated stats in order: strength,dexterity,intellect,wisdom,min_dmg,max_dmg,spell_dmg
    #shields
    build_id(1, 0) : [build_id(1, 0), _("Nothing"), [0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0], 0, _("You don't wear anything")],
    build_id(1, 1) : [build_id(1, 1), _("Basic shield"), [2, 0, 0, 0, 0], [1, 0, 0, 0, 0, 0, 0], 15, _("Just wooden shield with iron circle in center")],
    #heads
    build_id(2, 0) : [build_id(2, 0), _("Nothing"), [0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0], 0, _("You don't wear anything")],
    build_id(2, 1) : [build_id(2, 1), _("Basic helmet"), [2,0, 0, 0, 0], [0, 1, 0, 0, 0, 0, 0], 15, _("Wooden helmet is a better guard than your skull")],
    # body
    build_id(3, 0) : [build_id(3, 0), _("Nothing"), [0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0], 0, _("You don't wear anything")],
    # left_hand
    build_id(4, 0) : [build_id(4, 0), _("Nothing"), [0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0], 0, _("You don't wear anything")],
    # right_hand
    build_id(5, 0) : [build_id(5, 0), _("Nothing"), [0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0], 0, _("You don't wear anything")],
    # legs
    build_id(6, 0) : [build_id(6, 0), _("Nothing"), [0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0], 0, _("You don't wear anything")],
    # left_foot
    build_id(7, 0) : [build_id(7, 0), _("Nothing"), [0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0], 0, _("You don't wear anything")],
    # right_foot
    build_id(8, 0) : [build_id(8, 0), _("Nothing"), [0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0], 0, _("You don't wear anything")],
    # cloak
    build_id(9, 0) : [build_id(9, 0), _("Nothing"), [0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0], 0, _("You don't wear anything")]
    }

def get_classes(locale):
    result = dict()
    for class_id in classes.keys():
        result[class_id] = locale.translate(classes[class_id])
    return result

def get_class_name(classID, locale):
    return locale.translate(classes[classID])

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

def get_ability_name(classID, locale):
    ability_name = ""
    if classID < 4:
        ability_name = locale.translate(ability_names[0])
    else:
        ability_name = locale.translate(ability_names[1])

    return ability_name

def get_substance_name(classID, locale):
    substance_name = ""
    if classID < 4:
        substance_name = locale.translate(substance_names[0])
    else:
        substance_name = locale.translate(substance_names[1])

    return substance_name

def get_mp_count(character):
    if character.classID < 4:
        return character.dexterity*3
    else:
        return character.wisdom*3

def get_hp_count(character):
    return character.level + character.strength

def get_thing(id, locale):
    thing = things[id]
    thing[1] = locale.translate(things[id][1])
    thing[5] = locale.translate(things[id][5])
    return thing

def get_things(thing_ids_str, locale):
    things = list()
    thing_ids = thing_ids_str.split(",")
    for thing_id in thing_ids:
        things.append(get_thing(int(thing_id), locale))

    return things

def get_thing_type(id):
    thing_type = "undefined"
    if id < build_id(1, 0):
        thing_type = "weapon"
    elif id < build_id(2, 0):
        thing_type = "shield"
    elif id < build_id(3, 0):
        thing_type = "head"
    elif id < build_id(4, 0):
        thing_type = "body"
    elif id < build_id(5, 0):
        thing_type = "left_hand"
    elif id < build_id(6, 0):
        thing_type = "right_hand"
    elif id < build_id(7, 0):
        thing_type = "legs"
    elif id < build_id(8, 0):
        thing_type = "left_foot"
    elif id < build_id(9, 0):
        thing_type = "right_foot"
    elif id < build_id(10, 0):
        thing_type = "cloak"

    return thing_type

# 0 - level,
# 1 - strength,
# 2 - dexterity,
# 3 - intellect,
# 4 - wisdom
def check_thing(character, thing_id):
    result = False
    thing = things[thing_id]
    if (character.level >= thing[2][0]
        and character.strength >= thing[2][1]
        and character.dexterity>= thing[2][2]
        and character.intellect >= thing[2][3]
        and character.wisdom >= thing[2][4]):
        result = True
    return result

# 0 - strength,
# 1 - dexterity,
# 2 - intellect,
# 3 - wisdom,
# 4 - min_dmg,
# 5 - max_dmg,
# 6 - spell_dmg
def get_bonuses(thing_id):
    thing = things[thing_id]
    result = {}
    if thing[3][0] != 0:
        result["strength"] = thing[3][0]
    if thing[3][1] != 0:
        result["dexterity"] = thing[3][1]
    if thing[3][2] != 0:
        result["intellect"] = thing[3][2]
    if thing[3][3] != 0:
        result["wisdom"] = thing[3][3]
    if thing[3][4] != 0:
        result["min_dmg"] = thing[3][4]
    if thing[3][5] != 0:
        result["max_dmg"] = thing[3][5]
    if thing[3][6] != 0:
        result["spell_dmg"] = thing[3][6]

    return result