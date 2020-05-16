import tcod
from entity import Entity, Stackable, Item

class Menu:
    def __init__(self, parent, menu_width, header_label):
        self.parent = parent
        self.menu_width = menu_width
        self.header_label = header_label

    def render(self, options):
        if not len(options):
            options = ['Nothing to select.']
        elif len(options) > 26:
            raise ValueError("Cannot have a menu with more than 26 options.")

        header_height = tcod.console_get_height_rect(
            self.parent.console,
            0, 0,
            self.menu_width,
            self.parent.height,
            self.header_label
        )

        menu_height = len(options) + header_height

        window = tcod.console_new(self.menu_width + 2, menu_height)

        tcod.console_set_default_foreground(window, tcod.white)
        tcod.console_print_rect_ex(window, 0, 0, self.menu_width, menu_height, tcod.BKGND_NONE, tcod.LEFT, self.header_label)

        y = header_height
        letter_index = ord('a')
        for opt in options:
            if isinstance(opt, Entity):
                name = opt.name
                if isinstance(opt, Stackable):
                    name = f"{name} x{opt.stack_count}" 
            else:
                name = opt
            text = f"({chr(letter_index)}) {name}"
            if isinstance(opt, Item):
                tcod.console_set_default_foreground(window, opt.color)
                tcod.console_print_ex(window, 0, y, tcod.BKGND_NONE, tcod.LEFT, opt.char)
            tcod.console_set_default_foreground(window, tcod.white)
            tcod.console_print_ex(window, 2, y, tcod.BKGND_NONE, tcod.LEFT, text)
            y += 1
            letter_index += 1

        x = int(self.parent.width / 2 - self.menu_width / 2)
        y = int(self.parent.height / 2 - menu_height / 2)

        tcod.console_blit(window, 0, 0, self.menu_width, menu_height, 0, x, y, 1.0, 0.7)