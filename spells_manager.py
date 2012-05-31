from collections import OrderedDict
import copy
import random
import smarty

__author__ = 'PavelP'

_ = lambda s: s

spell_messages = {
    0 : _("{0} used ability {1}[{2}/{3}]"),
    1 : _("{0} casts spell {1} on {2} [{3}/{4}][{5}/{6}]"),
    2 : _("{0} tried to cast {1} on {2}, but had low mana"),
    3 : _("{0} tried to cast {1} on {2}, but couldn't"),
    4 : _("{0} tried to use ability {1}, but had low energy"),
    5 : _("{0} tried to use ability {1}, but couldn't"),
}

class SpellInfo:
    # spell/ability type
    # 0 - Special one round spell/ability
    # 1 - Direct spell
    # 2 - Over time spell
    # 3 - Area of effect spell
    # 4 - Buf (and debuf)
    def __init__(self, id, name, class_id, type, required_level, mana, price, description):
        self.id = id
        self.name = name
        self.class_id = class_id
        self.type = type
        self.required_level = required_level
        self.mana = mana
        self.price = price
        self.description = description

    def translate(self, locale):
        spell = copy.copy(self)
        spell.name = locale.translate(self.name)
        spell.description = locale.translate(self.description)
        return spell

class Ability(object):
    def init_internal(self, spell_info, who_character, whom_character):
        self.who_character = who_character
        self.whom_character = whom_character
        self.spell_info = spell_info
        self.experience = 0

    def consume_mana(self):
        if self.who_character.mana >= self.spell_info.mana:
            self.who_character.mana -= self.spell_info.mana
            return True
        return False

    def is_hit(self, percent):
        return True

    def get_low_mana_message(self, locale):
        return locale.translate(spell_messages[4]).format(
            self.who_character.name,
            locale.translate(self.spell_info.name))

    def get_failed_message(self, locale):
        return locale.translate(spell_messages[5]).format(
            self.who_character.name,
            locale.translate(self.spell_info.name))

class BerserkFurySpell(Ability):
    def init(self, who_character, whom_character):
        super(BerserkFurySpell, self).init_internal(spells[build_id(10, 0)], who_character, whom_character)
        self.attack = 0

    def is_hit(self, percent):
        return True

    def round_start(self):
        self.attack = round(self.who_character.attack * 0.3, 2)
        self.who_character.attack += self.attack
        self.experience = round(self.attack*0.9)
        self.who_character.experience += self.experience

    def round_end(self):
        self.who_character.attack -= self.attack
        return True

    def get_message(self, locale):
        return locale.translate(spell_messages[0]).format(
            self.who_character.name,
            locale.translate(self.spell_info.name),
            self.experience,
            self.who_character.experience)

class Spell(object):
    def init_internal(self, spell_info, who_character, whom_character):
        self.who_character = who_character
        self.whom_character = whom_character
        self.spell_info = spell_info
        self.experience = 0

    def consume_mana(self):
        if self.who_character.mana >= self.spell_info.mana:
            self.who_character.mana -= self.spell_info.mana
            return True
        return False

    def is_hit(self, percent):
        if (percent*self.who_character.magic_attack)/self.whom_character.magic_defence > 1.5: # definitely hit
            return True
        elif (percent*self.who_character.magic_attack)/self.whom_character.magic_defence < 1: # definitely not hit
            return False
        elif random.random()*0.5 < (percent*self.who_character.magic_attack)/self.whom_character.magic_defence - 1:
            return True
        return False

    def get_low_mana_message(self, locale):
        return locale.translate(spell_messages[2]).format(
            self.who_character.name,
            locale.translate(self.spell_info.name),
            self.whom_character.name)

    def get_failed_message(self, locale):
        return locale.translate(spell_messages[3]).format(
            self.who_character.name,
            locale.translate(self.spell_info.name),
            self.whom_character.name)

class PrayerForAttackSpell(Spell):
    def init(self, who_character, whom_character):
        super(PrayerForAttackSpell, self).init_internal(spells[build_id(15, 0)], who_character, whom_character)
        self.duration = smarty.get_spell_duration(who_character)
        self.attack = 0
        self.counter = 1

    def round_start(self):
        attack = round(self.whom_character.attack * 0.1, 2)
        self.attack += attack
        self.whom_character.attack += attack
        self.experience = round(attack*0.9)
        self.who_character.experience += self.experience

    def round_end(self):
        self.counter += 1
        if self.counter > self.duration:
            self.whom_character.attack -= self.attack
            return True
        return False

    def get_message(self, locale):
        return locale.translate(spell_messages[1]).format(
            self.who_character.name,
            locale.translate(self.spell_info.name),
            self.whom_character.name,
            self.counter,
            self.duration,
            self.experience,
            self.who_character.experience)

class SpellProcessor:
    def __init__(self):
        pass

spell_range = 100

build_id = lambda type, id: spell_range*type + id
# means that 1000-1099 are warrior spells, 1100-1199 are guardian spells, 2100-2199 are archer spells, etc.
spells = {
    #warrior
    build_id(10, 0) : SpellInfo(build_id(10, 0), _("Berserk Fury"),             0, 4, 1, 5, 15, _("Howling with rage, you rush to the enemy. Attack power is increased")),
    build_id(10, 1) : SpellInfo(build_id(10, 1), _("Disarmament"),              0, 0, 2, 8, 15, _("You knock weapons out of enemy hands. He can not attack")),
    # guardian
    build_id(11, 0) : SpellInfo(build_id(11, 0), _("Armor"),                    1, 0, 1, 5, 15, _("")),
    build_id(11, 1) : SpellInfo(build_id(11, 1), _("Shield Block"),             1, 0, 2, 8, 15, _("")),
    # archer
    build_id(12, 0) : SpellInfo(build_id(12, 0), _("Evasion"),                  2, 0, 1, 5, 15, _("")),
    build_id(12, 1) : SpellInfo(build_id(12, 1), _("Berserk Fury"),             2, 0, 2, 8, 15, _("")),
    # rogue
    build_id(13, 0) : SpellInfo(build_id(13, 0), _("Evasion"),                  3, 0, 1, 5, 15, _("")),
    build_id(13, 1) : SpellInfo(build_id(13, 1), _("Trip"),                     3, 0, 2, 8, 15, _("")),
    # mage
    build_id(14, 0) : SpellInfo(build_id(14, 0), _("Frost Needle"),             4, 0, 1, 5, 15, _("")),
    build_id(14, 1) : SpellInfo(build_id(14, 1), _("Fire Spark"),               4, 0, 2, 8, 15, _("")),
    # priest
    build_id(15, 0) : SpellInfo(build_id(15, 0), _("Prayer for Attack"),        5, 4, 1, 5, 15, _("")),
    build_id(15, 1) : SpellInfo(build_id(15, 1), _("Prayer for Protection"),    5, 0, 2, 8, 15, _("")),
    # warlock
    build_id(16, 0) : SpellInfo(build_id(16, 0), _("Curse of Weakness"),        6, 0, 1, 5, 15, _("")),
    build_id(16, 1) : SpellInfo(build_id(16, 1), _("Leech Life"),               6, 0, 2, 8, 15, _("")),
    # necromancer
    build_id(17, 0) : SpellInfo(build_id(17, 0), _("Infection"),                7, 0, 1, 5, 15, _("")),
    build_id(17, 1) : SpellInfo(build_id(17, 1), _("Stench"),                   7, 0, 2, 8, 15, _(""))
}

spells_action_classes = {
    build_id(10, 0) : BerserkFurySpell,
    build_id(15, 0) : PrayerForAttackSpell
}

def get_spell(id, locale):
    return spells[id].translate(locale)

def get_all_spells(locale):
    all = OrderedDict()
    for class_name in smarty.classes.values():
        all[locale.translate(class_name)] = OrderedDict()
    for spell in spells.values():
        all[locale.translate(smarty.classes[spell.class_id])][spell.id] = locale.translate(spell.name)
    return all


def get_spells(character, locale):
    result = list()
    if character.spells:
        spell_ids = character.spells.split(",")
        for spell_id in spell_ids:
            result.append(spells[int(spell_id)].translate(locale))
    return result

def get_spells_to_learn(character, locale):
    result = list()
    first_spell_id = build_id(character.class_id, 0)
    known_spells_ids = list()
    if character.spells:
        known_spells_ids = character.spells.split(",")
    for spell in spells.values():
        if spell.class_id == character.class_id:
            if not str(spell.id) in known_spells_ids:
                if spell.required_level <= character.level:
                    result.append(spell.translate(locale))
                else:
                    break
    return result