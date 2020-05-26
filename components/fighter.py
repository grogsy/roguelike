import random

import tcod

from game_messages import message

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
    def __init__(self, hp, defense, power, accuracy, mana=0, xp=0):
        self.max_hp = hp
        self.hp = hp

        self.mana = mana
        self.max_mana = mana
        self.base_mana_regen = 1
        self.base_mana_regen_rate = 20 # rate is in term of player turns

        self.defense = defense
        self.power = power
        self.accuracy = accuracy
        self.buffs = BuffCollection()

        self.xp = xp

    @property
    def all_stats(self):
        power = self.power + self.calculate_attack_bonus_from_buffs()
        return {
            'Health': self.max_hp,
            'Defense': self.defense,
            'Attack Power': power,
            'Hit Chance': self.accuracy
        }

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
        calculated_increased_attack_bonus = self.calculate_attack_bonus_from_buffs()

        if random.randint(0, 100) <= self.accuracy:
            calculated_power = self.power + calculated_increased_attack_bonus
            damage = calculated_power - target.fighter.defense

            if damage > 0:
                results.append(message(message=f"{self.owner.name} attacks {target.name} and deals {damage} damage."))
                results.extend(target.take_damage(damage))
            else:
                results.append(message(message=f"{self.owner.name} attacks {target.name} but does not damage."))
        else:
            results.append(message(message=f"{self.owner.name} attacks {target.name}, but misses."))

        for res in results:
            xp_amt = res.get('xp')
            if xp_amt and self.owner.__class__.__name__ == 'Player':
                results.extend(self.owner.gain_xp(xp_amt))


        return results
        
    def update_mana_regen(self):
        if self.owner.turn_count % self.base_mana_regen_rate == 0 and self.mana < self.max_mana:
            self.mana += self.base_mana_regen