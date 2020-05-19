import tcod
import math

from .entity import Entity
from .util import get_blocking_entities_at_location

from components.ai import BasicMonster
from game_state import RenderOrder


class Player(Entity):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

class Enemy(Entity):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs, render_order=RenderOrder.ACTOR)

        self.ai = BasicMonster()
        self.ai.owner = self
        self.soft_max_inventory = 3

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
