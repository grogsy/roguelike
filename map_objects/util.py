from random import randint, choice
import tcod
from entities.inanimate import create_chest
from enemies import create_enemy

from .tile import Door, Tunnel, Stairs

def place_enemy(x, y, entities):
    if randint(0, 100) < 80:
        # 80% chance for a weakling to spawn
        random_enemy_name = choice('orc bat rat kobold'.split(' '))
        # enemy = create_enemy(random_enemy_name, x, y, loot_chance=2)
        enemy = create_enemy('orc', x, y, loot_chance=2)
    else:
        # 20% chance for a troll to spawn
        enemy = create_enemy('troll', x, y, loot_chance=5)

    entities.append(enemy)

def place_chest(x, y, entities):
    entities.append(create_chest(x, y))

def is_stairs(tile):
    return isinstance(tile, Stairs)

def is_door(tile):
    return isinstance(tile, Door)

def is_tunnel(tile):
    return isinstance(tile, Tunnel)

def create_door(game_map, x, y, orientation):
    game_map.tiles[x][y] = Door(orientation, True, x, y)

def create_tunnel(game_map, x, y):
    game_map.tiles[x][y] = Tunnel(False, x, y)

def entity_can_move_to_tile(tile):
    return not tile.blocked or is_door(tile)