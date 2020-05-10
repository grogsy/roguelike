import tcod
class MessageLogUI:
    '''
    A class which represents the game's message logger which displays
    game info at the bottom panel.

    args:
        x        -> int. How far from the left messages should be displayed
        width    -> int. Width size of the message container.
        height   -> int. Height size of the message container.
    '''
    def __init__(self, parent, x, width, height):
        self.panel = parent.panel
        self.x = x
        self.width = width
        self.height = height

    def render(self, message_log):
        y = 1
        for message in message_log.messages:
            tcod.console_set_default_foreground(self.panel, message.color)
            tcod.console_print_ex(self.panel, self.x, y, tcod.BKGND_NONE, tcod.LEFT, message.text)
            y += 1