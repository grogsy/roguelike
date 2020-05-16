import random
from queue import deque

import tcod

from util import is_on_same_tile

from input_handlers import handle_keys, handle_mouse

from entity import Entity, Enemy, Item, get_blocking_entities_at_location

from components.fighter import Fighter
from components.inventory import Inventory
from map_objects import GameMap, Door

from game_messages import Message, MessageLog
from ui import RootConsole
from colors import Colors

from game_state import GameStates, RenderOrder
from fov_functions import initialize_fov, recompute_fov, FOV_Map

from log import GameLog
from debug import generate_level, give_items

from constants import INVENTORY_CONTEXT

def main():
    screen_width = 100
    screen_height = 70
    
    map_width = 100
    map_height = 50

    console = RootConsole('arial10x10.png', screen_width, screen_height, map_height)

    # create some entities
    player = Entity(
        0, 0,
        '@', Colors.player, 'Player', 
        render_order=RenderOrder.ACTOR,
        fighter=Fighter(hp=30, mana=30, defense=2, power=5, accuracy=100),
        inventory=Inventory(capacity=26)
    )
    player.stat_logger = GameLog(parent=console, width=50)


    # DEBUG
    give_items(player)
    
    entities = [player]

    # a possible refactorization of the entities container.
    # this would be useful if picking up items off the ground for example.
    # we can access items by way of their id.
    # deleting a specific entry for an item can be done as del entities['items'][item.id]
    # entities = {
    #     'sentients': {},
    #     'items': {}
    # }

    # initialize a game map object
    game_map = GameMap(map_width, map_height)
    game_map.make_map(player, entities)

    # initialize field-of-view map
    fov_map = FOV_Map(game_map)

    # initialize input objects
    key = tcod.Key()
    mouse = tcod.Mouse()

    # initialize game state
    game_state = GameStates.PLAYER_TURN
    prev_game_state = game_state

    targeting_item = None
    player.targeting_x = 0
    player.targeting_y = 0

    TURN_COUNT = 1

    while not tcod.console_is_window_closed():
        # capture user input, this modifies the input objects(key and mouse) defined above
        tcod.sys_check_for_event(tcod.EVENT_KEY_PRESS | tcod.EVENT_MOUSE, key, mouse)

        if fov_map.recompute:
            fov_map.recompute_fov(player.x, player.y)

        console.render_all(player, entities, game_map, fov_map, mouse, game_state)

        # field-of-view only needs to be re-rendered if player character is moving
        fov_map.recompute = False

        console.clear_all(entities, game_map, game_state)

        # get user actions
        action = handle_keys(key, game_state)
        mouse_action = handle_mouse(mouse)

        move                    = action.get('move')
        pickup                  = action.get('pickup')
        show_inventory          = action.get('show_inventory')
        selected_item           = action.get('inventory_index')
        select_readable         = action.get('select_readable')
        select_projectile       = action.get('select_projectile')
        select_quaffable        = action.get('select_quaffable')
        drop_inventory          = action.get('drop_inventory')
        exit                    = action.get('exit')
        fullscreen              = action.get('fullscreen')
        confirm_action          = action.get('confirm_action')
        check_stats             = action.get('check_player_status')
        view_stats              = action.get('view_stats')
        LEVEL_DEBUG             = action.get('generate_level')

        left_click = mouse_action.get('left_click')
        right_click = mouse_action.get('right_click')

        # store player turn action logs into a list
        player_turn_results = []

        if game_state == GameStates.PLAYER_TURN:
            if move:
                dx, dy = move
                dst_x = player.x + dx
                dst_y = player.y + dy

                target = get_blocking_entities_at_location(entities, dst_x, dst_y)

                if target or not game_map.is_blocked_by_tiling(dst_x, dst_y):
                    if target and isinstance(target, Enemy):
                        attack_results = player.fighter.attack(target)
                        player_turn_results.extend(attack_results)
                    elif target is None:
                        player.move(dx, dy)
                        fov_map.recompute = True

                    # plan to move this after door check, because considering door opening to consume a turn
                    player_turn_results.extend(player.update_buff_counter())
                    player.update_mana_regen(TURN_COUNT)
                    game_state = GameStates.ENEMY_TURN
                    TURN_COUNT += 1
                
                elif isinstance(game_map.tiles[dst_x][dst_y], Door):
                    door = game_map.tiles[dst_x][dst_y]
                    if not door.opened:
                        door.open()
                        if door.opened:
                            fov_map.modify_fov_at_tile(dst_x, dst_y, transparent=True, walkable=True)
                            player_turn_results.append({ 'message': Message('You open the door.', tcod.white) })
                        else:
                            player_turn_results.append({ 
                                'message': Message('You attempt to open the door, but it only budges slightly.', tcod.white)
                            })
            elif pickup:
                items_on_same_tile = [entity for entity in entities if isinstance(entity, Item) and (entity.x == player.x and entity.y == player.y)]
                # if its just one item, forego having to display a looting menu
                if len(items_on_same_tile) == 1:
                    item = items_on_same_tile[0]
                    pickup_results = player.inventory.add_item(item)
                    entities.remove(item)
                    player_turn_results.extend(pickup_results)
                    player.stat_logger.log_loot()
                else:
                    game_state = GameStates.LOOTING

        if game_state == GameStates.TARGETING:
            if targeting_item.use_effect.directional_targeting:
                if move:
                    dx, dy = move
                    item_result = player.use(targeting_item, user=player, game_map=game_map, fov_map=fov_map, entities=entities, dx=dx, dy=dy)
                    player_turn_results.extend(item_result)
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
                    item_result = player.use(targeting_item, user=player, entities=entities, fov_map=fov_map, target_x=target_x, target_y=target_y)
                    TURN_COUNT += 1
                    print(TURN_COUNT)
                    player_turn_results.extend(item_result)
                elif right_click:
                    player_turn_results.append({ 'targeting_cancelled': True })
        if game_state != GameStates.READABLE_INVENTORY and select_readable:
            prev_game_state = game_state
            game_state = GameStates.READABLE_INVENTORY
        if game_state != GameStates.QUAFFABLE_INVENTORY and select_quaffable:
            prev_game = game_state
            game_state = GameStates.QUAFFABLE_INVENTORY
        if game_state != GameStates.THROWABLE_INVENTORY and select_projectile:
            prev_game_state = game_state
            game_state = GameStates.THROWABLE_INVENTORY
        if game_state != GameStates.SHOW_INVENTORY and show_inventory:
            prev_game_state = game_state
            game_state = GameStates.SHOW_INVENTORY
        if game_state != GameStates.DROP_INVENTORY and drop_inventory:
            prev_game_state = game_state
            game_state = GameStates.DROP_INVENTORY
        # using/dropping/looting an item
        if selected_item is not None and prev_game_state != GameStates.PLAYER_DEAD and selected_item < len(console.inventory_context): #len(player.inventory.items):
            item = console.inventory_context[selected_item]
            if game_state == GameStates.SHOW_INVENTORY or game_state == GameStates.READABLE_INVENTORY or game_state == GameStates.THROWABLE_INVENTORY or game_state == GameStates.QUAFFABLE_INVENTORY:
                item_result = player.use(item, user=player, entities=entities, fov_map=fov_map, game_map=game_map, console=console)
                # if item requires targeting, use targeting game state context
                if item_result[0].get('requires_targeting'):
                    player.targeting_x = player.x
                    player.targeting_y = player.y
                    targeting_item = item_result[0].get('requires_targeting')
                    console.panel.message_log.add_message(targeting_item.use_effect.target_msg)
            elif game_state == GameStates.DROP_INVENTORY:
                item_result = player.drop_item(item)
                entities.append(item)
            elif game_state == GameStates.LOOTING:
                item_result = player.inventory.add_item(item)
                # remove the entity from the entities list since the player has picked it up
                entities.remove(item)
                player.stat_logger.log_loot()
            player_turn_results.extend(item_result)
            TURN_COUNT += 1

        if exit:
            if game_state in INVENTORY_CONTEXT:
                game_state = prev_game_state
            elif game_state == GameStates.TARGETING:
                player_turn_results.append({ 'targeting_cancelled': True })
            elif game_state in (GameStates.CHECK_PLAYER_STATS, GameStates.CHECK_CHAR_STATS):
                game_state = GameStates.PLAYER_TURN
            else:
                return True
        if fullscreen:
            tcod.console_set_fullscreen(not tcod.console_is_fullscreen())
        if game_state == GameStates.PLAYER_TURN and check_stats:
            game_state = GameStates.CHECK_PLAYER_STATS
        if view_stats:
            game_state = GameStates.CHECK_CHAR_STATS

        # drop enemy loot
        # for result in 
        

        next_game_state = console.panel.message_log.parse_turn_results(player_turn_results, entities, player.stat_logger)
        game_state = next_game_state if next_game_state is not None else game_state

        if game_state == GameStates.ENEMY_TURN:
            for e in entities:
                if isinstance(e, Enemy) and e.ai is not None and fov_map.is_in_fov(e.x, e.y):
                    enemy_turn_results = e.ai.take_turn(player, fov_map, game_map, entities)

                    game_state = console.panel.message_log.parse_turn_results(enemy_turn_results, entities)                    
                    if game_state == GameStates.PLAYER_DEAD:
                        break
            # else:
            #     game_state = GameStates.PLAYER_TURN
            if game_state != GameStates.PLAYER_DEAD:
                game_state = GameStates.PLAYER_TURN

        # LEVEL GEN DEBUG
        if LEVEL_DEBUG:

            entities = [player]

            settings = {
                'player': player,
                'entities': entities,
            }

            old_rooms = game_map.rooms
            console.clear_old_tiles(old_rooms)

            generate_level(game_map, settings)
            fov_map.fov_map = fov_map.initialize_fov(game_map)
            fov_map.recompute = True

            player.stat_logger.log_travel()

if __name__ == '__main__':
    main()