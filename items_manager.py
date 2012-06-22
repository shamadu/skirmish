from collections import OrderedDict
import copy
import smarty

__author__ = 'Pavel Padinker'

_ = lambda s: s

class RequiredStats(object):
    def __init__(self, level, strength, dexterity, intellect, wisdom):
        self.level = level
        self.strength = strength
        self.dexterity = dexterity
        self.intellect = intellect
        self.wisdom = wisdom

    def get_required(self, locale):
        result = dict()
        if self.level > 0:
            result[locale.translate(smarty.stat_names[4])] = self.level
        if self.strength > 0:
            result[locale.translate(smarty.stat_names[0])] = self.strength
        if self.dexterity > 0:
            result[locale.translate(smarty.stat_names[1])] = self.dexterity
        if self.intellect > 0:
            result[locale.translate(smarty.stat_names[2])] = self.intellect
        if self.wisdom > 0:
            result[locale.translate(smarty.stat_names[3])] = self.wisdom

        return result

class BonusStats(object):
    def __init__(self, strength, dexterity, intellect, wisdom, min_dmg, max_dmg, spell_dmg):
        self.strength = strength
        self.dexterity = dexterity
        self.intellect = intellect
        self.wisdom = wisdom
        self.min_dmg = min_dmg
        self.max_dmg = max_dmg
        self.spell_dmg = spell_dmg

    def get_bonus(self, locale):
        result = dict()
        if self.strength > 0:
            result[locale.translate(smarty.stat_names[0])] = self.strength
        if self.dexterity > 0:
            result[locale.translate(smarty.stat_names[1])] = self.dexterity
        if self.intellect > 0:
            result[locale.translate(smarty.stat_names[2])] = self.intellect
        if self.wisdom > 0:
            result[locale.translate(smarty.stat_names[3])] = self.wisdom
        if self.min_dmg > 0:
            result[locale.translate(smarty.stat_names[5])] = self.min_dmg
        if self.max_dmg > 0:
            result[locale.translate(smarty.stat_names[6])] = self.max_dmg
        if self.spell_dmg > 0:
            result[locale.translate(smarty.stat_names[7])] = self.spell_dmg

        return result

class Item(object):
    def __init__(self, id, name, type, required_stats, bonus_stats, price, description):
        self.id = id
        self.name = name
        self.type = type
        self.required_stats = required_stats
        self.bonus_stats = bonus_stats
        self.price = price
        self.description = description

    def translate(self, locale):
        item = copy.copy(self)
        item.name = locale.translate(self.name)
        item.description = locale.translate(self.description)
        return item


class Weapon(Item):
    def __init__(self, id, name, type, required_stats, bonus_stats, price, description, min_damage, max_damage):
        super(Weapon, self).__init__(id, name, type, required_stats, bonus_stats, price, description)
        self.min_damage = min_damage
        self.max_damage = max_damage

item_groups = {
    0 : _("Right hand"),
    1 : _("Left hand"),
    2 : _("Head"),
    3 : _("Body"),
    4 : _("Hands"),
    5 : _("Legs"),
    6 : _("Feet"),
    7 : _("Cloak"),
}

# means that 0-99 are weapons, 100 - no shield, 101-199 are shields, 200 - empty head, 201-299 are helmets, etc.
build_id = lambda type, id: 100*type + id

items = {
    #right hand
    build_id(0, 0) : Weapon(build_id(0, 0), _("Knife"), 0, RequiredStats(0, 0, 0, 0, 0), BonusStats(0, 0, 0, 0, 0, 0, 0), 0, _("Knife is basic weapon, everybody has it"), 1.2, 2.2),
    build_id(0, 1) : Weapon(build_id(0, 1), _("Stone"), 0, RequiredStats(0, 0, 0, 0, 0), BonusStats(1, 1, 0, 0, 0, 0, 0), 15, _("Sharpened stone is the weapon of real barbarian"), 1.4, 2.6),
    #left hand
    build_id(1, 0) : Item(build_id(1, 0), _("Nothing"), -1, RequiredStats(0, 0, 0, 0, 0), BonusStats(0, 0, 0, 0, 0, 0, 0), 0, _("You don't wear anything")),
    build_id(1, 1) : Item(build_id(1, 1), _("Basic shield"), 1, RequiredStats(2, 0, 0, 0, 0), BonusStats(1, 0, 0, 0, 0, 0, 0), 15, _("Just wooden shield with iron circle in center")),
    #head
    build_id(2, 0) : Item(build_id(2, 0), _("Nothing"), -1, RequiredStats(0, 0, 0, 0, 0), BonusStats(0, 0, 0, 0, 0, 0, 0), 0, _("You don't wear anything")),
    build_id(2, 1) : Item(build_id(2, 1), _("Basic helmet"), 2, RequiredStats(2, 0, 0, 0, 0), BonusStats(0, 1, 0, 0, 0, 0, 0), 15, _("Wooden helmet is a better guard than your skull")),
    # body
    build_id(3, 0) : Item(build_id(3, 0), _("Nothing"), -1, RequiredStats(0, 0, 0, 0, 0), BonusStats(0, 0, 0, 0, 0, 0, 0), 0, _("You don't wear anything")),
    # hands
    build_id(4, 0) : Item(build_id(4, 0), _("Nothing"), -1, RequiredStats(0, 0, 0, 0, 0), BonusStats(0, 0, 0, 0, 0, 0, 0), 0, _("You don't wear anything")),
    # legs
    build_id(5, 0) : Item(build_id(5, 0), _("Nothing"), -1, RequiredStats(0, 0, 0, 0, 0), BonusStats(0, 0, 0, 0, 0, 0, 0), 0, _("You don't wear anything")),
    # feet
    build_id(6, 0) : Item(build_id(6, 0), _("Nothing"), -1, RequiredStats(0, 0, 0, 0, 0), BonusStats(0, 0, 0, 0, 0, 0, 0), 0, _("You don't wear anything")),
    # cloak
    build_id(7, 0) : Item(build_id(7, 0), _("Nothing"), -1, RequiredStats(0, 0, 0, 0, 0), BonusStats(0, 0, 0, 0, 0, 0, 0), 0, _("You don't wear anything")),
    }

shop_items_ids = [
    build_id(0, 1),
    build_id(1, 1),
    build_id(2, 1)
]

def get_shop(locale):
    shop = OrderedDict()
    for group_name in item_groups.values():
        shop[locale.translate(group_name)] = OrderedDict()
    for id in shop_items_ids:
        item = items[id]
        shop[locale.translate(item_groups[item.type])][item.id] = locale.translate(item.name)
    return shop

def get_all(locale):
    all = OrderedDict()
    for group_name in item_groups.values():
        all[locale.translate(group_name)] = OrderedDict()
    for item in items.values():
        if item.type != -1:
            all[locale.translate(item_groups[item.type])][item.id] = locale.translate(item.name)
    return all

def get_item_group_name(type, locale):
    return locale.translate(item_groups[type])

def get_item(id, locale):
    return items[id].translate(locale)

def get_current_weapon_name(character, locale):
    return get_item(int(character.right_hand.split(",")[0]), locale).name

def get_items(item_ids_str, locale):
    items = list()
    item_ids = item_ids_str.split(",")
    for item_id in item_ids:
        items.append(get_item(int(item_id), locale))

    return items

def get_item_type(id):
    item_type = "undefined"
    if items[id].type == 0:
        item_type = "right_hand"
    elif items[id].type == 1 or (items[id].type == -1 and id == build_id(1, 0)):
        item_type = "left_hand"
    elif items[id].type == 2 or (items[id].type == -1 and id == build_id(2, 0)):
        item_type = "head"
    elif items[id].type == 3 or (items[id].type == -1 and id == build_id(3, 0)):
        item_type = "body"
    elif items[id].type == 4 or (items[id].type == -1 and id == build_id(4, 0)):
        item_type = "hands"
    elif items[id].type == 5 or (items[id].type == -1 and id == build_id(5, 0)):
        item_type = "legs"
    elif items[id].type == 6 or (items[id].type == -1 and id == build_id(6, 0)):
        item_type = "feet"
    elif items[id].type == 7 or (items[id].type == -1 and id == build_id(7, 0)):
        item_type = "cloak"

    return item_type

def check_item(character, item_id):
    result = False
    required_stats = items[item_id].required_stats
    if (character.level >= required_stats.level
        and character.strength >= required_stats.strength
        and character.dexterity>= required_stats.dexterity
        and character.intellect >= required_stats.intellect
        and character.wisdom >= required_stats.wisdom):
        result = True
    return result

def get_bonuses(item_id):
    bonus_stats = items[item_id].bonus_stats
    result = {}
    if bonus_stats.strength != 0:
        result["strength"] = bonus_stats.strength
    if bonus_stats.dexterity != 0:
        result["dexterity"] = bonus_stats.dexterity
    if bonus_stats.intellect != 0:
        result["intellect"] = bonus_stats.intellect
    if bonus_stats.wisdom != 0:
        result["wisdom"] = bonus_stats.wisdom
    if bonus_stats.min_dmg != 0:
        result["min_dmg"] = bonus_stats.min_dmg
    if bonus_stats.max_dmg != 0:
        result["max_dmg"] = bonus_stats.max_dmg
    if bonus_stats.spell_dmg != 0:
        result["spell_dmg"] = bonus_stats.spell_dmg

    return result

# return default stuff
def get_default_stuff(class_id):
    stuff = []
    if class_id < 4: # non casters
        stuff = [
              str(build_id(0, 0))
            , str(build_id(1, 0))
            , str(build_id(2, 0))
            , str(build_id(3, 0))
            , str(build_id(4, 0))
            , str(build_id(5, 0))
            , str(build_id(6, 0))
            , str(build_id(7, 0))
        ]
    else: # casters
        stuff = [
              str(build_id(0, 0))
            , str(build_id(1, 0))
            , str(build_id(2, 0))
            , str(build_id(3, 0))
            , str(build_id(4, 0))
            , str(build_id(5, 0))
            , str(build_id(6, 0))
            , str(build_id(7, 0))
        ]

    return stuff