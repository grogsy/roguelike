import tcod

from .bar import Bar
from message_log import MessageLog

class Panel:
    def __init__(self, parent, width, screen_height, height):
        '''
        A ui panel wrapper to be displayed under the game map.
        This class contains attributes related to the panel console as well as the panel itself
        '''

        self.parent = parent
        self.height = height
        self.y = screen_height - self.height - 1
        self.width = width
        self.console = tcod.console_new(self.width, self.height)

        # components
        self.bar_width = 20
        self.health_bar = Bar(
            parent=self,
            label='HP',
            color=tcod.light_red,
            bg_color=tcod.dark_red,
            width=self.bar_width
        )
        self.mana_bar = Bar(
            parent=self,
            label='MP',
            color=tcod.light_azure,
            bg_color=tcod.dark_azure,
            width=self.bar_width
        )
        self.xp_bar = Bar(
            parent=self,
            label='XP',
            color=tcod.dark_yellow,
            bg_color=tcod.darker_yellow,
            width=self.bar_width
        )
        self.message_log = MessageLog(
            parent=self,
            x=self.health_bar.width + 2,
            width=self.parent.width - self.health_bar.width - 33,
            height=self.height - 1
        )

    def clear(self):
        tcod.console_set_default_background(self.console, tcod.black)
        tcod.console_clear(self.console)

    def console_blit(self):
        tcod.console_blit(self.console, 0, 0, self.width, self.height, 0, 0, self.y)

    def display_names(self, names):
        tcod.console_set_default_foreground(self.console, tcod.light_gray)
        tcod.console_print_ex(self.console, self.width - 35, 1, tcod.BKGND_NONE, tcod.LEFT, names)

    def render(self, player, entities, game_map, fov_map, mouse_event): #, message_log):
        self.clear()

        # message_log.render()
        self.message_log.render()
        names = self.parent.get_entities_at_mouse_cursor(mouse_event, entities, fov_map, game_map)
        names += self.parent.get_entities_at_player_location(player, entities) + '\n'
        names += self.parent.get_tile_at_player_locations(player, game_map)
        self.display_names(names)
        self.health_bar.render(1, 1, player.fighter.hp, player.fighter.max_hp)
        self.mana_bar.render(1, 2, player.fighter.mana, player.fighter.max_mana)
        self.xp_bar.render(1, 3, player.level.xp, player.level.xp_to_next_level)

        # below is experimental
        tcod.console_set_default_foreground(self.console, tcod.gold)
        money = f"$:{player.inventory.guld:05}"
        tcod.console_print_ex(self.console, 1, 4, tcod.BKGND_NONE, tcod.LEFT, money)

        tcod.console_set_default_foreground(self.console, tcod.white)
        player_level = f"LVL:{player.level.current_level}"
        tcod.console_print_ex(self.console, 1, 5, tcod.BKGND_NONE, tcod.LEFT, player_level)
        player_turn = f"Turn:{player.turn_count}"
        tcod.console_print_ex(self.console, len(player_level) + 2, 5, tcod.BKGND_NONE, tcod.LEFT, player_turn)
        player_def = f"DEF:{player.fighter.defense:02}"
        tcod.console_print_ex(self.console, 1, 6, tcod.BKGND_NONE, tcod.LEFT, player_def)
        tcod.console_print_ex(self.console, 1, 7, tcod.BKGND_NONE, tcod.LEFT, f"Floor:{game_map.dungeon_level}")
        # above is experimental

        self.console_blit()