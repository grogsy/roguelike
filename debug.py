import random
import tcod

from entities.items import Scroll, Potion, Projectile, Book, Guld

from items import items

def label_rooms(console, game_map):
    for i, room in enumerate(game_map.rooms):
        x, y = room.center()        
        label = chr(65 + i)

        tcod.console_set_default_foreground(console, tcod.white)
        tcod.console_put_char(console, x, y, label, flag=tcod.BKGND_NONE)

def generate_level(game_map, settings):
    game_map.tiles = game_map.initialize_tiles()
    game_map.make_map(**settings)

def clear_labels(console, game_map):
    for room in game_map.rooms:
        x, y = room.center()
        tcod.console_put_char(console, x, y, ' ', flag=tcod.BKGND_NONE)

def print_player_status(player):
    print(f"Player health: {player.fighter.hp}/{player.fighter.max_hp}")

def give_items(player):
    player.inventory.items.append((Potion(0, 0, **items.potion_of_healing)))
    player.inventory.items.append((Potion(0, 0, **items.potion_of_mana)))
    player.inventory.items.append((Scroll(0, 0, **items.scroll_of_fireball)))
    player.inventory.items.append((Scroll(0, 0, **items.scroll_of_lightning)))
    player.inventory.items.append((Scroll(0, 0, **items.scroll_of_confuse_monster)))
    player.inventory.items.append((Scroll(0, 0, **items.scroll_of_strength)))
    player.inventory.items.append((Scroll(0, 0, **items.scroll_of_magic_mapping)))
    player.inventory.items.append((Scroll(0, 0, **items.scroll_of_teleport)))
    player.inventory.items.append((Projectile(0, 0, stack_count=random.randint(1, 10), **items.throwing_knife)))
    player.inventory.items.append((Projectile(0, 0, stack_count=random.randint(1, 10), **items.throwing_dagger)))
    player.inventory.items.append((Book(0, 0, **items.magic_missile_book)))
    player.inventory.items.append((Book(0, 0, **items.aoe_sleep_book)))
    # player.inventory.add_item(Guld(0, 0, stack_count=random.randint(30, 1500)))