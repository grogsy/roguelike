import random
import math
from uuid import uuid4

import tcod

from components import BasicMonster
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
            inventory=None
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


    def __repr__(self):
        return f"<{self.__class__.__name__} '{self.name}'({self.x},{self.y}){'(dead)' if self.render_order == RenderOrder.CORPSE else ''}>"

    def use(self, obj, target=None, **kwargs):
        '''
        obj param should support more than just items(possibly different entities)
        target param should support more than just entities(it should support locations on the map as well).
        '''
        results = []
        if isinstance(obj, Item):
            item = obj
            # notify that the item requires targeting
            if item.use_effect.requires_target and not (kwargs.get('target_x') or kwargs.get('target_y')):
                # if no target specified, try using it on self
                # target = target or self
                # results.extend(obj.use_effect(target=target, **kwargs))
                results.append({ 'requires_targeting': item })
            else:
                if isinstance(item, Scroll):
                    results.append({'message': Message(f"You read from the {item.name}.")})
                results.extend(item.use_effect(**kwargs)) 

                for item_use_result in results:
                    if item_use_result.get('consumed'):
                        self.remove_item(item)
                        self.stat_logger.write_entry(item)
                        break


        return results

    def remove_item(self, item):
        self.inventory.remove_item(item)
        # self.inventory.items.remove(item)

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

class Player(Entity):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

class Enemy(Entity):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs, render_order=RenderOrder.ACTOR)

        self.ai = BasicMonster()
        self.ai.owner = self

    def move_towards(self, target_x, target_y, game_map, entities):
        dx = target_x - self.x
        dy = target_y - self.y
        dist = math.sqrt(dx** 2 + dy**2)

        dx = int(round(dx / dist))
        dy = int(round(dy / dist))

        if not (
            game_map.is_blocked_by_tiling(self.x + dx, self.y + dy) or
            get_blocking_entities_at_location(entities, self.x + dx, self.y + dy)
        ):
            self.move(dx, dy)

    def move_astar(self, target, game_map, entities):
        # Create fov map that has dimensions of the game map
        fov = tcod.map_new(game_map.width, game_map.height)

        # Scan the current map each turn and set all the walls as unwalkable
        height = game_map.height
        width = game_map.width
        for y in range(height):
            for x in range(width):
                tcod.map_set_properties(
                    fov,
                    x, y,
                    not game_map.tiles[x][y].block_sight,
                    not game_map.tiles[x][y].blocked
                )

        # Scan all the objects to see if there are objects that must be navigated around
        # Check also that the object isn't self or the target (so that the start and the end points are free)
        # The AI class handles the situation if self is next to the target so it will not use this A* function anyway
        for entity in entities:
            for entity in entities:
                # if entity.blocks and entity is not self and entity is not target:
                if not isinstance(entity, Enemy) and entity.blocks and entity is not self and entity is not target:
                    tcod.map_set_properties(
                        fov,
                        entity.x, entity.y,
                        True, False
                    )

        # Allocate a A* path
        # The 1.41 is the normal diagonal cost of moving, it can be set as 0.0 if diagonal moves are prohibited
        my_path = tcod.path_new_using_map(fov, 1.41)

        # Check if the path exists, and in this case, also the path is shorter than 25 tiles
        # The path size matters if you want the monster to use alternative longer paths (for example through other rooms) if for example the player is in a corridor
        # It makes sense to keep path size relatively low to keep the monsters from running around the map if there's an alternative path really far away
        if not tcod.path_is_empty(my_path) and tcod.path_size(my_path) < 25:
            # Find the next coordinates in the computed full path
            x, y = tcod.path_walk(my_path, True)
            if x or y:
                # Set self's coordinates to the next path tile
                self.x = x
                self.y = y
        else:
            # Keep the old move function as a backup so that if there are not paths (e.g. another monster blocks a corridor)
            # it will still try to move towards the player(closer to the corridor opening)
            self.move_towards(target.x, target.y, game_map, entities)

        # Delete path to free memory            
        tcod.path_delete(my_path)

class Item(Entity):
    def __init__(self, *args, use_effect=None, **kwargs):
        super().__init__(*args, **kwargs, blocks=False, render_order=RenderOrder.ITEM)
        self.use_effect = use_effect
        self.use_effect.source = self

class Scroll(Item):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

class Potion(Item):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


def get_blocking_entities_at_location(entities, dst_x, dst_y):
    '''
    Checks if an entity is blocking at coords x,y.
    '''
    for e in entities:
        if e.blocks and e.x == dst_x and e.y == dst_y:
            return e

    return None