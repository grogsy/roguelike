from entities.actors import Player
from map_objects.game_map import GameMap
from components.fighter import Fighter
from components.inventory import Inventory
from colors import Colors
from ui import RootConsole
from ui.menu import Menu
from fov_functions import FOV_Map

def create_player():
    player = Player(
        0, 0,
        '@', Colors.player, 'Player', 
        # fighter=Fighter(hp=30, mana=30, defense=2, power=5, accuracy=100),
        fighter=Fighter(
            hp=10,
            power=5,
            defense=4,
            constitution=5,
            strength=4,
            intelligence=4,
            dexterity=5,
            mana=10
        ),
        inventory=Inventory(capacity=26)
    )

    return player

def create_game_map(width, height, player, entities):
    game_map = GameMap(width, height)
    game_map.make_map(player, entities)

    return game_map

def create_root_console(font, screen_width, screen_height, map_height):
    return RootConsole(font, screen_width, screen_height, map_height)

def create_fov_map(game_map):
    return FOV_Map(game_map)

def create_menu(console, header_label, options, menu_width=50):
    return Menu(console, menu_width, header_label).render(options)