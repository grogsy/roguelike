import math
import random
from uuid import uuid4
import tcod

from components.ai import BasicMonster
from game_state import RenderOrder
from game_messages import Message

class Entity:
    '''
    A generic object to represent players, enemies, items, etc.
    '''

    def __init__(
            self, 
            x, y, 
            char, color, name, 
            blocks=True, 
            render_order=RenderOrder.CORPSE, 
            fighter=None,
            inventory=None,
            level=1
    ):
        self.x = x
        self.y = y
        self.char = char
        self.color = color
        self.name = name
        self.blocks = blocks
        self.render_order = render_order
        self.fighter = fighter
        self.inventory = inventory
        self.level = level

        self.ai = None

        self.id = str(uuid4())

        if self.fighter:
            self.fighter.owner = self
        if self.inventory:
            self.inventory.owner = self

    def move(self, dx, dy):
        '''
        Move the entity by a given amount
        '''
        self.x += dx
        self.y += dy

    def update_buff_counter(self):
        results = []
        if self.fighter:
            results.extend(self.fighter.buffs.update_buff_counter())

        return results

    def update_mana_regen(self, turn_count):
        self.fighter.update_mana_regen(turn_count)


    def __repr__(self):
        return f"<{self.__class__.__name__} '{self.name}'({self.x},{self.y}){'(dead)' if self.render_order == RenderOrder.CORPSE else ''}>"
    
    def __str__(self):
        return self.name

    def __eq__(self, other):
        return self.id == other.id

    def use(self, obj, target=None, **kwargs):
        '''
        obj param should support more than just items(possibly different entities)
        target param should support more than just entities(it should support locations on the map as well).
        '''
        results = []
        item = obj
        # notify that the item requires targeting
        if item.use_effect.directional_targeting and not (kwargs.get('dx') or kwargs.get('dy')):
            results.append({ 'requires_targeting': item})
        # requires point-and-click targeting
        elif item.use_effect.requires_target and not (kwargs.get('target_x') or kwargs.get('target_y')):
            results.append({ 'requires_targeting': item })
        else:
            results.extend(item.use(**kwargs)) 
            self.stat_logger.write_entry(item)

        return results

    def loot(self, item):
        results = []

        if len(self.inventory) >= self.inventory.capacity:
            results.append({
                'item_added': None,
                'message': Message('You cannot carry any more, your inventory is full.', tcod.yellow)
            })
        else:
            prefix = "You pick up" if self.name == "Player" else f"{self.name} picks up"
            self.inventory.add_item(item)
            results.append({
                'item_added': item,
                'message': Message(f"{prefix} the {item}.")
            })

        return results


    def remove_item(self, item):
        self.inventory.remove_item(item)

    def drop_item(self, item):
        results = []

        item.x = self.x
        item.y = self.y

        self.remove_item(item)

        prefix = 'You drop' if self.name == 'Player' else f"{self.name} drops"

        results.append({
            'source': self.name,
            'item_dropped': item,
            'message': Message(f"{prefix} the {item.name}.", tcod.yellow)
        })

        return results

    def distance(self, x, y):
        return math.sqrt((x - self.x) ** 2 + (y - self.y) ** 2)

    def distance_to(self, other):
        dx = other.x - self.x
        dy = other.y - self.y
        return math.sqrt(dx**2 + dy**2)