import random

def is_on_same_tile(this, other):
    return this.x == other.x and this.y == other.y

def get_entity_at_coord(x, y, entities):
    for entity in entities:
        if entity.x == x and entity.y == y:
            return entity
    
    return None
