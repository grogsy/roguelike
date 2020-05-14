import tcod

class StatsView:
    def __init__(self, parent, width):
        self.parent = parent
        self.width = width

    def render(self, player):
        header_height = tcod.console_get_height_rect(
            self.parent.console,
            0, 0,
            self.width,
            self.parent.height,
            "Character Stats:"
        )

        window_height = len(player.fighter.all_stats) + 10

        window = tcod.console_new(self.width, window_height)
        tcod.console_set_default_foreground(window, tcod.white)
        tcod.console_print_rect_ex(window, 0, 0, self.width, window_height, tcod.BKGND_NONE, tcod.LEFT, "Character Stats:\n")

        y = header_height
        for title, stat in player.fighter.all_stats.items():
            tcod.console_print_ex(window, 0, y, tcod.BKGND_NONE, tcod.LEFT, f"{title}: {stat}")
            y += 1
            
        x = int(self.parent.width / 2 - self.width / 2)
        y = int(self.parent.height / 2 - window_height / 2)
        tcod.console_blit(window, 0, 0, self.width, window_height, 0, x, y, 1.0, 0.7)