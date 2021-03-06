import random
import tcod

from game_messages import message
from components.util import has_equip

class Buff:
    def __init__(self, effect, duration, expire_message, name):
        self.name = name
        self.effect = effect
        self.duration = duration
        self.expire_message = expire_message

    @property
    def expired(self):
        return self.duration <= 0

    def __repr__(self):
        return f"<Buff {self.name}, duration{self.duration}>"

class BuffCollection:
    def __init__(self):
        self.attack_buffs = {}
        self.defense_buffs = {}

    def remove_attack_buff(self, buff_name):
        del self.attack_buffs[buff_name]

    def add_attack_buff(self, buff):
        self.attack_buffs[buff.name] = buff

    def update_buff_counter(self):
        results = []
        attack_buffs_to_remove = []
        for buff_name in self.attack_buffs:
            buff = self.attack_buffs[buff_name]
            buff.duration -= 1
            if buff.expired:
                results.append({ 'message': buff.expire_message })
                attack_buffs_to_remove.append(buff_name)

        for buff_name in attack_buffs_to_remove:
            self.remove_attack_buff(buff_name)
            
        return results

    @property
    def buffs(self):
        return self.attack_buffs.update(self.defense_buffs)
        

class Fighter:
    '''
    A fighter component which some entities utilize to engage in combat.
    '''

    def __init__(self, hp, power, defense, constitution, strength, intelligence, dexterity, mana=0, xp=0):
        self.base_hp = hp
        self.base_hp_regen = 1
        self.base_hp_regen_rate = 15
        self.base_mana = mana
        self.base_mana_regen = 1
        self.base_mana_regen_rate = 20

        self.mana = self.base_mana + int(1.4 * intelligence)
        self.hp = self.base_hp + int(3.3 * constitution)

        self.constitution = constitution
        self.strength = strength
        self.intelligence = intelligence
        self.dexterity = dexterity

        self.base_power = power
        self.base_defense = defense

        self.buffs = BuffCollection()

        self.xp = xp

    @property
    def power_modifier(self):
        return int(1.25 * self.strength)

    @property
    def max_hp(self):
        return self.base_hp + int(3.3 * self.constitution)

    @property
    def max_mana(self):
        return self.base_mana + int(1.4 * self.intelligence)

    @property
    def power(self):
        power = self.base_power + self.power_modifier + self.calculate_attack_bonus_from_buffs()
        try:
            power += self.owner.equipment.power_bonus
        except AttributeError:
            pass
        
        return power

    @property
    def defense(self):
        defense = self.base_defense + int(0.35 * self.dexterity)
        try:
            defense  += self.owner.equipment.defense_bonus
        except AttributeError:
            pass

        return defense

    @property
    def hp_regen_tick(self):
        return self.base_hp_regen + int(0.35 * self.constitution)

    @property
    def mp_regen_tick(self):
        return self.base_mana_regen + int(0.45 * self.intelligence)

    @property
    def all_stats(self):
        return {
            'Health': self.max_hp,
            'Defense': self.base_defense,
            'Attack Power': self.base_power + self.power_modifier
            # 'Constitution': self.constitution,
            # 'Strength': self.strength,
            # 'Intelligence': self.intelligence,
            # 'Dexterity': self.dexterity
        }

    def perform_accuracy_check(self, other):
        # https://nethackwiki.com/wiki/To-hit
        roll = 1
        str_and_dex = self.strength + self.dexterity
        if str_and_dex >= 8:
            roll += 3
        elif str_and_dex >= 5:
            roll += 3
        elif str_and_dex >= 3:
            roll += 2
        else:
            roll -= 1

        # print(f'str and dex:{self.owner.name} ',  roll)
        
        if self.owner._level - other._level >= 4:
            roll += 3
        elif self.owner._level - other._level >= 2:
            roll += 2
        elif self.owner._level - other._level <= -2:
            roll -= 1

        # print(f'level diff: {self.owner.name} ', roll)
        
        if self.dexterity - other.fighter.dexterity >= 3:
            roll += 2
        elif self.dexterity - other.fighter.dexterity >= 1:
            roll += 1
        elif self.dexterity - other.fighter.dexterity <= -2:
            roll -= 1

        # print(f'dex diff: {self.owner.name} ', roll)

        return roll

    def take_damage(self, amount, dmg_type='physical'):
        results = []
        self.hp -= amount

        if self.hp <= 0:
            results.append(message(dead=self.owner, xp=self.xp, cause=dmg_type))

        return results

    def calculate_attack_bonus_from_buffs(self):
        bonus = 0
        buffs_to_remove = []
        messages = []
        for attack_buff in self.buffs.attack_buffs:
            buff = self.buffs.attack_buffs[attack_buff]
            if not buff.expired:
                bonus += buff.effect
        
        return bonus

    def attack(self, target):
        results = []

        # https://nethackwiki.com/wiki/To-hit
        accuracy = self.perform_accuracy_check(target)
        d8 = random.randint(1, 8)
        if d8 <= accuracy:
            # calculated_power = self.power + calculated_increased_attack_bonus
            damage = self.power - target.fighter.defense

            if damage > 0:
                results.append(message(message=f"{self.owner.name} attacks {target.name} and deals {damage} damage."))
                results.extend(target.take_damage(damage))
            else:
                results.append(message(message=f"{self.owner.name} attacks {target.name} but does not damage."))
        else:
            results.append(message(message=f"{self.owner.name} attacks {target.name}, but misses."))

        results.append(message(perform_attack=True, source=self.owner, acc=accuracy, match=d8))

        return results
        
    def update_mana_regen(self):
        if self.owner.turn_count % self.base_mana_regen_rate == 0 and self.mana < self.max_mana:
            self.mana += self.mp_regen_tick

    def update_hp_regen(self):
        if self.owner.turn_count % self.base_hp_regen_rate == 0 and self.hp < self.max_hp:
            self.hp += self.hp_regen_tick
        if self.hp > self.max_hp:
            self.hp = self.max_hp

    def update_regens(self):
        self.update_mana_regen()
        self.update_hp_regen()