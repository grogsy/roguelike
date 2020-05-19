import tcod
from random import randint

from entities.actors import Enemy

from components.fighter import Fighter
from components.ai import BasicMonster
from components.inventory import Inventory

from items.util import generate_enemy_inventory

def place_enemy(x, y, entities):
    if randint(0, 100) < 80:
        # 80% chance for an orc to spawn
        enemy = Enemy(
            x, y, 
            'o', tcod.desaturated_green, 'Orc',
            fighter=Fighter(hp=10, defense=0, power=3, accuracy=35),
            # just giving it a random inventory size
            inventory=Inventory(20)
        )
        for i in range(enemy.soft_max_inventory):
            loot_chance = randint(1, 10) < 3
            if loot_chance:
                enemy.inventory.append(generate_enemy_inventory())
    else:
        # 20% chance for a troll to spawn
        enemy = Enemy(
            x, y, 
            'T', tcod.darker_green, 'Troll',
            fighter=Fighter(hp=16, defense=1, power=4, accuracy=50),
            inventory=Inventory(20)
        )
        for i in range(enemy.soft_max_inventory):
            loot_chance = randint(1, 10) < 4
            if loot_chance:
                enemy.inventory.append(generate_enemy_inventory())

    entities.append(enemy)