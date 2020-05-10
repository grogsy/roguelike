import tcod

from .bar import Bar
from game_messages import MessageLog

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

    def render(self, player, entities, game_map, fov_map, mouse_event):
        self.clear()

        self.message_log.render()
        names = self.parent.get_entities_at_mouse_cursor(mouse_event, entities, fov_map, game_map)
        names += self.parent.get_entities_at_player_location(player, entities)
        self.display_names(names)
        self.health_bar.render(1, 1, player.fighter.hp, player.fighter.max_hp)
        self.mana_bar.render(1, 2, 30, 30)

        self.console_blit()