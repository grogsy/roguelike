def get_blocking_entities_at_location(entities, dst_x, dst_y):
    '''
    Checks if an entity is blocking at coords x,y.
    '''
    for e in entities:
        if e.blocks and e.x == dst_x and e.y == dst_y:
            return e

    return None

def entity_on_tile(entity, x, y):
    return entity.x == x and entity.y == y

def is_same_entity_name(entity, other):
    return entity.name == other.name

def is_enemy(entity):
    return entity and entity.hostile

def is_alive(entity):
    return entity.ai is not None

def drop_dead_entity_inventory(dead_entity, entities):
    while dead_entity.inventory:
        dropped_item = dead_entity.inventory.items.pop()
        dropped_item.x = dead_entity.x
        dropped_item.y = dead_entity.y
        entities.append(dropped_item)