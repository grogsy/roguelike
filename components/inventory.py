import tcod
from collections import defaultdict
from game_messages import Message
from entity import Stackable, Item

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

    def add_item(self, item):
        results = []

        if len(self.items) >= self.capacity:
            results.append({
                'item_added': None,
                'message': Message('You cannot carry any more, your inventory is full.', tcod.yellow)
            })
        else:
    
            # rough draft of implementing stackable item
            if isinstance(item, Stackable):
                for i in self.items:
                    if i.name == item.name:
                        i.stack_count += item.stack_count
                        break
                else:
                    self.items.append(item)
                results.append({'item_added': item, 'message': Message(f"You pick up {item.name} x{item.stack_count}")})
            else:    
                self.items.append(item)
                results.append({
                    'item_added': item,
                    'message': Message(f"You pick up the {item.name}.", tcod.lighter_blue)
                })

        return results

    def append(self, item):
        assert isinstance(item, Item)
        self.items.append(item)

    def remove_item(self, item):
        self.items.remove(item)