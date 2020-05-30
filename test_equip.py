import tcod
from entities.items import Equipable

sword = {
    'name': 'Sword',
    'char': '/',
    'color': tcod.silver,
    'slot': 'main_hand',
    'power_bonus': 7,
    'max_hp_bonus': 1
}

sword = Equipable(0, 0, **sword)

print(sword, sword.equip_slot, sword.color, sword.char, sword.power_bonus, sword.defense_bonus)