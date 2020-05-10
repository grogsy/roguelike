import random

import tcod

from game_messages import Message

class Fighter:
    '''
    A fighter component which some entities utilize to engage in combat.
    '''
    def __init__(self, hp, defense, power, accuracy):
        self.max_hp = hp
        self.hp = hp
        self.defense = defense
        self.power = power
        self.accuracy = accuracy

    def take_damage(self, amount, dmg_type='physical'):
        results = []
        self.hp -= amount

        if self.hp <= 0:
            results.append({
                'dead': self.owner,
                'cause': dmg_type
            })

        return results

    def attack(self, target):
        results = []

        if random.randint(0, 100) <= self.accuracy:
            damage = self.power - target.fighter.defense

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
            
        return results
        
