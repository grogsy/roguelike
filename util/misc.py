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
    equip_starting_x = 15

    for slot, item in player.equipment.slots.items():
        try:
            name = slot.name.split('_')
        except AttributeError:
            name = slot.split('_')
        this_slot_text = ' '.join(name).title() + ': '
        
        tcod.console_set_default_foreground(window, tcod.white)
        tcod.console_print_ex(window, 0, y, tcod.BKGND_NONE, tcod.LEFT, this_slot_text)
        if item:
            tcod.console_set_default_foreground(window, item.color)
            tcod.console_print_ex(window, equip_starting_x, y, tcod.BKGND_NONE, tcod.LEFT, item.char)
            tcod.console_set_default_foreground(window, tcod.white)
            tcod.console_print_ex(window, equip_starting_x + 2, y, tcod.BKGND_NONE, tcod.LEFT, item.name)
        else:
            tcod.console_print_ex(window, equip_starting_x, y, tcod.BKGND_NONE, tcod.LEFT, "Nothing equipped in this slot.")

        y += 2

    
    x = int(console.width / 2 - menu_width / 2)
    y = int(console.height / 2 - menu_height / 2)

    tcod.console_blit(window, 0, 0, menu_width, menu_height, 0, x, y, 1.0, 0.7)