from entities.actors import Player
from entities.util import get_blocking_entities_at_location, is_enemy

from map_objects.util import is_door
from map_objects.game_map import GameMap

from items.util import is_item

from components.fighter import Fighter
from components.inventory import Inventory

from colors import Colors

from game_messages import message

def is_on_same_tile(this, other):
    return this.x == other.x and this.y == other.y

def get_entity_at_coord(x, y, entities):
    for entity in entities:
        if entity.x == x and entity.y == y:
            return entity
    
    return None

def entity_on_tile(entity, x, y):
    return entity.x == x and entity.y == y

def is_same_entity_name(entity, other):
    return entity.name == other.name

def handle_player_move(player, move, entities, game_map, fov_map):
    dx, dy = move
    dst_x = player.x + dx
    dst_y = player.y + dy

    target = get_blocking_entities_at_location(entities, dst_x, dst_y)
    tile = game_map.tiles[dst_x][dst_y]

    results = []

    if is_enemy(target):
        attack_results = player.fighter.attack(target)
        results.extend(attack_results)
    elif is_door(tile):
        door = tile
        if not door.opened:
            results.extend(player.open(door, fov_map))
    
    if not target and not game_map.is_blocked_by_tiling(dst_x, dst_y):
        player.move(dx, dy)
        fov_map.recompute = True

    return results

def handle_player_pickup(player, entities):
    results = []

    items_on_same_tile = [entity for entity in entities if is_item(entity) and is_on_same_tile(entity, player)]
    # if its just one item, forego having to display a looting menu
    if not items_on_same_tile:
        results.append(message(message="There is nothing here to pick up."))
    elif len(items_on_same_tile) == 1:
        item = items_on_same_tile[0]
        pickup_results = player.loot(item)
        entities.remove(item)
        results.extend(pickup_results)
        player.stat_logger.log_loot()
    else:
        results.append(message(player_looting=True))

    return results

def create_player():
    return Player(
        0, 0,
        '@', Colors.player, 'Player', 
        fighter=Fighter(hp=30, mana=30, defense=2, power=5, accuracy=100),
        inventory=Inventory(capacity=26)
    )

def create_game_map(width, height, player, entities):
    game_map = GameMap(width, height)
    game_map.make_map(player, entities)

    return game_map