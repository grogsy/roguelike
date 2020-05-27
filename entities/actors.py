import functools
import tcod
import math

from .entity import Entity
from .util import get_blocking_entities_at_location

from components.ai import BasicMonster
from components.level import Level

from game_state import RenderOrder
from game_messages import message

def update(func):
    '''
    A wrapper that updates turn-based internal state, such as mana regen 
    and buff duration of sentient entities.

    inst -> the instance of a sentient entity this function is working on.
    '''
    @functools.wraps(func)
    def updater(inst, *args, **kwargs):
        results = []
        function_results = func(inst, *args, **kwargs)
        # most entity methods return a list result of messages to pass to the 
        # logger. Some(like Entity.move) don't, which is why this checking
        # is somewhat necessary.
        if isinstance(function_results, list):
            results.extend(function_results)

        inst.turn_count += 1
        inst.update_mana_regen()
        results.extend(inst.update_buff_counter())

        return results
    return updater

class Actor(Entity):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, render_order=RenderOrder.ACTOR, **kwargs)
        self.hostile = False
        self.turn_count = 0

    def update_mana_regen(self):
        self.fighter.update_mana_regen()

    @update
    def attack(self, target):
        return self.fighter.attack(target)

    def take_damage(self, amount):
        return self.fighter.take_damage(amount)

class Player(Actor):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.level = Level()

    def gain_xp(self, amt):
        return self.level.add_xp(amt)

    @property
    def _level(self):
        return self.level.current_level

    @update
    def use(self, obj, target=None, **kwargs):
        '''
        obj param should support more than just items(possibly different entities)
        target param should support more than just entities(it should support locations on the map as well).
        '''
        results = []
        item = obj
        # notify that the item requires targeting
        if item.use_effect.directional_targeting and not (kwargs.get('dx') or kwargs.get('dy')):
            results.append(message(requires_targeting=item))
        # requires point-and-click targeting
        elif item.use_effect.requires_target and not (kwargs.get('target_x') or kwargs.get('target_y')):
            results.append(message(requires_targeting=item))
        else:
            results.extend(item.use(**kwargs)) 
            self.stat_logger.write_entry(item)


        return results

    @update
    def loot(self, item):
        results = []

        if len(self.inventory) >= self.inventory.capacity:
            results.append(message(item_added=None, message="You cannot carry any more, your inventory is full.", color=tcod.yellow))
        else:
            self.inventory.add_item(item)
            results.append(message(item_added=item, message=f"You pick up the {item}."))

        return results

    def remove_item(self, item):
        self.inventory.remove_item(item)

    @update
    def drop_item(self, item):
        results = []

        item.x = self.x
        item.y = self.y

        self.remove_item(item)

        results.append(message(source=self.name, item_dropped=item, message=f"You drop the {item.name}", color=tcod.yellow))

        return results

    @update
    def open(self, obj, *args, **kwargs):
        results = []
        if obj.locked:
            msg = f"That {obj} is locked."
        elif obj.open(*args, **kwargs):
            msg = f"You open the {obj}."
        else:
            msg = f"You attempt to open the {obj}, but it only budges slightly."

        results.append(message(message=msg))

        return results
    
    @update
    def move(self, *args, **kwargs):
        results = [message(player_move=True)]
        super().move(*args, **kwargs)

        return results

    @update
    def wait(self):
        return [message(player_wait=True)]


class Enemy(Actor):
    def __init__(self, *args, level, **kwargs):
        super().__init__(*args, **kwargs)

        self.ai = BasicMonster()
        self.ai.owner = self
        self.soft_max_inventory = 3
        self._level = level
        self.hostile = True

    def take_turn(self, *args, **kwargs):
        return self.ai.take_turn(*args, **kwargs)

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
