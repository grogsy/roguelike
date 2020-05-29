import tcod

def is_on_same_tile(this, other):
    return this.x == other.x and this.y == other.y

def show_equipped_items(console, player):
    menu_width = 50
    
    header_height = tcod.console_get_height_rect(
        console.console,
        0, 0,
        menu_width,
        console.height,
        "You are currently equipping: "
    )

    menu_height = 30

    window = tcod.console_new(menu_width + 2, menu_height)

    tcod.console_set_default_foreground(window, tcod.white)
    tcod.console_print_rect_ex(
        window, 0, 0, 
        menu_width, menu_height, 
        tcod.BKGND_NONE, tcod.LEFT, 
        "You are currently equipping: "
    )

    y = header_height + 2

    for slot, item in player.equipment.slots.items():
        x_pos = 0
        this_slot_text = ' '.join(slot.name.split('_')).title() + ': '
        
        tcod.console_set_default_foreground(window, tcod.white)
        tcod.console_print_ex(window, x_pos, y, tcod.BKGND_NONE, tcod.LEFT, this_slot_text)
        x_pos += len(this_slot_text) + 1
        if item:
            tcod.console_set_default_foreground(window, item.color)
            tcod.console_print_ex(window, x_pos, y, tcod.BKGND_NONE, tcod.LEFT, item.char)
            x_pos += 2
            tcod.console_set_default_foreground(window, tcod.white)
            tcod.console_print_ex(window, x_pos, y, tcod.BKGND_NONE, tcod.LEFT, item.name)
        else:
            tcod.console_print_ex(window, x_pos, y, tcod.BKGND_NONE, tcod.LEFT, "Nothing equipped in this slot.")

        y += 1

    
    x = int(console.width / 2 - menu_width / 2)
    y = int(console.height / 2 - menu_height / 2)

    tcod.console_blit(window, 0, 0, menu_width, menu_height, 0, x, y, 1.0, 0.7)