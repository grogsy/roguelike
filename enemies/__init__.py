import random

from entities.actors import Enemy

from components.fighter import Fighter
from components.inventory import Inventory

from items.util import generate_random_scroll, generate_random_potion, generate_random_projectile, generate_gold

from .enemies import enemies, fighters

def create_enemy(enemy_name, *args, **kwargs):
    loot_chance = kwargs.pop('loot_chance', 0)
    fighter_values = fighters[enemy_name]

    kwargs.update(enemies[enemy_name])

    enemy = Enemy(
        *args,
        **kwargs,
        fighter=Fighter(**fighter_values),
        inventory=Inventory(20)
    )
    generate_enemy_inventory(enemy, loot_chance)
    return enemy

def generate_enemy_inventory(enemy, loot_chance=0):
    if not loot_chance:
        return

    for i in range(enemy.soft_max_inventory):
        if random.randint(1, 10) < loot_chance:
            random_item = random.choice([generate_random_projectile(), generate_random_scroll(), generate_random_potion(), generate_gold()])
            enemy.inventory.append(random_item)