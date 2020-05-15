import random

import tcod

from game_messages import Message

class Buff:
    def __init__(self, effect, duration, expire_message, name):
        self.name = name
        self.effect = effect
        self.duration = duration
        self.expire_message = expire_message

    @property
    def expired(self):
        return self.duration <= 0

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
    def __init__(self, hp, defense, power, accuracy, mana=0):
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

    @property
    def all_stats(self):
        power = self.power + self.calculate_attack_bonus_from_buffs()['bonus']
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
            results.append({
                'dead': self.owner,
                'cause': dmg_type
            })

        return results

    def calculate_attack_bonus_from_buffs(self):
        bonus = 0
        buffs_to_remove = []
        messages = []
        for attack_buff in self.buffs.attack_buffs:
            buff = self.buffs.attack_buffs[attack_buff]
            if not buff.expired:
                bonus += buff.effect
                buff.duration -= 1
            else:
                buffs_to_remove.append(attack_buff)
        
        for buff in buffs_to_remove:
            messages.append({'message': self.buffs.attack_buffs[buff].expire_message})
            self.buffs.remove_attack_buff(buff)

        return {
            'messages': messages,
            'bonus': bonus
        }

    def attack(self, target):
        results = []
        calculated_increased_attack_bonus = self.calculate_attack_bonus_from_buffs()

        if random.randint(0, 100) <= self.accuracy:
            calculated_power = self.power + calculated_increased_attack_bonus['bonus']
            damage = calculated_power - target.fighter.defense

            if damage > 0:
                results.append({ 
                    'message': Message(f"{self.owner.name} attacks {target.name} and deals {damage} damage.", tcod.white)
                })

                results.extend(target.fighter.take_damage(damage))
            else:
                results.append({
                    'message' : Message(f"{self.owner.name} attacks {target.name} but does not damage.", tcod.white)
                })
        else:
            results.append({
                'message': Message(f"{self.owner.name} attacks {target.name}, but misses.", tcod.white)
            })

        results.extend(calculated_increased_attack_bonus['messages'])
            
        return results
        
    def update_mana_regen(self, turn_count):
        if turn_count % self.base_mana_regen_rate == 0 and self.mana < self.max_mana:
            self.mana += self.base_mana_regen