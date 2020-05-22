import random
from .items import *

from entities.items import Potion, Scroll, Projectile, Book, Guld, Item

def is_item(entity):
    return isinstance(entity, Item)

def generate_item_at_coord(x, y):
    item_chance = random.randint(0, 100)

    # 33% for a potion
    # 33% for a scroll
    # 25% for a throwing weapon
    #  8% for a spellbook

    if item_chance < 25:
        item = generate_random_potion(x, y)
    elif item_chance < 50:
        item = generate_random_scroll(x, y)
    elif item_chance < 75:
        item = generate_gold(x, y)
    elif item_chance < 95:
        item = generate_random_projectile(x, y)
    else:
        item = generate_random_book(x, y)

    return item

def generate_random_potion(x=0, y=0):
    item_chance = random.randint(0, 100)
    
    if item_chance < 25:
        item = Potion(x, y, **potion_of_mana)
    else:
        item = Potion(x, y, **potion_of_healing)

    return item

def generate_random_scroll(x=0, y=0):
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

def generate_random_projectile(x=0, y=0):
    item_chance = random.randint(0, 100)
    if item_chance <= 15:
        item = Projectile(x, y, stack_count=random.randint(1, 10), **throwing_dagger)
    else:
        item = Projectile(x, y, stack_count=random.randint(1, 10), **throwing_knife)


    return item

def generate_random_book(x=0, y=0):
    item_chance = random.randint(0, 100)

    if item_chance < 98:
        item = Book(x, y, **magic_missile_book)
    else:
        item = Book(x, y, **aoe_sleep_book)

    return item

def generate_gold(x=0, y=0, min_amount=1, max_amount=30):
    return Guld(x, y, stack_count=random.randint(min_amount, max_amount))

def generate_random_item():
    return random.choice([generate_random_projectile(), generate_random_scroll(), generate_random_potion(), generate_gold()])