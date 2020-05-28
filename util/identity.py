def is_item(entity):
    return getattr(entity, "use_effect", False)

def is_stairs(tile):
    return tile.__class__.__name__ == 'Stairs'

def is_door(tile):
    return tile.__class__.__name__ == 'Door'

def is_player(entity):
    return entity.__class__.__name__ == 'Player'

def is_tunnel(entity):
    return entity.__class__.__name__ == 'Tunnel'

def is_container(entity):
    return getattr(entity, 'initialize_loot', False)

def is_equipable(item):
    return getattr(item, 'equip_slot', False)