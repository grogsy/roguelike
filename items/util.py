import random
from .items import *
from entity import Potion, Scroll, Projectile, Book

def generate_item_at_coord(x, y):
    item_chance = random.randint(0, 100)

    # 33% for a potion
    # 33% for a scroll
    # 25% for a throwing weapon
    #  8% for a spellbook

    if item_chance < 33:
        item = generate_random_potion(x, y)
    elif item_chance < 66:
        item = generate_random_scroll(x, y)
    elif item_chance < 92:
        item = generate_random_projectile(x, y)
    else:
        item = generate_random_book(x, y)

    return item

def generate_random_potion(x, y):
    item_chance = random.randint(0, 100)
    
    if item_chance < 25:
        item = Potion(x, y, **potion_of_mana)
    else:
        item = Potion(x, y, **potion_of_healing)

    return item

def generate_random_scroll(x, y):
    common = [
        scroll_of_confuse_monster,
        scroll_of_fireball,
        scroll_of_teleport
    ]

    uncommon = [
        scroll_of_lightning,
        scroll_of_magic_mapping,
        scroll_of_strength,
    ]

    item_chance = random.randint(0, 100)

    if item_chance < 40:
        item = random.choice(uncommon)
    else:
        item = random.choice(common)

    return Scroll(x, y, **item)

def generate_random_projectile(x, y):
    item_chance = random.randint(0, 100)
    if item_chance <= 15:
        item = Projectile(x, y, stack_count=random.randint(1, 10), **throwing_dagger)
    else:
        item = Projectile(x, y, stack_count=random.randint(1, 10), **throwing_knife)

    print(item_chance, item)

    return item

def generate_random_book(x, y):
    item_chance = random.randint(0, 100)

    if item_chance < 98:
        item = Book(x, y, **magic_missile_book)
    else:
        item = Book(x, y, **aoe_sleep_book)

    return item

def generate_enemy_inventory():
    '''
    placeholder function 
    '''
    return Potion(0, 0, **potion_of_healing)