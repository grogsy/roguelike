from entities.actors import Player
from entities.inanimate import is_container
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
    if not items_on_same_tile:
        # if there are not items on the ground, maybe there's a container?
        for entity in entities:
            if is_container(entity) and is_on_same_tile(entity, player):
                results.append(message(player_looting=True, looting_container=True, source=entity))
                break
        else:
            results.append(message(message="There is nothing here to pick up."))
    # if its just one item, forego having to display a looting menu
    elif len(items_on_same_tile) == 1:
        item = items_on_same_tile[0]
        pickup_results = player.loot(item)
        entities.remove(item)
        results.extend(pickup_results)
        player.stat_logger.log_loot()
    else:
        results.append(message(player_looting=True, source=f"Ground({player.x}, {player.y})"))

    return results

def handle_player_targeting(player, targeting_item, *args, **kwargs):
    move            = kwargs.get('move')
    left_click      = kwargs.get("left_click")
    confirm_action  = kwargs.get('confirm_action')
    right_click     = kwargs.get('right_click')

    results = []
    
    if targeting_item.use_effect.directional_targeting:
        if move:
            dx, dy = move
            item_result = player.use(targeting_item, **kwargs, dx=dx, dy=dy)
            results.extend(item_result)
    else:
        if move:
            dx, dy = move
            player.targeting_x += dx
            player.targeting_y += dy
        if left_click or confirm_action:
            if left_click:
                target_x, target_y = left_click
            elif confirm_action:
                target_x, target_y = player.targeting_x, player.targeting_y
            item_result = player.use(targeting_item, **kwargs, target_x=target_x, target_y=target_y)
            results.extend(item_result)
        elif right_click:
            results.append(message(targeting_cancelled=True))

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

def create_new_floor(console, game_map, player, entities):
    console.clear_old_tiles(game_map)

    game_map.tiles = game_map.initialize_tiles()
    game_map.make_map(player, entities)

def load_previous_floor(console, game_map, player, entities, curr_level, prev_level):
    next_floor = game_map.floors[prev_level - 1]
    entities.extend(next_floor.entities)

    console.clear_old_tiles(game_map)

    game_map.tiles = next_floor.tiles

    # if we're going DOWN to prev visited floor
    if curr_level < prev_level:
        player.x = next_floor.upstair_x
        player.y = next_floor.upstair_y
    # if we're going UP to prev visited floor
    else:
        player.x = next_floor.downstair_x
        player.y = next_floor.downstair_y

def save_current_floor(game_map, entities):
    this_floor = game_map.floors[game_map.dungeon_level - 1]
    this_floor.tiles = game_map.tiles
    this_floor.entities = entities

def handle_player_take_stairs(console, game_map, player, entities, stairs):
    old_level              = game_map.dungeon_level
    game_map.dungeon_level = stairs.level

    if stairs.level >= len(game_map.floors) + 1:
        create_new_floor(console, game_map, player, entities)
    else:
        load_previous_floor(console, game_map, player, entities, old_level, stairs.level)