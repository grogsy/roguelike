import tcod

def render_text(console, text, color, x_pos, y_pos, alignment=tcod.LEFT):
    tcod.console_set_default_foreground(console, color)
    tcod.console_print_ex(console, x_pos, y_pos, tcod.BKGND_NONE, alignment, text)