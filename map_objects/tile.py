import random
import tcod
from colors import Colors

class Tile:
    '''
    A tile on a map. It may or may not block movement and/or sight.
    '''

    def __init__(self, blocked, x, y, block_sight=None):
        self.blocked = blocked
        self.explored = False
        self.color = Colors.unexplored
    
        self.visible_color = Colors.light_ground
        self.out_of_fov_color = Colors.dark_ground

        # grab coords for debugging purposes
        self.x = x
        self.y = y

        # by default, if a tile is blocked it also blocks sight
        if block_sight is None:
            block_sight = blocked

        self.block_sight = block_sight

    def __repr__(self):
        return f"<{self.__class__.__name__} ({self.x}, {self.y})>"

    def __str__(self):
        return f"{self.__class__.__name__.lower()}"

    def render(self, console, in_fov=False):
        is_wall = self.block_sight

        if in_fov:
            self.color = self.visible_color if not is_wall else Colors.light_wall
        elif self.explored:
            self.color = self.out_of_fov_color if not is_wall else Colors.dark_wall
        # else:
            # color = Colors.unexplored

        tcod.console_set_char_background(console, self.x, self.y, self.color, tcod.BKGND_SET)

class Tunnel(Tile):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.visible_color = Colors.light_tunnel
        self.out_of_fov_color = Colors.dark_tunnel

class Door(Tile):
    def  __init__(self, orientation, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.blocked = True
        self.block_sight = True
        self.opened = False
        self.orientation = orientation
        self.locked = False

    def __str__(self):
        return "door"

    def open(self, fov_map):
        if random.randint(0, 1) == 1:
            self.blocked = False
            self.block_sight = False
            self.opened = True
            fov_map.modify_fov_at_tile(self.x, self.y, transparent=True, walkable=True)
        
        return self.opened

    def render(self, console, in_fov=False):
        if not self.opened:
            char = '+'
        elif self.orientation == 'v':
            char = '|'
        elif self.orientation == 'h':
            char = '-'

        super().render(console, in_fov)
        if self.explored or in_fov:
            tcod.console_set_default_foreground(console, tcod.white)
            tcod.console_put_char(console, self.x, self.y, char, tcod.BKGND_NONE)

class Stairs(Tile):
    def __init__(self, level, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.level = level
        self.char = '>'

    def render(self, console, in_fov=False):
        super().render(console, in_fov)
        if self.explored or in_fov:
            tcod.console_set_default_foreground(console, tcod.white)
            tcod.console_put_char(console, self.x, self.y, self.char, tcod.BKGND_NONE)