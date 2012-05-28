import copy

__author__ = 'PavelP'

_ = lambda s: s

class Spell:
    def __init__(self, id, name, required_level, price, description):
        self.id = id
        self.name = name
        self.required_level = required_level
        self.price = price
        self.description = description

    def translate(self, locale):
        spell = copy.copy(self)
        spell.name = locale.translate(self.name)
        spell.description = locale.translate(self.description)
        return spell

spell_range = 100

# means that 0-99 are warrior spells, 100-199 are guardian spells, 201-299 are archer spells, etc.
build_id = lambda type, id: spell_range*type + id

spells = {
    #warrior
    build_id(0, 0) : Spell(build_id(0, 0), _("Berserk Fury"), 1, 15, _("Howling with rage, you rush to the enemy. Attack power is increased")),
    build_id(0, 1) : Spell(build_id(0, 1), _("Disarmament"), 2, 15, _("You knock weapons out of enemy hands. He can not attack")),
    # guardian
    build_id(1, 0) : Spell(build_id(1, 0), _("Armor"), 1, 15, _("")),
    build_id(1, 1) : Spell(build_id(1, 1), _("Shield Block"), 2, 15, _("")),
    # archer
    build_id(2, 0) : Spell(build_id(2, 0), _("Evasion"), 1, 15, _("")),
    build_id(2, 1) : Spell(build_id(2, 1), _("Berserk Fury"), 2, 15, _("")),
    # rogue
    build_id(3, 0) : Spell(build_id(3, 0), _("Evasion"), 1, 15, _("")),
    build_id(3, 1) : Spell(build_id(3, 1), _("Trip"), 2, 15, _("")),
    # mage
    build_id(4, 0) : Spell(build_id(4, 0), _("Frost Needle"), 1, 15, _("")),
    build_id(4, 1) : Spell(build_id(4, 1), _("Fire Spark"), 2, 15, _("")),
    # priest
    build_id(5, 0) : Spell(build_id(5, 0), _("Prayer for Attack"), 1, 15, _("")),
    build_id(5, 1) : Spell(build_id(5, 1), _("Prayer for Protection"), 2, 15, _("")),
    # warlock
    build_id(6, 0) : Spell(build_id(6, 0), _("Curse of Weakness"), 1, 15, _("")),
    build_id(6, 1) : Spell(build_id(6, 1), _("Leech Life"), 2, 15, _("")),
    # necromancer
    build_id(7, 0) : Spell(build_id(7, 0), _("Infection"), 1, 15, _("")),
    build_id(7, 1) : Spell(build_id(7, 1), _("Stench"), 2, 15, _("")),
}

def get_spells(character, locale):
    result = list()
    if character.spells:
        spell_ids = character.spells.split(",")
        for spell_id in spell_ids:
            result.append(spells[int(spell_id)].translate(locale))
    return result

def get_spells_to_learn(character, locale):
    result = list()
    first_spell_id = build_id(character.classID, 0)
    known_spells_ids = list()
    if character.spells:
        known_spells_ids = character.spells.split(",")
    for i in range(spell_range):
        if i in spells.keys():
            spell = spells[first_spell_id + i]
            if not str(spell.id) in known_spells_ids:
                if spell.required_level <= character.level:
                    result.append(spell.translate(locale))
                else:
                    break
    return result