# -*- coding: utf-8 -*-

from collections import OrderedDict
import random
import items_manager

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
        1 : [_("Berserk Fury"), _("Disarmament")]
    },
    # guardian
    1 : {
        1 : [_("Armor"), _("Shield Block")]
    },
    # archer
    2 : {
        1 : [_("Evasion"), _("Berserk Fury")]
    },
    # rogue
    3 : {
        1 : [_("Evasion"), _("Trip")]
    },
    # mage
    4 : {
        1 : [_("Frost Needle"), _("Fire Spark")]
    },
    # priest
    5 : {
        1 : [_("Prayer for Attack"), _("Prayer for Protection")]
    },
    # warlock
    6 : {
        1 : [_("Curse of Weakness"), _("Leech Life")]
    },
    # necromancer
    7 : {
        1 : [_("Infection"), _("Stench")]
    }
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

def get_spells(character, locale):
    result = list()
    for enough_level in range(character.level):
        level_spells = spells[character.classID][enough_level + 1]
        for i in range(len(level_spells)):
            result.append(locale.translate(level_spells[i]))

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
        return character.wisdom*1.7

def get_hp_count(character):
    return character.level + character.strength

# return default parameters : str, dex, int, wis, con
def get_default_parameters(classID):
    parameters = []
    if classID == 0: # Warrior
        parameters = [8, 4, 3, 3, 5]
    elif classID == 1: # Guardian
        parameters = [5, 3, 3, 3, 8]
    elif classID == 2: # Archer
        parameters = [5, 7, 3, 3, 5]
    elif classID == 3: # Rogue
        parameters = [6, 6, 3, 3, 5]
    elif classID == 4: # Mage
        parameters = [3, 3, 8, 5, 4]
    elif classID == 5: # Priest
        parameters = [3, 3, 5, 8, 4]
    elif classID == 6: # Warlock
        parameters = [3, 3, 7, 6, 4]
    elif classID == 7: # Necromancer
        parameters = [3, 3, 6, 7, 4]
    return parameters

def get_regeneration(character):
    if character.classID < 4:
        return 0.4*character.dexterity + 0.3*character.strength
    else:
        return 0.4*character.wisdom + 0.3*character.intellect

def get_attack(character):
    return character.strength*0.4 + character.dexterity*0.6

def get_defence(character):
    return character.strength*0.4 + character.constitution*0.6

def get_magic_attack(character):
    return character.wisdom*0.4 + character.intellect*0.6

def get_magic_defence(character):
    return character.wisdom*0.6 + character.intellect*0.4

def get_armor(character):
    return character.dexterity*3 + character.strength*6

def get_spell_length(character):
    return character.intellect/3

def get_damage(character_to_attack, character_to_defence):
    min_damage = items_manager.items[character_to_attack.current_weapon_id][7]
    max_damage = items_manager.items[character_to_attack.current_weapon_id][8]
    weapon_damage = random.uniform(min_damage, max_damage)
    damage = max(0.90 + (character_to_attack.strength / 100), 1) ** 2 * weapon_damage
    absorb = max(character_to_defence.armor * 0.01)
    return damage*absorb

def is_hit(character_to_attack, attack_percent, character_to_defence, defence_percent):
    if (attack_percent*character_to_attack.attack)/(defence_percent*character_to_defence.defence) > 1.5: # definitely not hit
        return True
    elif random.random() < 2 - (attack_percent*character_to_attack.attack)/(defence_percent*character_to_defence.defence):
        return True
    return False

def is_critical_damage(character_to_attack, character_to_defence):
    return random.random() < character_to_attack.dexterity/1000

def get_experience_for_damage(damage):
    return damage * 10

def get_experience_for_spell_damage(damage):
    return damage * 15

def get_experience_for_defence(damage):
    return damage * 10
