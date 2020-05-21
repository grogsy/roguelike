import tcod
from collections import defaultdict

# from entity import Stackable, Item
from entities.items import Item, Stackable, Guld

class StackManager:
    '''
    A helper class for the inventory to manage stackable items.
    '''
    def __init__(self):
        self.items = defaultdict(list)

    def __contains__(self, item):
        return item.name in self.stacks

    def add(self, item):
        self.items[item.name].append(item)
    
    def remove(self, item):
        del self.items[item.name]

class Inventory:
    def __init__(self, capacity):
        self.capacity = capacity
        self.items = []
        self.stacks = StackManager()
        self.guld = 0

    def __bool__(self):
        return bool(self.items)

    def __len__(self):
        return len(self.items)

    def add_item(self, item):
        if isinstance(item, Stackable):
            if isinstance(item, Guld):
                self.guld += item.stack_count
            else:
                for i in self.items:
                    if i.name == item.name:
                        i.stack_count += item.stack_count
                        break
                else:
                    self.items.append(item)
        else:
            self.items.append(item)
            
    def append(self, item):
        assert isinstance(item, Item)
        if isinstance(item, Guld):
            self.guld += item.stack_count
        else:
            self.items.append(item)

    def remove_item(self, item):
        self.items.remove(item)