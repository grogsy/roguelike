from enum import Enum
import textwrap

import tcod

from colors import Colors
from entity import get_blocking_entities_at_location
from debug import label_rooms, clear_labels
from render_order import RenderOrder
from ui import Panel
from map_objects import Door

def get_entities_at_mouse_cursor(panel, mouse, entities, fov_map, game_map):
    x, y = mouse.cx, mouse.cy

    names = []
    for entity in entities:
        if entity.x == x and entity.y == y and fov_map.is_in_fov(entity.x, entity.y):
            if entity.name == 'Player':
                names.append("You see yourself.")
            elif entity.name[0].lower() in 'aeiou':
                names.append(f"You see an {entity.name}")
            elif entity.render_order == RenderOrder.CORPSE:
                names.append(f"You see {entity.name}")
            else:
                names.append(f"You see a {entity.name}")
    
    width = game_map.width
    height = game_map.height
    for y in range(height):
        for x in range(width):
            tile = game_map.tiles[x][y]
            if tile.explored and tile.x == mouse.cx and tile.y == mouse.cy and isinstance(tile, Door):
                if tile.opened:
                    door_status = "an open"
                else:
                    door_status = "a closed"
                names.append(f"This is {door_status} door.")
        
    names = '\n'.join(names)

    panel.display_names_at_cursor(names)

def render_all(console, panel, player, game_map, fov_map, entities, screen_width, screen_height, message_log, mouse):
    draw_map(console, game_map, fov_map)

    for entity in sorted(entities, key=lambda e: e.render_order.value):
        draw_entity(console, entity, fov_map)

    tcod.console_blit(console, 0, 0, screen_width, screen_height, 0, 0, 0)

    panel.clear()
    panel.render_message_log(message_log)
    # display info panel below the map
    panel.render_bar(1, 1, 'HP', player.fighter.hp, player.fighter.max_hp,
                        tcod.light_red, tcod.dark_red)

    # get entities at cursor
    get_entities_at_mouse_cursor(panel, mouse, entities, fov_map, game_map)
    
    panel.console_blit()

def clear_all(console, entities, game_map):
    # LEVEL LABEL DEBUG
    clear_labels(console, game_map)

    for e in entities:
        clear_entity(console, e)

def clear_entity(console, entity):
    tcod.console_put_char(console, entity.x, entity.y, ' ', flag=tcod.BKGND_NONE)

def clear_old_tiles(console, old_rooms):
    '''
    A helper function that can be useful when regenerating a floor.
    It wipes the game map of old tile symbols that would otherwise appear on new floor generation.
    '''
    for room in old_rooms:
        for x in range(room.x1, room.x2 + 1):
            for y in range(room.y1, room.y2 + 1):
                tcod.console_put_char(console, x, y, ' ', flag=tcod.BKGND_NONE)

def draw_entity(console, entity, fov_map):
    if fov_map.is_in_fov(entity.x, entity.y):
        tcod.console_set_default_foreground(console, entity.color)
        tcod.console_put_char(console, entity.x, entity.y, entity.char, flag=tcod.BKGND_NONE)

def draw_map(console, game_map, fov_map):
    height = game_map.height
    width = game_map.width
    
    # label_rooms(console, game_map)

    if fov_map.recompute:
        for y in range(height):
            for x in range(width):
                tile = game_map.tiles[x][y]
                visible = fov_map.is_in_fov(x, y)

                if visible:
                    tile.render(console, in_fov=True)
                    tile.explored = True
                else:
                    tile.render(console, in_fov=False)
