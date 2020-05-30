import tcod
from entities.items import EquipmentSlots

long_sword = {
    'name': 'Long Sword',
    'char': '/',
    'color': tcod.silver,
    'slot': EquipmentSlots.MAIN_HAND,
    'power_bonus': 4
}

wooden_shield = {
    'name': 'Wooden Shield',
    'char': '[',
    'color': tcod.brass,
    'slot': EquipmentSlots.OFF_HAND,
    'defense_bonus': 2
}

ring_of_protection = {
    'name': 'Ring of Protection',
    'char': '=',
    'color': tcod.darkest_grey,
    'slot': EquipmentSlots.RING,
    'defense_bonus': 1
}

# for the most part only for debugging purposes
equips = {
    'long_sword': long_sword,
    'wooden_shield': wooden_shield,
    'ring_of_protection': ring_of_protection
}