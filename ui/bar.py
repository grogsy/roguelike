import tcod

class Bar:
    '''
    Progression bars
    '''
    def __init__(self, parent, label, color, bg_color, width):
        self.parent = parent
        self.width = width
        self.color = color
        self.label = label
        self.bg_color = bg_color

    def clear(self):
        tcod.console_set_default_background(self.panel, tcod.red)
        tcod.console_clear(self.panel)

    def render(self, x, y, value, max_value):
        '''
        x -> x-pos on parent console
        y -> y pos on parent console
        '''
        bar_width = int(float(value) / max_value * self.width)

        tcod.console_set_default_background(self.parent.console, self.bg_color)
        tcod.console_rect(self.parent.console, x, y, self.width, 1, False, tcod.BKGND_SCREEN)

        tcod.console_set_default_background(self.parent.console, self.color)
        if bar_width > 0:
            tcod.console_rect(self.parent.console, x, y, bar_width, 1, False, tcod.BKGND_SCREEN)

        tcod.console_set_default_foreground(self.parent.console, tcod.white)

        tcod.console_print_ex(
            self.parent.console,
            int(x + self.width / 2), y,
            tcod.BKGND_NONE, tcod.CENTER,
            f"{self.label}: {value}/{max_value}"
        )

# panel.health_bar = Bar(panel, 'HP', red, dark_red, 20)