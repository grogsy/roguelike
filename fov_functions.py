import tcod

class FOV_Map:
    '''
    Wrapper class for field-of-view functionality used by the player and ai entities.
    '''
    def __init__(self, game_map):
        # determine if field-of-view needs to be recomputed
        # initially set to True in order to initialize field-of-view on first screen render
        self.recompute = True

        # http://roguecentral.org/doryen/data/libtcod/doc/1.5.1/html2/fov_compute.html
        self.algorithm = 0
        self.default_radius = 7
        self.light_walls = True
        self.fov_map = self.initialize_fov(game_map)

    def initialize_fov(self, game_map):
        self.width = game_map.width
        self.height = game_map.height

        fov_map = tcod.map_new(self.width, self.height)
        for y in range(self.height):
            for x in range(self.width):
                tile = game_map.tiles[x][y]
                tcod.map_set_properties(
                    fov_map,
                    x, y,
                    not tile.block_sight,
                    not tile.blocked
                )

        return fov_map

    def recompute_fov(self, x, y, radius=None, light_walls=None, algorithm=None):
        if not radius:
            radius = self.default_radius
        if not light_walls:
            light_walls = self.light_walls
        if not algorithm:
            algorithm = self.algorithm

        tcod.map_compute_fov(self.fov_map, x, y, radius, light_walls, algorithm)

    def modify_fov_at_tile(self, x, y, transparent, walkable):
        '''
        Adjust the fov at x, y.
        This is useful for when the player takes actions such as opening and closing doors;
        it will modify the fov for a previously closed door, which has no viewability beyond it, for example,
        and allow the player to see past it as if it were not view blocking.
        '''
        tcod.map_set_properties(
            self.fov_map,
            x, y,
            transparent,
            walkable
        )

        self.recompute = True

    def is_in_fov(self, x, y):
        return tcod.map_is_in_fov(self.fov_map, x, y)



def initialize_fov(game_map):
    width = game_map.width
    height = game_map.height

    fov_map = tcod.map_new(width, height)

    for y in range(height):
        for x in range(width):
            tile = game_map.tiles[x][y]
            tcod.map_set_properties(
                fov_map, 
                x, y, 
                not tile.block_sight, # is_transparent
                not tile.blocked      # is_walkable
            )

    return fov_map

def recompute_fov(fov_map, x, y, radius, light_walls=True, algorithm=0):
    tcod.map_compute_fov(fov_map, x, y, radius, light_walls, algorithm)