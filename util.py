import random

def is_on_same_tile(this, other):
    return this.x == other.x and this.y == other.y

def get_entity_at_coord(x, y, entities):
    for entity in entities:
        if entity.x == x and entity.y == y:
            return entity
    
    return None

def entity_on_tile(entity, x, y):
    return entity.x == x and entity.y == y

def is_same_entity_name(entity, other):
    return entity.name == other.name

def drop_dead_entity_inventory(dead_entity, entities):
    while dead_entity.inventory:
        dropped_item = dead_entity.inventory.items.pop()
        dropped_item.x = dead_entity.x
        dropped_item.y = dead_entity.y
        entities.append(dropped_item)