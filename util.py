from entity import Item
import items

def is_on_same_tile(this, other):
    return this.x == other.x and this.y == other.y

def place_item(x, y):
    item = Item(x, y, **items.potion_of_healing)
    
    return item