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

        y = header_height + 1
        x_offset = 14
        for title, stat in player.fighter.all_stats.items():
            title_text = f"{title}:"
            tcod.console_print_ex(window, 0, y, tcod.BKGND_NONE, tcod.LEFT, title_text)
            value_text = f"{stat}"
            tcod.console_print_ex(window, x_offset, y, tcod.BKGND_NONE, tcod.LEFT, value_text)
            self.handle_stat_bonus_display(window, player, title, x_offset + 3, y)

            y += 1
            
        x = int(self.parent.width / 2 - self.width / 2)
        y = int(self.parent.height / 2 - window_height / 2)
        tcod.console_blit(window, 0, 0, self.width, window_height, 0, x, y, 1.0, 0.7)

    def handle_stat_bonus_display(self, window, player, stat_name, x_offset, y):
        if stat_name == 'Attack Power' and (player.fighter.calculate_attack_bonus_from_buffs() != 0 or player.equipment.power_bonus != 0):
            tcod.console_set_default_foreground(window, tcod.green)
            bonus_attack = player.fighter.calculate_attack_bonus_from_buffs() + player.equipment.power_bonus
            tcod.console_print_ex(window, x_offset, y, tcod.BKGND_NONE, tcod.LEFT, f"+{bonus_attack}")
        elif stat_name == 'Defense' and player.equipment.defense_bonus > 0:
            tcod.console_set_default_foreground(window, tcod.green)
            tcod.console_print_ex(window, x_offset, y, tcod.BKGND_NONE, tcod.LEFT, f"+{player.equipment.defense_bonus}")

        tcod.console_set_default_foreground(window, tcod.white)