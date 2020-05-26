from game_messages import message

from .entities import get_blocking_entities_at_location, is_enemy
from .identity import is_door, is_item, is_container
from .misc import is_on_same_tile
from .level import create_new_floor, save_current_floor, load_previous_floor

def handle_player_move(player, move, entities, game_map, fov_map):
    dx, dy = move
    dst_x = player.x + dx
    dst_y = player.y + dy

    target = get_blocking_entities_at_location(entities, dst_x, dst_y)
    tile = game_map.tiles[dst_x][dst_y]

    results = []

    if is_enemy(target):
        attack_results = player.attack(target)
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

def handle_player_take_stairs(console, game_map, player, entities, stairs):
    results = []
    old_level              = game_map.dungeon_level
    game_map.dungeon_level = stairs.level

    if stairs.level >= len(game_map.floors) + 1:
        create_new_floor(console, game_map, player, entities)
    else:
        load_previous_floor(console, game_map, player, entities, old_level, stairs.level)

    results.append(message(message="You take the stairs."))

    return results