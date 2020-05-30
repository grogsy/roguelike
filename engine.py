import tcod

from constants import INVENTORY_CONTEXT
from saves import save_game, load_game
from game_state import GameStates
from game_messages import message

from util.create import (
    create_game_map, create_player, create_root_console, create_fov_map,
    create_menu
)
from util.player_action import (
    handle_player_move, handle_player_pickup, 
    handle_player_targeting, handle_player_take_stairs,
    handle_player_level_up
)
from util.entities import is_enemy, is_alive
from util.identity import is_item, is_stairs
from util.level import save_current_floor
from util.misc import show_equipped_items

from input_handlers import handle_keys, handle_mouse, handle_main_menu_keys
from log import GameLog

from debug import give_items

def play(console, player, entities, game_map, game_state):
    fov_map = create_fov_map(game_map)

    # initialize input objects
    key = tcod.Key()
    mouse = tcod.Mouse()

    # initialize game state
    game_state = GameStates.PLAYER_TURN
    prev_game_state = game_state

    targeting_item = None
    looting_container = None
    player.targeting_x = 0
    player.targeting_y = 0

    while not tcod.console_is_window_closed():
        # capture user input, this modifies the input objects(key and mouse) defined above
        tcod.sys_check_for_event(tcod.EVENT_KEY_PRESS | tcod.EVENT_MOUSE, key, mouse)

        if fov_map.recompute:
            fov_map.recompute_fov(player.x, player.y)

        console.render_all(player, entities, game_map, fov_map, mouse, game_state)

        if game_state in INVENTORY_CONTEXT:
            console.render_inventory(player, entities, game_state, container=looting_container)
        if game_state == GameStates.VIEW_EQUIP:
            show_equipped_items(console, player)

        if game_state == GameStates.PLAYER_LEVEL_UP:
            level_up_options = [
                '+1 CON',
                '+1 STR',
                '+1 INT',
                '+1 DEX'
            ]
            create_menu(console, 'Choose a stat to strengthen.', level_up_options)

        console.flush()

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
        wait                    = action.get('wait')
        take_stairs             = action.get('take_stairs')
        level_up                = action.get('level_up')
        equipping               = action.get('equipping')
        unequipping             = action.get('unequipping')
        view_equip              = action.get('view_equip')

        left_click = mouse_action.get('left_click')
        right_click = mouse_action.get('right_click')

        # store player turn action logs into a list
        player_turn_results = []

        if game_state == GameStates.PLAYER_TURN:
            if move:
                player_turn_results.extend(handle_player_move(player, move, entities, game_map, fov_map))
            elif pickup:
                pick_up_results = handle_player_pickup(player, entities)
                for result in pick_up_results:
                    if result.get('looting_container') and result.get('source') is not None:
                        looting_container = result.get('source')
                        break
                player_turn_results.extend(pick_up_results)
            elif wait:
                player_turn_results.extend(player.wait())

        if game_state == GameStates.TARGETING:
            kwargs = {
                'user':           player,
                'game_map':       game_map,
                'fov_map':        fov_map,
                'entities':       entities,
                'move':           move,
                'left_click':     left_click,
                'confirm_action': confirm_action
            }
            player_turn_results.extend(handle_player_targeting(player, targeting_item, **kwargs))
        if select_readable:
            game_state = GameStates.READABLE_INVENTORY
        if select_quaffable:
            game_state = GameStates.QUAFFABLE_INVENTORY
        if select_projectile:
            game_state = GameStates.THROWABLE_INVENTORY
        if show_inventory:
            game_state = GameStates.SHOW_INVENTORY
        if drop_inventory:
            game_state = GameStates.DROP_INVENTORY
        if equipping:
            game_state = GameStates.EQUIPABLE_INVENTORY
        if unequipping:
            game_state = GameStates.UNEQUIP
        # using/dropping/looting an item
        if selected_item is not None and prev_game_state != GameStates.PLAYER_DEAD and selected_item < len(console.inventory_context):
            item = console.inventory_context[selected_item]
            if game_state in (GameStates.SHOW_INVENTORY, GameStates.READABLE_INVENTORY, GameStates.THROWABLE_INVENTORY, GameStates.QUAFFABLE_INVENTORY):
                item_result = player.use(item, user=player, entities=entities, fov_map=fov_map, game_map=game_map, console=console)
                # if item requires targeting, use targeting game state context
                if item_result[0].get('requires_targeting'):
                    player.targeting_x = player.x
                    player.targeting_y = player.y
                    targeting_item = item_result[0].get('requires_targeting')
                    console.panel.message_log.add_message(targeting_item.use_effect.target_msg)
            elif game_state == GameStates.EQUIPABLE_INVENTORY:
                item_result = player.equip(item)
            elif game_state == GameStates.UNEQUIP:
                item_result = player.unequip(item)
            elif game_state == GameStates.DROP_INVENTORY:
                item_result = player.drop_item(item)
                entities.append(item)
            elif game_state == GameStates.LOOTING:
                item_result = player.loot(item)
                if looting_container:
                    looting_container.remove_item(item)
                    looting_container = None
                else:
                    # remove the entity from the entities list since the player has picked it up
                    entities.remove(item)
                player.stat_logger.log_loot()
            player_turn_results.extend(item_result)

        if exit:
            if game_state in INVENTORY_CONTEXT:
                game_state = GameStates.PLAYER_TURN
            elif game_state == GameStates.TARGETING:
                player_turn_results.append({ 'targeting_cancelled': True })
            elif game_state in (GameStates.CHECK_PLAYER_STATS, GameStates.CHECK_CHAR_STATS, GameStates.VIEW_EQUIP):
                game_state = GameStates.PLAYER_TURN
            else:
                save_game(player, entities, game_map, console.panel.message_log, game_state)
                return True
        if fullscreen:
            tcod.console_set_fullscreen(not tcod.console_is_fullscreen())
        if game_state == GameStates.PLAYER_TURN and check_stats:
            game_state = GameStates.CHECK_PLAYER_STATS
        if view_stats:
            game_state = GameStates.CHECK_CHAR_STATS
        if view_equip:
            game_state = GameStates.VIEW_EQUIP
        if level_up:
            player_turn_results.append(handle_player_level_up(player, level_up))
            game_state = GameStates.PLAYER_TURN

        if take_stairs and is_stairs(game_map.tiles[player.x][player.y]):
            stairs = game_map.tiles[player.x][player.y]
            save_current_floor(game_map, entities)
            entities = [player]

            if stairs.level != 0:
                player_turn_results.extend(handle_player_take_stairs(console, game_map, player, entities, stairs)) 
                fov_map.fov_map = fov_map.initialize_fov(game_map)
                fov_map.recompute = True

        next_game_state = console.panel.message_log.parse_turn_results(player_turn_results, player, entities, game_state, player.stat_logger)
        game_state = next_game_state if next_game_state is not None else game_state

        if game_state == GameStates.ENEMY_TURN:
            for e in entities:                     # enemy turn only occurs when they are in player field-of-view
                if is_alive(e) and is_enemy(e) and fov_map.is_in_fov(e.x, e.y):
                    enemy_turn_results = e.take_turn(player, fov_map, game_map, entities)

                    game_state = console.panel.message_log.parse_turn_results(enemy_turn_results, player, entities, game_state)
                    if game_state == GameStates.PLAYER_DEAD:
                        break
            if game_state != GameStates.PLAYER_DEAD:
                game_state = GameStates.PLAYER_TURN

def main():
    screen_width = 100
    screen_height = 70
    
    map_width = 100
    map_height = 50
    
    console = create_root_console('arial10x10.png', screen_width, screen_height, map_height)

    player = None
    entities = []
    game_map = None
    message_log = None
    game_state = None

    show_main_menu = True
    show_load_error_message = False

    key = tcod.Key()
    mouse = tcod.Mouse()

    while not tcod.console_is_window_closed():
        tcod.sys_check_for_event(tcod.EVENT_KEY_PRESS | tcod.EVENT_MOUSE, key, mouse)

        if show_main_menu:
            console.main_menu.render(['New Game', 'Load Save', 'Quit'])

            if show_load_error_message:
                print("Error occured and this ran (show load error message)")
                return 1

            tcod.console_flush()

            action = handle_main_menu_keys(key)

            new_game = action.get('new_game')
            load_saved_game = action.get('load_game')
            exit_game = action.get('exit')

            if show_load_error_message and (new_game or load_saved_game or exit_game):
                show_load_error_message = False
            elif new_game:
                player = create_player()
                player.stat_logger = GameLog(parent=console, width=50)

                # DEBUG
                give_items(player)
                
                entities = [player]

                # initialize a game map object
                game_map = create_game_map(map_width, map_height, player, entities)
                game_state = GameStates.PLAYER_TURN

                show_main_menu = False
            elif load_saved_game:
                try:
                    data = load_game()
                    player = data.get('player')
                    entities = data.get('entities')
                    game_map = data.get('game_map')

                    # message log probably needs to get refactored
                    message_log = data.get('message_log')
                    message_log.parent = console.panel
                    console.panel.message_log = message_log

                    game_state = data.get('game_state')
                    show_main_menu = False
                except FileNotFoundError:
                    show_load_error_message = True
            elif exit_game:
                break
        else:
            console.clear()
            return play(console, player, entities, game_map, game_state)

if __name__ == '__main__':
    main()