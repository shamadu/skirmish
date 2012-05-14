# -*- coding: utf-8 -*-

from collections import OrderedDict

__author__ = 'Pavel Padinker'

_ = lambda s: s

rest_time = 5
registration_time = 5
turn_time = 5

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

def get_locales(locale):
    result = OrderedDict()
    for locale_id in locales.keys():
        result[locale_id] = locale.translate(locales[locale_id])
    return result

def get_classes(locale):
    result = dict()
    for class_id in classes.keys():
        result[class_id] = locale.translate(classes[class_id])
    return result

def get_class_name(locale, classID):
    return get_classes(locale)[classID]

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
