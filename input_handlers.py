import tcod
from game_state import GameStates
from constants import INVENTORY_CONTEXT


def handle_keys(key, game_state):
    if game_state == GameStates.PLAYER_TURN:
        return handle_player_turn_keys(key)
    elif game_state in INVENTORY_CONTEXT:
        return handle_inventory_keys(key)
    elif game_state == GameStates.TARGETING:
        return handle_targeting_keys(key)
    elif game_state == GameStates.CHECK_PLAYER_STATS:
        return handle_player_stat_keys(key)
    elif game_state == GameStates.PLAYER_DEAD:
        return handle_player_dead_keys(key)
    elif game_state == GameStates.CHECK_CHAR_STATS:
        return handle_player_check_stats(key)
    elif game_state == GameStates.PLAYER_LEVEL_UP:
        return handle_player_level_up(key)
    elif game_state == GameStates.VIEW_EQUIP:
        return handle_view_equip_keys(key)

    return {}

def handle_player_turn_keys(key):
    # get the corresponding char from the keycode
    key_char = chr(key.c)

    # movement keys
    if key.vk in (tcod.KEY_UP, tcod.KEY_KP8):
        return { 'move': (0, -1) }
    elif key.vk in (tcod.KEY_DOWN, tcod.KEY_KP2):
        return { 'move': (0, 1) }
    elif key.vk in (tcod.KEY_LEFT, tcod.KEY_KP4):
        return { 'move': (-1, 0) }
    elif key.vk in (tcod.KEY_RIGHT, tcod.KEY_KP6):
        return { 'move': (1, 0) }
    elif key.vk == tcod.KEY_KP7:
        return { 'move': (-1, -1) }
    elif key.vk == tcod.KEY_KP9:
        return { 'move': (1, -1) }
    elif key.vk == tcod.KEY_KP1:
        return { 'move': (-1, 1) }
    elif key.vk == tcod.KEY_KP3:
        return { 'move': (1, 1) }

    if key.vk == tcod.KEY_ENTER and key.lalt:
        # alt + enter: toggle full screen
        return { 'fullscreen': True }
    elif key.vk == tcod.KEY_ESCAPE:
        return { 'exit': True }
    elif key_char == 'c':
        return { 'check_player_status': True }
    elif key_char == ',' or key_char == 'l':
        return { 'pickup': True }
    elif key_char == 'i':
        return { 'show_inventory': True }
    elif key_char == 'd':
        return { 'drop_inventory': True }
    elif key_char == 'r':
        return { 'select_readable': True }
    elif key_char == 't':
        return { 'select_projectile': True }
    elif key_char == 'q':
        return { 'select_quaffable': True }
    elif key_char == 'e':
        return { 'equipping': True }
    elif key_char == 'u':
        return { 'unequipping': True }
    elif key_char == 'w':
        return { 'view_equip': True }
    elif key_char == 's':
        return { 'view_stats': True }
    elif key_char == 'z' or key_char == '.':
        return { 'wait': True }
    elif key.vk == tcod.KEY_ENTER:
        return { 'take_stairs': True }

    return {}

def handle_inventory_keys(key):
    index = key.c - ord('a')

    if index >= 0:
        return { 'inventory_index': index }
    if key.vk == tcod.KEY_ENTER and key.lalt:
        return { 'fullscreen': True }
    elif key.vk == tcod.KEY_ESCAPE:
        return { 'exit': True }

    return {}

def handle_player_dead_keys(key):
    key_char = chr(key.c)

    if key_char == 'i':
        return { 'show_inventory': True }
    if key.vk == tcod.KEY_ENTER and key.lalt:
        return { 'fullscreen': True }
    elif key.vk == tcod.KEY_ESCAPE:
        return { 'exit': True }

    return {}

def handle_player_stat_keys(key):
    key_char = chr(key.c)

    if key_char == 'c' or key.vk == tcod.KEY_ESCAPE:
        return { 'exit': True }

    return {}

def handle_targeting_keys(key):
    key_char = chr(key.c)
    if key.vk == tcod.KEY_ESCAPE:
        return { 'exit': True }
    if key.vk in (tcod.KEY_UP, tcod.KEY_KP8):
        return { 'move': (0, -1) }
    elif key.vk in (tcod.KEY_DOWN, tcod.KEY_KP2):
        return { 'move': (0, 1) }
    elif key.vk in (tcod.KEY_LEFT, tcod.KEY_KP4):
        return { 'move': (-1, 0) }
    elif key.vk in (tcod.KEY_RIGHT, tcod.KEY_KP6):
        return { 'move': (1, 0) }
    elif key.vk == tcod.KEY_KP7:
        return { 'move': (-1, -1) }
    elif key.vk == tcod.KEY_KP9:
        return { 'move': (1, -1) }
    elif key.vk == tcod.KEY_KP1:
        return { 'move': (-1, 1) }
    elif key.vk == tcod.KEY_KP3:
        return { 'move': (1, 1) }

    elif key.vk == tcod.KEY_ENTER or key_char == '.':
        return { 'confirm_action': True }

    return {}

def handle_player_check_stats(key):
    key_char = chr(key.c)
    if key.vk == tcod.KEY_ESCAPE or key.vk == tcod.KEY_ENTER or key_char == 's':
        return { 'exit': True }

    return {}

def handle_mouse(mouse):
    x, y = (mouse.cx, mouse.cy)

    if mouse.lbutton_pressed:
        return { 'left_click': (x, y) }
    elif mouse.rbutton_pressed:
        return { 'right_click': (x, y) }

    return {}

def handle_main_menu_keys(key):
    key_char = chr(key.c)

    if key_char == 'a':
        return { 'new_game': True }
    elif key_char == 'b':
        return { 'load_game': True }
    elif key_char == 'c' or key.vk == tcod.KEY_ESCAPE:
        return { 'exit': True }

    return {}

def handle_player_level_up(key):
    if key:
        key_char = chr(key.c)

        if key_char == 'a':
            return { 'level_up': 'CON' }
        elif key_char == 'b':
            return { 'level_up': 'STR' }
        elif key_char == 'c':
            return { 'level_up': 'INT' }
        elif key_char == 'd':
            return { 'level_up': 'DEX' }

    return {}

def handle_view_equip_keys(key):
    key_char = chr(key.c)

    if key_char == 'w' or key.vk == tcod.KEY_ESCAPE:
        return { 'exit': True }

    return {}