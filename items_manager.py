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

class Classes(object):
    def __init__(self, *classes):
        self.classes = list()
        self.classes.extend(classes)

    def get_class_names(self, locale):
        result = list()
        if len(self.classes) == len(smarty.classes):
            result.append(locale.translate(_("All")))
        else:
            for class_id in self.classes:
                result.append(locale.translate(smarty.classes[class_id]))

        return result

    def get_classes(self):
        return self.classes

class Item(object):
    def __init__(self, id, name, type, classes, required_stats, bonus_stats, price, description):
        self.id = id
        self.name = name
        self.type = type
        self.classes = classes
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
    def __init__(self, id, name, type, classes, required_stats, bonus_stats, price, description, min_damage, max_damage):
        super(Weapon, self).__init__(id, name, type, classes, required_stats, bonus_stats, price, description)
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
    build_id(0, 0) : Weapon(build_id(0, 0), _("Knife"), 0, Classes(0, 1, 2, 3, 4, 5, 6, 7), RequiredStats(0, 0, 0, 0, 0), BonusStats(0, 0, 0, 0, 0, 0, 0), 0, _("Knife is basic weapon, everybody has it"), 1.2, 2.2),
    build_id(0, 1) : Weapon(build_id(0, 1), _("Stone"), 0, Classes(0, 1, 2, 3), RequiredStats(0, 0, 0, 0, 0), BonusStats(1, 1, 0, 0, 0, 0, 0), 150, _("Sharpened stone is the weapon of real barbarian"), 1.4, 2.6),
    #left hand
    build_id(1, 0) : Item(build_id(1, 0), _("Basic shield"), 1, Classes(0, 1, 2, 3), RequiredStats(2, 0, 0, 0, 0), BonusStats(1, 0, 0, 0, 0, 0, 0), 150, _("Just wooden shield with iron circle in center")),
    #head
    build_id(2, 0) : Item(build_id(2, 0), _("Basic helmet"), 2, Classes(0, 1, 2, 3), RequiredStats(2, 0, 0, 0, 0), BonusStats(0, 1, 0, 0, 0, 0, 0), 150, _("Wooden helmet is a better guard than your skull")),
    # body
    build_id(3, 0) : Item(build_id(3, 0), _("A"), 3, Classes(2, 3, 4, 5), RequiredStats(0, 0, 0, 0, 0), BonusStats(0, 0, 0, 0, 0, 0, 0), 0, _("You don't wear anything")),
    # hands
    build_id(4, 0) : Item(build_id(4, 0), _("B"), 4, Classes(3, 4, 5), RequiredStats(0, 0, 0, 0, 0), BonusStats(0, 0, 0, 0, 0, 0, 0), 0, _("You don't wear anything")),
    # legs
    build_id(5, 0) : Item(build_id(5, 0), _("C"), 5, Classes(7), RequiredStats(0, 0, 0, 0, 0), BonusStats(0, 0, 0, 0, 0, 0, 0), 0, _("You don't wear anything")),
    # feet
    build_id(6, 0) : Item(build_id(6, 0), _("D"), 6, Classes(0, 1, 2, 3), RequiredStats(0, 0, 0, 0, 0), BonusStats(0, 0, 0, 0, 0, 0, 0), 0, _("You don't wear anything")),
    # cloak
    build_id(7, 0) : Item(build_id(7, 0), _("E"), 7, Classes(0, 1, 2, 3), RequiredStats(0, 0, 0, 0, 0), BonusStats(0, 0, 0, 0, 0, 0, 0), 0, _("You don't wear anything")),
    }

shop_items_ids = [
    build_id(0, 1),
    build_id(1, 0),
    build_id(2, 0),
    build_id(3, 0),
    build_id(4, 0),
    build_id(5, 0),
    build_id(6, 0),
    build_id(7, 0)
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
    if character.right_hand:
        return get_item(int(character.right_hand), locale).name
    else:
        return locale.translate(_("Empty hands"))

def get_bag_items(character, locale):
    items = list()
    item_ids = character.bag.split(",")
    for item_id in item_ids:
        items.append(get_item(int(item_id), locale))

    return items

def get_items(character):
    items = dict()
    if character.right_hand:
        items["right_hand"] = character.right_hand
    if character.left_hand:
        items["left_hand"] = character.left_hand
    if character.head:
        items["head"] = character.head
    if character.body:
        items["body"] = character.body
    if character.hands:
        items["hands"] = character.hands
    if character.legs:
        items["legs"] = character.legs
    if character.feet:
        items["feet"] = character.feet
    if character.cloak:
        items["cloak"] = character.cloak
    if character.bag:
        items["bag"] = character.bag

    return items

def get_item_type(id):
    item_type = "undefined"
    if items[id].type == 0:
        item_type = "right_hand"
    elif items[id].type == 1:
        item_type = "left_hand"
    elif items[id].type == 2:
        item_type = "head"
    elif items[id].type == 3:
        item_type = "body"
    elif items[id].type == 4:
        item_type = "hands"
    elif items[id].type == 5:
        item_type = "legs"
    elif items[id].type == 6:
        item_type = "feet"
    elif items[id].type == 7:
        item_type = "cloak"

    return item_type

def check_item(character, item_id):
    result = False
    required_stats = items[item_id].required_stats
    classes = items[item_id].classes.get_classes()
    if (character.level >= required_stats.level
        and character.strength >= required_stats.strength
        and character.dexterity>= required_stats.dexterity
        and character.intellect >= required_stats.intellect
        and character.wisdom >= required_stats.wisdom
        and character.class_id in classes):
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
            , ""
            , ""
            , ""
            , ""
            , ""
            , ""
            , ""
        ]
    else: # casters
        stuff = [
              str(build_id(0, 0))
            , ""
            , ""
            , ""
            , ""
            , ""
            , ""
            , ""
        ]

    return stuff