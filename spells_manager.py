from collections import OrderedDict
import copy
import smarty

__author__ = 'PavelP'

_ = lambda s: s

class Spell:
    # ordinal is ordinal_group when this spell/ability is activated - special are 0 and 1, abilities is 2, damage is 3, and heal is 4
    def __init__(self, id, name, class_id, ordinal , required_level, damage, mana, price, description):
        self.id = id
        self.name = name
        self.class_id = class_id
        self.ordinal = ordinal
        self.required_level = required_level
        self.damage = damage
        self.mana = mana
        self.price = price
        self.description = description

    def translate(self, locale):
        spell = copy.copy(self)
        spell.name = locale.translate(self.name)
        spell.description = locale.translate(self.description)
        return spell

spell_range = 100

build_id = lambda type, id: spell_range*type + id
# means that 1000-1099 are warrior spells, 1100-1199 are guardian spells, 2100-2199 are archer spells, etc.
spells = {
    #warrior
    build_id(10, 0) : Spell(build_id(10, 0), _("Berserk Fury"),             0, 2, 1, 0, 5, 15, _("Howling with rage, you rush to the enemy. Attack power is increased")),
    build_id(10, 1) : Spell(build_id(10, 1), _("Disarmament"),              0, 2, 2, 0, 8, 15, _("You knock weapons out of enemy hands. He can not attack")),
    # guardian
    build_id(11, 0) : Spell(build_id(11, 0), _("Armor"),                    1, 2, 1, 0, 15, 5, _("")),
    build_id(11, 1) : Spell(build_id(11, 1), _("Shield Block"),             1, 2, 2, 0, 8, 15, _("")),
    # archer
    build_id(12, 0) : Spell(build_id(12, 0), _("Evasion"),                  2, 2, 1, 0, 5, 15, _("")),
    build_id(12, 1) : Spell(build_id(12, 1), _("Berserk Fury"),             2, 2, 2, 0, 8, 15, _("")),
    # rogue
    build_id(13, 0) : Spell(build_id(13, 0), _("Evasion"),                  3, 2, 1, 0, 5, 15, _("")),
    build_id(13, 1) : Spell(build_id(13, 1), _("Trip"),                     3, 2, 2, 0, 8, 15, _("")),
    # mage
    build_id(14, 0) : Spell(build_id(14, 0), _("Frost Needle"),             4, 3, 1, 2, 5, 15, _("")),
    build_id(14, 1) : Spell(build_id(14, 1), _("Fire Spark"),               4, 3, 2, 3, 8, 15, _("")),
    # priest
    build_id(15, 0) : Spell(build_id(15, 0), _("Prayer for Attack"),        5, 1, 1, 0, 5, 15, _("")),
    build_id(15, 1) : Spell(build_id(15, 1), _("Prayer for Protection"),    5, 1, 2, 0, 8, 15, _("")),
    # warlock
    build_id(16, 0) : Spell(build_id(16, 0), _("Curse of Weakness"),        6, 3, 1, 2, 5, 15, _("")),
    build_id(16, 1) : Spell(build_id(16, 1), _("Leech Life"),               6, 3, 2, 3, 8, 15, _("")),
    # necromancer
    build_id(17, 0) : Spell(build_id(17, 0), _("Infection"),                7, 3, 1, 2, 5, 15, _("")),
    build_id(17, 1) : Spell(build_id(17, 1), _("Stench"),                   7, 3, 2, 3, 8, 15, _(""))
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