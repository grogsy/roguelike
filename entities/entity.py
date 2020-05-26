import math
from uuid import uuid4
import tcod

from game_state import RenderOrder

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
        self.hostile = None

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

    def distance(self, x, y):
        return math.sqrt((x - self.x) ** 2 + (y - self.y) ** 2)

    def distance_to(self, other):
        dx = other.x - self.x
        dy = other.y - self.y
        return math.sqrt(dx**2 + dy**2)

    def __repr__(self):
        return f"<{self.__class__.__name__} '{self.name}'({self.x},{self.y}){'(dead)' if self.render_order == RenderOrder.CORPSE else ''}>"
    
    def __str__(self):
        return self.name

    def __eq__(self, other):
        return self.id == other.id

    def use(self, obj, target=None, **kwargs):
        raise NotImplemented

    def loot(self, item):
        raise NotImplemented

    def remove_item(self, item):
        raise NotImplemented


    def drop_item(self, item):
        raise NotImplemented

