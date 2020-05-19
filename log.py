'''
Simple playthrough statistics
'''
from collections import defaultdict
import tcod

from entities.items import Item
from entities.actors import Enemy

class GameLog:
    def __init__(self, parent, width):
        self.monsters_killed = defaultdict(int)
        self.items_used = defaultdict(int)
        self.floors_traveled = 1
        self.items_looted = 0

        self.parent = parent
        self.width = width

    def write_entry(self, entity):
        if isinstance(entity, Item):
            self.items_used[entity.name] += 1
        elif isinstance(entity, Enemy):
            self.monsters_killed[entity.name] += 1

    def log_travel(self):
        self.floors_traveled += 1

    def log_loot(self):
        self.items_looted += 1

    def render(self):
        header_height = tcod.console_get_height_rect(
            self.parent.console,
            0, 0,
            self.width,
            self.parent.height,
            "Game Stats:"
        )

        window_height = len(self.monsters_killed) + len(self.items_used) + header_height + 10

        window = tcod.console_new(self.width, window_height)
        tcod.console_set_default_foreground(window, tcod.white)
        tcod.console_print_rect_ex(window, 0, 0, self.width, window_height, tcod.BKGND_NONE, tcod.LEFT, "Game Stats:\n")

        y = header_height
        for title, log in (('Monsters Killed: ', self.monsters_killed), ('Items Used: ', self.items_used)):
            tcod.console_print_ex(window, 0, y, tcod.BKGND_NONE, tcod.LEFT, title)
            y += 1
            for entity, value in log.items():
                tcod.console_print_ex(window, 3, y, tcod.BKGND_NONE, tcod.LEFT, f"{entity}: {value}")
                y += 1
            tcod.console_print_ex(window, 0, y, tcod.BKGND_NONE, tcod.LEFT, "\n")
            y += 1

        tcod.console_print_ex(window, 0, y, tcod.BKGND_NONE, tcod.LEFT, f"\nItems Looted: {self.items_looted}")
        y += 1
        tcod.console_print_ex(window, 0, y, tcod.BKGND_NONE, tcod.LEFT, f"\nFloors traveled: {self.floors_traveled}")

        x = int(self.parent.width / 2 - self.width / 2)
        y = int(self.parent.height / 2 - window_height / 2)
        tcod.console_blit(window, 0, 0, self.width, window_height, 0, x, y, 1.0, 0.7)