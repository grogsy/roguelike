from random import randint
import tcod
from enemies import create_enemy

from .tile import Door, Tunnel

def place_enemy(x, y, entities):
    if randint(0, 100) < 80:
        # 80% chance for an orc to spawn
        enemy = create_enemy('orc', x, y, loot_chance=2)
    else:
        # 20% chance for a troll to spawn
        enemy = create_enemy('troll', x, y, loot_chance=5)

    entities.append(enemy)

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