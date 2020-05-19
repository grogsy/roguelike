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