from collections import OrderedDict
import copy
import random
import smarty

__author__ = 'PavelP'

_ = lambda s: s

spell_messages = {
    0 : _("<b>{0}</b> used ability <b>{1}</b>[<font class=\"font-exp\">{2}</font>/<font class=\"font-exp\">{3}</font>]"),
    1 : _("<b>{0}</b> increases attack of <b>{2}</b> [{3}/{4}][<font class=\"font-exp\">{5}</font>/<font class=\"font-exp\">{6}</font>]"),
    2 : _("<b>{0}</b> tried to cast <b>{1}</b> on <b>{2}</b>, but had low mana"),
    3 : _("<b>{0}</b> tried to cast <b>{1}</b> on <b>{2}</b>, but couldn't"),
    4 : _("<b>{0}</b> tried to use ability <b>{1}</b>, but had low energy"),
    5 : _("<b>{0}</b> tried to use ability <b>{1}</b>, but couldn't"),
    6 : _("<b>{0}</b> freezes <b>{2}</b> with spell <b>{1}</b> for <font class=\"font-damage\">{3}</font>({4})[<font class=\"font-exp\">{5}</font>/<font class=\"font-exp\">{6}</font>]"),
    7 : _("<b>{0}</b> burns <b>{2}</b> with spell <b>{1}</b> for <font class=\"font-damage\">{3}</font>({4})[<font class=\"font-exp\">{5}</font>/<font class=\"font-exp\">{6}</font>]"),
    8 : _("<b>{0}</b> heals <b>{2}</b> with spell <b>{1}</b> for <font class=\"font-heal\">{3}</font>({4})[<font class=\"font-exp\">{5}</font>/<font class=\"font-exp\">{6}</font>]"),
    9 : _("<b>{0}</b> tried to attack <b>{1}</b>, but killed one phantom {2}/{3}"),
    10 : _("<b>{0}</b> created {1} phantoms [{2}/{3}][<font class=\"font-exp\">{4}</font>/<font class=\"font-exp\">{5}</font>]"),
    11 : _("<b>{0}</b> used ability <b>{1}</b> and knocked the weapon from <b>{2}</b>[<font class=\"font-exp\">{3}</font>/<font class=\"font-exp\">{4}</font>]"),
    12 : _("<b>{0}</b> has tried to attack <b>{1}</b> but has no weapon in hands"),
    13 : _("<b>{0}</b> receives the reflected damage <font class=\"font-damage\">{1}</font>/{2}(<b>{3}</b>[<font class=\"font-exp\">{4}</font>/<font class=\"font-exp\">{5}</font>])"),
    14 : _("<b>{0}</b> has rounded <b>{1}</b> with mirror shield [{2}/{3}][<font class=\"font-exp\">{4}</font>/<font class=\"font-exp\">{5}</font>]"),
    15 : _("<b>{0}</b> has tried to attack <b>{1}</b> but he has dodged"),
    16 : _("<b>{0}</b> casts spell <b>{1}</b> and increases defence of <b>{2}</b> [{3}/{4}][<font class=\"font-exp\">{5}</font>/<font class=\"font-exp\">{6}</font>]"),
    17 : _("<b>{0}</b> used ability <b>{1}</b> and reduced defence of <b>{2}</b>[<font class=\"font-exp\">{3}</font>/<font class=\"font-exp\">{4}</font>]"),
    18 : _("<b>{0}</b> casts spell <b>{1}</b> and decreases defence of <b>{2}</b> [{3}/{4}][<font class=\"font-exp\">{5}</font>/<font class=\"font-exp\">{6}</font>]"),
    19 : _("<b>{0}</b> casts spell <b>{1}</b> on <b>{2}</b> and steals <font class=\"font-damage\">{3}</font>({4}) <font class=\"font-heal\">{5}</font>({6})[<font class=\"font-exp\">{7}</font>/<font class=\"font-exp\">{8}</font>]"),
    20 : _("<b>{0}</b> damages <b>{2}</b> with spell <b>{1}</b> for <font class=\"font-damage\">{3}</font>({4})[{5}/{6}][<font class=\"font-exp\">{7}</font>/<font class=\"font-exp\">{8}</font>]"),
    21 : _("<b>{0}</b> has rounded <b>{1}</b> with stench [{2}/{3}][<font class=\"font-exp\">{4}</font>/<font class=\"font-exp\">{5}</font>]"),
    22 : _("<b>{0}</b> receives the damage from stench <font class=\"font-damage\">{1}</font>/{2}(<b>{3}</b>[<font class=\"font-exp\">{4}</font>/<font class=\"font-exp\">{5}</font>])"),
    23 : _("<b>{0}</b> used ability <b>{1}</b> and increased his defence[<font class=\"font-exp\">{2}</font>/<font class=\"font-exp\">{3}</font>]"),
    24 : _("<b>{0}</b> tried to use ability <b>{1}</b>, but didn't have shield in hands"),
}

class SpellInfo:
    # spell/ability type
    # 0 - Special one round spell/ability
    # 1 - Direct damage spell
    # 2 - Direct heal spell
    # 3 - Affects victim spell
    # 4 - Over time spell
    # 5 - Affects attacker spell
    # 6 - After attack spell
    def __init__(self, id, name, class_id, type, is_self, required_level, base_amount, mana, price, description):
        self.id = id
        self.name = name
        self.class_id = class_id
        self.type = type
        self.is_self = is_self
        self.required_level = required_level
        self.base_amount = base_amount
        self.mana = mana
        self.price = price
        self.description = description

    def translate(self, locale):
        spell = copy.copy(self)
        spell.name = locale.translate(self.name)
        spell.description = locale.translate(self.description)
        return spell

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
        if random.uniform(0.9, 1.1) < (percent*self.who_character.magic_attack)/self.whom_character.magic_defence:
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

class LongSpell(Spell):
    def init_internal(self, spell_info, who_character, whom_character):
        super(LongSpell, self).init_internal(spell_info, who_character, whom_character)
        self.duration = smarty.get_spell_duration(who_character)
        self.counter = 0

    # implement if inherit
    def on_round_start(self):
        pass

    def round_start(self):
        self.counter += 1
        self.on_round_start()

    # implement if inherit
    def on_effect_end(self):
        pass

    def round_end(self):
        if self.counter == self.duration:
            self.on_effect_end()
            return True
        return False

class Ability(LongSpell):
    def init_internal(self, spell_info, who_character, whom_character):
        super(Ability, self).init_internal(spell_info, who_character, whom_character)
        self.duration = 1
        self.counter = 0

    def is_hit(self, percent):
        if random.uniform(0.1, 0.2) < percent:
            return True
        return False

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

    def on_round_start(self):
        self.attack = round(self.who_character.attack * 0.3, 2)
        self.who_character.attack += self.attack
        self.experience = round(self.attack*0.9)

    def on_effect_end(self):
        self.who_character.attack -= self.attack

    def get_message(self, locale):
        return locale.translate(spell_messages[0]).format(
            self.who_character.name,
            locale.translate(self.spell_info.name),
            self.experience,
            self.who_character.experience)

class BackHeelSpell(Ability):
    def init(self, who_character, whom_character):
        super(BackHeelSpell, self).init_internal(spells[build_id(13, 1)], who_character, whom_character)
        self.defence = 0

    def on_round_start(self):
        self.defence = round(self.whom_character.defence * 0.5, 2)
        self.whom_character.defence -= self.defence
        self.experience = round(self.defence*0.9)

    def on_effect_end(self):
        self.whom_character.defence += self.defence

    def get_message(self, locale):
        return locale.translate(spell_messages[17]).format(
            self.who_character.name,
            locale.translate(self.spell_info.name),
            self.whom_character.name,
            self.experience,
            self.who_character.experience)

class ArmorSpell(Ability):
    def init(self, who_character, whom_character):
        super(ArmorSpell, self).init_internal(spells[build_id(11, 0)], who_character, whom_character)
        self.defence = 0

    def on_round_start(self):
        self.defence = round(self.whom_character.defence * 2, 2)
        self.whom_character.defence += self.defence
        self.experience = round(self.defence*0.9)

    def on_effect_end(self):
        self.whom_character.defence -= self.defence

    def get_message(self, locale):
        return locale.translate(spell_messages[23]).format(
            self.who_character.name,
            locale.translate(self.spell_info.name),
            self.experience,
            self.who_character.experience)

class ShieldBlockSpell(Ability):
    def init(self, who_character, whom_character):
        super(ShieldBlockSpell, self).init_internal(spells[build_id(11, 1)], who_character, whom_character)
        self.defence = 0

    def on_round_start(self):
        if self.who_character.shield.split(",")[0] != build_id(1, 0):
            self.defence = round(self.whom_character.defence * 5, 2)
            self.whom_character.defence += self.defence
            self.experience = round(self.defence*0.9)

    def on_effect_end(self):
        self.whom_character.defence -= self.defence

    def get_message(self, locale):
        if self.defence != 0:
            return locale.translate(spell_messages[23]).format(
                self.who_character.name,
                locale.translate(self.spell_info.name),
                self.experience,
                self.who_character.experience)
        else:
            return locale.translate(spell_messages[24]).format(
                self.who_character.name,
                locale.translate(self.spell_info.name),
                self.experience,
                self.who_character.experience)

class FierceShotSpell(BerserkFurySpell):
    def init(self, who_character, whom_character):
        super(FierceShotSpell, self).init_internal(spells[build_id(12, 1)], who_character, whom_character)
        self.attack = 0

class AffectAttackSpell(object):
    def is_succeed_attack(self, attack_character, defence_character):
        self.attack_character = attack_character
        self.defence_character = defence_character
        return self.check_succeed_attack()

    # implement if inherit
    def check_succeed_attack(self):
        return True

    # implement if inherit
    def get_attack_message(self, locale):
        pass

class EvasionSpell(Ability, AffectAttackSpell):
    def init(self, who_character, whom_character):
        super(EvasionSpell, self).init_internal(spells[build_id(12, 0)], who_character, whom_character)

    def check_succeed_attack(self):
        return False

    def get_attack_message(self, locale):
        return locale.translate(spell_messages[15]).format(
            self.attack_character.name,
            self.defence_character.name)

    def on_round_start(self):
        self.experience = self.who_character.level*10

    def get_message(self, locale):
        return locale.translate(spell_messages[0]).format(
            self.who_character.name,
            locale.translate(self.spell_info.name),
            self.experience,
            self.who_character.experience)

class DodgeSpell(EvasionSpell):
    def init(self, who_character, whom_character):
        super(DodgeSpell, self).init_internal(spells[build_id(13, 0)], who_character, whom_character)

class DisarmamentSpell(Ability, AffectAttackSpell):
    def init(self, who_character, whom_character):
        super(DisarmamentSpell, self).init_internal(spells[build_id(10, 1)], who_character, whom_character)

    def check_succeed_attack(self):
        return False

    def get_attack_message(self, locale):
        return locale.translate(spell_messages[12]).format(
            self.attack_character.name,
            self.defence_character.name)

    def on_round_start(self):
        self.experience = self.who_character.level*10

    def get_message(self, locale):
        return locale.translate(spell_messages[11]).format(
            self.who_character.name,
            locale.translate(self.spell_info.name),
            self.whom_character.name,
            self.experience,
            self.who_character.experience)

class PrayerForAttackSpell(LongSpell):
    def init(self, who_character, whom_character):
        super(PrayerForAttackSpell, self).init_internal(spells[build_id(15, 0)], who_character, whom_character)
        self.attack = 0

    def on_round_start(self):
        attack = round(self.whom_character.attack * 0.1, 2)
        self.attack += attack
        self.whom_character.attack += attack
        self.experience = round(attack*0.9)

    def on_effect_end(self):
        self.whom_character.attack -= self.attack

    def get_message(self, locale):
        return locale.translate(spell_messages[1]).format(
            self.who_character.name,
            locale.translate(self.spell_info.name),
            self.whom_character.name,
            self.counter,
            self.duration,
            self.experience,
            self.who_character.experience)

class PrayerForProtectionSpell(LongSpell):
    def init(self, who_character, whom_character):
        super(PrayerForProtectionSpell, self).init_internal(spells[build_id(15, 2)], who_character, whom_character)
        self.defence = 0

    def on_round_start(self):
        defence = round(self.whom_character.defence * 0.1, 2)
        self.defence += defence
        self.whom_character.defence += defence
        self.experience = round(defence*0.9)

    def on_effect_end(self):
        self.whom_character.defence -= self.defence

    def get_message(self, locale):
        return locale.translate(spell_messages[16]).format(
            self.who_character.name,
            locale.translate(self.spell_info.name),
            self.whom_character.name,
            self.counter,
            self.duration,
            self.experience,
            self.who_character.experience)

class CurseOfWeaknessSpell(LongSpell):
    def init(self, who_character, whom_character):
        super(CurseOfWeaknessSpell, self).init_internal(spells[build_id(16, 0)], who_character, whom_character)
        self.defence = 0

    def on_round_start(self):
        if self.counter == 1: # apply effect
            self.defence = round(self.whom_character.defence * 0.4, 2)
            self.whom_character.defence -= self.defence
        self.experience = round(self.defence*0.9)

    def on_effect_end(self):
        self.whom_character.defence += self.defence

    def get_message(self, locale):
        return locale.translate(spell_messages[18]).format(
            self.who_character.name,
            locale.translate(self.spell_info.name),
            self.whom_character.name,
            self.counter,
            self.duration,
            self.experience,
            self.who_character.experience)

class InfectionSpell(LongSpell):
    def init(self, who_character, whom_character):
        super(InfectionSpell, self).init_internal(spells[build_id(17, 0)], who_character, whom_character)
        self.damage = 0

    def on_round_start(self):
        self.experience = 0
        self.damage = smarty.get_spell_damage(self.who_character, 1, self.spell_info.base_amount, self.whom_character)
        self.whom_character.health -= self.damage
        if self.who_character.name != self.whom_character.name:
            self.experience = smarty.get_experience_for_spell_damage(self.damage)
            if self.whom_character.health <= 0 and not self.whom_character.killer_name:
                self.whom_character.killer_name = self.who_character.name

    def get_message(self, locale):
        return locale.translate(spell_messages[20]).format(
            self.who_character.name,
            locale.translate(self.spell_info.name),
            self.whom_character.name,
            self.damage,
            smarty.apply_hp_colour(self.whom_character.health, self.whom_character.full_health),
            self.counter,
            self.duration,
            self.experience,
            self.who_character.experience)

class PhantomsSpell(LongSpell, AffectAttackSpell):
    def init(self, who_character, whom_character):
        super(PhantomsSpell, self).init_internal(spells[build_id(14, 2)], who_character, whom_character)
        self.all_phantoms = 3
        self.phantoms = self.all_phantoms

    def on_round_start(self):
        self.experience = self.who_character.level*10

    def check_succeed_attack(self):
        succeed_attack = (random.random() < 1/(self.phantoms + 1)) # 1 / phantoms_count + you
        if not succeed_attack:
            self.phantoms -= 1
            if self.phantoms == 0: # no phantoms - finish spell
                self.counter = self.duration
        return succeed_attack

    def get_attack_message(self, locale):
        return locale.translate(spell_messages[9]).format(
            self.attack_character.name,
            self.defence_character.name,
            self.phantoms,
            self.all_phantoms)

    def get_message(self, locale):
        return locale.translate(spell_messages[10]).format(
            self.who_character.name,
            self.phantoms,
            self.counter,
            self.duration,
            self.experience,
            self.who_character.experience)

class AfterAttackSpell:
    def process_after_attack(self, attack_character, damage):
        self.attack_character = attack_character
        self.damage = damage
        self.do_after_attack()

    # implement if inherit
    def do_after_attack(self):
        pass

    # implement if inherit
    def get_after_attack_message(self, locale):
        pass

class MirrorCharmSpell(LongSpell, AfterAttackSpell):
    def init(self, who_character, whom_character):
        super(MirrorCharmSpell, self).init_internal(spells[build_id(14, 3)], who_character, whom_character)

    def on_round_start(self):
        self.experience = self.who_character.level

    def do_after_attack(self):
        self.experience = 0
        self.damage = round(self.damage*0.3, 2)
        self.attack_character.health -= self.damage
        if self.attack_character.name != self.who_character.name:
            if self.whom_character.health <= 0 and not self.whom_character.killer_name:
                self.whom_character.killer_name = self.who_character.name
            self.experience = smarty.get_experience_for_spell_damage(self.damage)

    def get_after_attack_message(self, locale):
        return locale.translate(spell_messages[13]).format(
            self.attack_character.name,
            self.damage,
            smarty.apply_hp_colour(self.attack_character.health, self.attack_character.full_health),
            self.who_character.name,
            self.experience,
            self.who_character.experience)

    def get_message(self, locale):
        return locale.translate(spell_messages[14]).format(
            self.who_character.name,
            self.whom_character.name,
            self.counter,
            self.duration,
            self.experience,
            self.who_character.experience)

class StenchSpell(LongSpell, AfterAttackSpell):
    def init(self, who_character, whom_character):
        super(StenchSpell, self).init_internal(spells[build_id(17, 1)], who_character, whom_character)

    def on_round_start(self):
        self.experience = self.who_character.level

    def do_after_attack(self):
        self.experience = 0
        self.damage = smarty.get_spell_damage(self.who_character, 1, self.spell_info.base_amount, self.whom_character)
        self.attack_character.health -= self.damage
        if self.attack_character.name != self.who_character.name:
            if self.attack_character.health <= 0 and not self.attack_character.killer_name:
                self.attack_character.killer_name = self.who_character.name
            self.experience = smarty.get_experience_for_spell_damage(self.damage)

    def get_after_attack_message(self, locale):
        return locale.translate(spell_messages[22]).format(
            self.attack_character.name,
            self.damage,
            smarty.apply_hp_colour(self.attack_character.health, self.attack_character.full_health),
            self.who_character.name,
            self.experience,
            self.who_character.experience)

    def get_message(self, locale):
        return locale.translate(spell_messages[21]).format(
            self.who_character.name,
            self.whom_character.name,
            self.counter,
            self.duration,
            self.experience,
            self.who_character.experience)

class DirectDamageSpell(Spell):
    def init_internal(self, spell_id, who_character, whom_character):
        super(DirectDamageSpell, self).init_internal(spell_id, who_character, whom_character)
        self.damage = 0

    def process(self, percent):
        self.experience = 0
        self.damage = smarty.get_spell_damage(self.who_character, percent, self.spell_info.base_amount, self.whom_character)
        if smarty.is_critical_magic_hit(self.who_character, self.whom_character):
            self.damage *= 1.5

        if self.who_character.name != self.whom_character.name:
            self.experience = smarty.get_experience_for_spell_damage(self.damage)
        self.whom_character.health -= self.damage

class FrostNeedleSpell(DirectDamageSpell):
    def init(self, who_character, whom_character):
        super(FrostNeedleSpell, self).init_internal(spells[build_id(14, 0)], who_character, whom_character)

    def get_message(self, locale):
        return locale.translate(spell_messages[6]).format(
            self.who_character.name,
            locale.translate(self.spell_info.name),
            self.whom_character.name,
            self.damage,
            smarty.apply_hp_colour(self.whom_character.health, self.whom_character.full_health),
            self.experience,
            self.who_character.experience)

class FireSparkSpell(DirectDamageSpell):
    def init(self, who_character, whom_character):
        super(FireSparkSpell, self).init_internal(spells[build_id(14, 1)], who_character, whom_character)

    def get_message(self, locale):
        return locale.translate(spell_messages[7]).format(
            self.who_character.name,
            locale.translate(self.spell_info.name),
            self.whom_character.name,
            self.damage,
            smarty.apply_hp_colour(self.whom_character.health, self.whom_character.full_health),
            self.experience,
            self.who_character.experience)

class LeechLifeSpell(DirectDamageSpell):
    def init(self, who_character, whom_character):
        super(LeechLifeSpell, self).init_internal(spells[build_id(16, 1)], who_character, whom_character)

    def process(self, percent):
        self.experience = 0
        self.damage = smarty.get_spell_damage(self.who_character, percent, self.spell_info.base_amount, self.who_character)
        if smarty.is_critical_magic_hit(self.who_character, self.whom_character):
            self.damage *= 1.5

        self.whom_character.health -= self.damage
        self.who_character.health += self.damage

        if self.who_character.name != self.whom_character.name:
            if self.whom_character.health <= 0 and not self.whom_character.killer_name:
                self.whom_character.killer_name = self.who_character.name
            self.experience = smarty.get_experience_for_spell_damage(self.damage)

    def get_message(self, locale):
        return locale.translate(spell_messages[19]).format(
            self.who_character.name,
            locale.translate(self.spell_info.name),
            self.whom_character.name,
            self.damage,
            smarty.apply_hp_colour(self.whom_character.health, self.whom_character.full_health),
            self.damage,
            smarty.apply_hp_colour(self.who_character.health, self.who_character.full_health),
            self.experience,
            self.who_character.experience)

class DirectHealSpell(Spell):
    def init_internal(self, spell_id, who_character, whom_character):
        super(DirectHealSpell, self).init_internal(spell_id, who_character, whom_character)
        self.heal = 0

    def is_hit(self, percent):
        if random.uniform(0.5, 0.8) < percent + max(self.who_character.level - 4, 1)/10:
            return True
        return False

    def process(self, percent):
        heal = smarty.get_heal(self.who_character, percent, self.spell_info.base_amount, self.whom_character)
        if smarty.is_critical_magic_hit(self.who_character, self.whom_character):
            self.heal *= 1.5

        self.heal = min(self.whom_character.health + heal, self.whom_character.full_health) - self.whom_character.health
        self.whom_character.health += self.heal

        self.experience = smarty.get_experience_for_spell_heal(self.heal)

class PrayerForHealthSpell(DirectHealSpell):
    def init(self, who_character, whom_character):
        super(PrayerForHealthSpell, self).init_internal(spells[build_id(15, 1)], who_character, whom_character)

    def get_message(self, locale):
        return locale.translate(spell_messages[8]).format(
            self.who_character.name,
            locale.translate(self.spell_info.name),
            self.whom_character.name,
            self.heal,
            smarty.apply_hp_colour(self.whom_character.health, self.whom_character.full_health),
            self.experience,
            self.who_character.experience)

spell_range = 100

build_id = lambda type, id: spell_range*type + id
# means that 1000-1099 are warrior spells, 1100-1199 are guardian spells, 2100-2199 are archer spells, etc.
spells = {
    #warrior
    build_id(10, 0) : SpellInfo(build_id(10, 0), _("Berserk Fury"),             0, 4, True, 1, 0, 1, 15, _("Howling with rage, you rush to the enemy. Attack power is increased")),
    build_id(10, 1) : SpellInfo(build_id(10, 1), _("Disarmament"),              0, 5, False, 1, 0, 1, 15, _("You knock weapons out of enemy hands. He can not attack")),
    # guardian
    build_id(11, 0) : SpellInfo(build_id(11, 0), _("Armor"),                    1, 4, True, 1, 0, 5, 15, _("Armor becomes heavier and stronger. It is difficult to break it")),
    build_id(11, 1) : SpellInfo(build_id(11, 1), _("Shield Block"),             1, 4, True, 1, 0, 5, 15, _("You place the shield in front of you. You should have shield to do that")),
    # archer
    build_id(12, 0) : SpellInfo(build_id(12, 0), _("Dodge"),                    2, 3, True, 1, 0, 5, 15, _("It's hard to hit you as you are ready to dodge")),
    build_id(12, 1) : SpellInfo(build_id(12, 1), _("Fierce Shot"),              2, 4, True, 1, 0, 1, 15, _("You put all your rage in this shot. Tou should have a bow to do that")),
    # rogue
    build_id(13, 0) : SpellInfo(build_id(13, 0), _("Evasion"),                  3, 3, True, 1, 0, 5, 15, _("It's hard to hit you as you are doing a series of deviations")),
    build_id(13, 1) : SpellInfo(build_id(13, 1), _("Back Heel"),                3, 4, False, 1, 0, 5, 15, _("You make a back heel to a player, reducing his ability of protection")),
    # mage
    build_id(14, 0) : SpellInfo(build_id(14, 0), _("Frost Needle"),             4, 1, False, 1, 1.5, 1, 15, _("You are sending an frost needle at the enemy. Ice damage")),
    build_id(14, 1) : SpellInfo(build_id(14, 1), _("Fire Spark"),               4, 1, False, 1, 2.5, 1, 15, _("You are sending an fire spark at the enemy. Fire damage")),
    build_id(14, 2) : SpellInfo(build_id(14, 2), _("Phantoms"),                 4, 3, True, 1, 0, 1, 15, _("You round yourself with phantoms. They could be attacked instead of you")),
    build_id(14, 3) : SpellInfo(build_id(14, 3), _("Mirror Charm"),             4, 6, False, 1, 0, 1, 15, _("Place a mirror charm on player and each of his attackers will receive reflected damage")),
    # priest
    build_id(15, 0) : SpellInfo(build_id(15, 0), _("Prayer for Attack"),        5, 4, False, 1, 0, 1, 15, _("Your prayer increases attack of player")),
    build_id(15, 1) : SpellInfo(build_id(15, 1), _("Prayer for Health"),        5, 2, False, 1, 2, 1, 15, _("Your prayer heals player")),
    build_id(15, 2) : SpellInfo(build_id(15, 2), _("Prayer for Protection"),    5, 4, False, 1, 0, 5, 15, _("Your prayer increases protection of player")),
    # warlock
    build_id(16, 0) : SpellInfo(build_id(16, 0), _("Curse of Weakness"),        6, 4, False, 1, 0, 5, 15, _("Your curse make player weak. His attack is reduced")),
    build_id(16, 1) : SpellInfo(build_id(16, 1), _("Leech Life"),               6, 1, False, 1, 2, 5, 15, _("You steal some amount of health of player and adds them to yourself")),
    # necromancer
    build_id(17, 0) : SpellInfo(build_id(17, 0), _("Infection"),                7, 4, False, 1, 1.5, 5, 15, _("You infect player. Some damage will be done to him every round")),
    build_id(17, 1) : SpellInfo(build_id(17, 1), _("Stench"),                   7, 6, False, 1, 1.5, 5, 15, _("You surround the player with a stench. Every attacker will recieve some damage"))
}

spells_action_classes = {
    build_id(10, 0) : BerserkFurySpell,
    build_id(10, 1) : DisarmamentSpell,
    build_id(11, 0) : ArmorSpell,
    build_id(11, 1) : ShieldBlockSpell,
    build_id(12, 0) : DodgeSpell,
    build_id(12, 1) : FierceShotSpell,
    build_id(13, 0) : EvasionSpell,
    build_id(13, 1) : BackHeelSpell,
    build_id(14, 0) : FrostNeedleSpell,
    build_id(14, 1) : FireSparkSpell,
    build_id(14, 2) : PhantomsSpell,
    build_id(14, 3) : MirrorCharmSpell,
    build_id(15, 0) : PrayerForAttackSpell,
    build_id(15, 1) : PrayerForHealthSpell,
    build_id(15, 2) : PrayerForProtectionSpell,
    build_id(16, 0) : CurseOfWeaknessSpell,
    build_id(16, 1) : LeechLifeSpell,
    build_id(17, 0) : InfectionSpell,
    build_id(17, 1) : StenchSpell
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