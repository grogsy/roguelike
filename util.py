from entity import Item
import items

def is_on_same_tile(this, other):
    return this.x == other.x and this.y == other.y