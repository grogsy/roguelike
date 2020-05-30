def has_equip(entity):
    return getattr(entity, 'equipment', False)

def has_inventory(entity):
    return getattr(entity, 'inventory', False)