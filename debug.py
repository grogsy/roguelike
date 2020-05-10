import tcod
from fov_functions import initialize_fov

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