# -*- coding: utf-8 -*-

from collections import OrderedDict
import random
import items_manager

__author__ = 'Pavel Padinker'

_ = lambda s: s

rest_time = 1
registration_time = 5
turn_time = 25

locations = {
    0 : _("Training Camp"),
    1 : _("Underworld"),
    2 : _("Airii Forest"),
    3 : _("Corutarr"),
}

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

battle_messages = {
    0 : _("Registration has been started"),
    1 : _("Registration has been ended"),
    2 : _("Round {0} has been started"),
    3 : _("Round {0} has been ended"),
    4 : _("Game has been ended"),
    5 : _("Game can't be started, not enough players"),
    6 : _("{0} attacked {1} with {2} and damaged him for {3}hp({4}hp) [{5}/{6}]"),
    7 : _("{0} tried to attack {1} with {2}, but couldn't break protection({3})"),
    8 : _("{0} makes critical hit!"),
    9 : _("{0} is dead"),
    10 : _("{0} ran from skirmish"),
    11 : _("Team {0} win"),
    12 : _("{0} win"),
    13 : _("Nobody win"),
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

races = {
    0 : _("Human"),
    1 : _("Orc"),
    2 : _("Elf"),
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

level_up_experiences = {
    1 : 1000,
    2 : 2000,
    3 : 4000,
    4 : 8000,
    5 : 16000,
    6 : 32000,
    7 : 64000,
    8 : 128000,
    9 : 256000,
    10 : 512000,
    11 : 1024000,
    12 : 2048000,
    13 : 4096000,
    14 : 8192000,
    15 : 16384000,
}

def get_locations(locale):
    result = dict()
    for location_id in locations.keys():
        result[location_id] = locale.translate(locations[location_id])
    return result

def get_classes(locale):
    result = dict()
    for class_id in classes.keys():
        result[class_id] = locale.translate(classes[class_id])
    return result

def get_races(locale):
    result = dict()
    for race_id in races.keys():
        result[race_id] = locale.translate(races[race_id])
    return result

def get_class_name(class_id, locale):
    return locale.translate(classes[class_id])

def get_race_name(race_id, locale):
    return locale.translate(races[race_id])

def get_attack_count(class_id, level):
    attack_count = 1
    if 3 == class_id:
        if level > 5:
            attack_count = 2
    elif 2 == class_id:
        if level > 7:
            attack_count = 4
        elif level > 5:
            attack_count = 3
        elif level > 3:
            attack_count = 2

    return attack_count

def get_defence_count(class_id, level):
    defence_count = 1
    if 0 == class_id:
        if level > 7:
            defence_count = 3
        elif level > 5:
            defence_count = 2
    elif 1 == class_id:
        if level > 7:
            defence_count = 4
        elif level > 5:
            defence_count = 3
        elif level > 3:
            defence_count = 2

    return defence_count

def get_spell_count(class_id, level):
    spell_count = 1
    # TODO: add level condition - 4 or 5 or smth else
    if 5 == class_id or 6 == class_id:
        spell_count = 2

    return spell_count

def get_ability_name(class_id, locale):
    ability_name = ""
    if class_id < 4:
        ability_name = locale.translate(ability_names[0])
    else:
        ability_name = locale.translate(ability_names[1])

    return ability_name

def get_substance_name(class_id, locale):
    substance_name = ""
    if class_id < 4:
        substance_name = locale.translate(substance_names[0])
    else:
        substance_name = locale.translate(substance_names[1])

    return substance_name

def get_mp_count(character):
    if character.class_id < 4:
        return character.dexterity*3
    else:
        return character.wisdom*1.7

def get_hp_count(character):
    return character.level + character.strength + character.constitution

# return default parameters : str, dex, int, wis, con
def get_default_parameters(race_id, class_id):
    parameters = []
    if class_id == 0: # Warrior
        parameters = [8, 4, 3, 3, 5]
    elif class_id == 1: # Guardian
        parameters = [5, 3, 3, 3, 8]
    elif class_id == 2: # Archer
        parameters = [5, 7, 3, 3, 5]
    elif class_id == 3: # Rogue
        parameters = [6, 6, 3, 3, 5]
    elif class_id == 4: # Mage
        parameters = [3, 3, 8, 5, 4]
    elif class_id == 5: # Priest
        parameters = [3, 3, 5, 8, 4]
    elif class_id == 6: # Warlock
        parameters = [3, 3, 7, 6, 4]
    elif class_id == 7: # Necromancer
        parameters = [3, 3, 6, 7, 4]

    if race_id == 0: # human
        parameters[2] += 1
        parameters[3] += 1
    elif race_id == 1: # orc
        parameters[0] += 2
    elif race_id == 2: # elf
        parameters[1] += 2
    return parameters

def get_regeneration(character):
    if character.class_id < 4:
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

def get_spell_duration(character):
    return character.intellect/3

def get_damage(character_to_attack, attack_percent, character_to_defence):
    min_damage = items_manager.items[character_to_attack.current_weapon_id].min_damage
    max_damage = items_manager.items[character_to_attack.current_weapon_id].max_damage
    weapon_damage = random.uniform(min_damage, max_damage)
    damage = max(0.90 + (character_to_attack.strength / 100), 1) ** 2 * weapon_damage
    absorb = character_to_defence.armor * 0.001
    return round((damage*attack_percent) - damage*absorb, 2)

def is_hit(character_to_attack, attack_percent, defenders):
    defence = 0.001 # attack 1 on 1% should hit player without defence at all
    for defender in defenders:
        defence += defender[0].defence*defender[1]
    if random.uniform(0.8, 1.3) < (attack_percent*character_to_attack.attack)/defence:
        return True
    return False

def is_critical_hit(character_to_attack, character_to_defence):
    return random.random() < character_to_attack.dexterity/1000

def is_critical_magic_hit(character_to_attack, character_to_defence):
    return random.random() < character_to_attack.intellect/1000

def get_experience_for_damage(damage):
    return round(damage * 10)

def get_experience_for_spell_damage(damage):
    return round(damage * 15)

def get_experience_for_spell_heal(damage):
    return round(damage * 15)

def get_experience_for_defence(damage):
    return round(damage * 5)
