from random import randint

import tcod

from .tile import Tile, Door, Tunnel
from .rectangle import Rect
from entity import Entity, Enemy, Item, Scroll, Potion
# from components import Fighter, BasicMonster
from components.fighter import Fighter
from components.ai import BasicMonster
from components.inventory import Inventory
from game_state import RenderOrder
from game_messages import Message
import items

class GameMap:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.tiles = self.initialize_tiles()

        self.max_rooms = 30
        self.max_room_size = 10
        self.min_room_size = 6

        self.max_items_per_room = 2
        self.max_monsters_per_room = 3

        self.rooms = []

    def initialize_tiles(self):
        tiles = [[Tile(True, x, y) for y in range(self.height)] for x in range(self.width)]
        return tiles

    def make_map(self, player, entities):
        '''
        Procedurally generate a random map layout.
        '''
        rooms = []

        for r in range(self.max_rooms):
            w = randint(self.min_room_size, self.max_room_size)
            h = randint(self.min_room_size, self.max_room_size)
            # random position without going out of the boundaries of the map
            x = randint(0, self.width - w - 1)
            y = randint(0, self.height - h - 1)

            new_room = Rect(x, y, w, h)

            for other_room in rooms:
                if new_room.is_intersecting(other_room):
                    break
            else:
                self.create_room(new_room)
                if not rooms:
                    self.place_player(new_room, player)
                else:
                    previous_room = rooms[-1]
                    self.create_tunnels(previous_room, new_room)
                    self.place_entities(new_room, entities)

                rooms.append(new_room)

        self.update_tunnels_after_level_generation()
        self.rooms = rooms
        # still experimental, will comment out if its REALLY causing problems
        # Also, this must run AFTER assigning rooms to self.rooms
        # because it uses the attribute
        self.place_doors()

    def place_player(self, room, player):
        '''
        Randomly position player entity in the room.
        '''
        player.x = randint(room.x1 + 1, room.x2 - 1)
        player.y = randint(room.y1 + 1, room.y2 - 1)

    def place_entities(self, room, entities):
        # get a random number of monsters
        number_of_monsters = randint(0, self.max_monsters_per_room)
        number_of_items = randint(0, self.max_items_per_room)

        for i in range(number_of_monsters):
            # choose a random location in the room
            x = randint(room.x1 + 1, room.x2 - 1)
            y = randint(room.y1 + 1, room.y2 - 1)

            tile_is_occupied = any([e for e in entities if e.x == x and e.y == y])

            if not tile_is_occupied:
                if randint(0, 100) < 80:
                    # 80% chance for an orc to spawn
                    monster = Enemy(
                        x, y, 
                        'o', tcod.desaturated_green, 'Orc',
                        fighter=Fighter(hp=10, defense=0, power=3, accuracy=35),
                        # just giving it a random inventory size
                        inventory=Inventory(20)
                    )
                    for i in range(monster.soft_max_inventory):
                        loot_chance = randint(1, 10) < 3
                        if loot_chance:
                            monster.inventory.append(Potion(0, 0, **items.potion_of_healing))
                else:
                    # 20% chance for a troll to spawn
                    monster = Enemy(
                        x, y, 
                        'T', tcod.darker_green, 'Troll',
                        fighter=Fighter(hp=16, defense=1, power=4, accuracy=50),
                        inventory=Inventory(20)
                    )
                    for i in range(monster.soft_max_inventory):
                        loot_chance = randint(1, 10) < 2
                        if loot_chance:
                            monster.inventory.append(Scroll(0, 0, **items.potion_of_healing))
                entities.append(monster)

        for i in range(number_of_items):
            x = randint(room.x1 + 1, room.x2 - 1)
            y = randint(room.y1 + 1, room.y2 - 1)

            tile_is_occupied = any([e for e in entities if e.x == x and e.y == y])

            if not tile_is_occupied:
                item_chance = randint(0, 100)
                if item_chance < 50:
                    item = Potion(x, y, **items.potion_of_healing)
                elif item_chance < 62:
                    item = Scroll(x, y, **items.scroll_of_fireball)
                elif item_chance < 74:
                    item = Scroll(x, y, **items.scroll_of_confuse_monster)
                elif item_chance < 86:
                    item = Scroll(x, y, **items.scroll_of_lightning)
                else:
                    item = Scroll(x, y, **items.scroll_of_strength)
                entities.append(item)

    def place_item(self, x, y, **kwargs):
        item_chance = randint(0, 100)
        if item_chance < 50:
            self.place_potion(x, y)
        else:
            self.place_scroll(x, y)

    def place_potion(self, x, y):
        pass

    def place_scroll(self, x, y):
        pass
 
    def create_tunnels(self, prev_room, new_room):
        new_x, new_y = new_room.center()
        prev_x, prev_y = prev_room.center()

        if randint(0, 1) == 1:
            # move horizontally, and then vertically
            self.create_h_tunnel(prev_x, new_x, prev_y)
            self.create_v_tunnel(prev_y, new_y, new_x)
        else:
            # move vertically, and then horizontally
            self.create_v_tunnel(prev_y, new_y, prev_x)
            self.create_h_tunnel(prev_x, new_x, new_y)

    def create_room(self, room):
        '''
        Iterate through the tiles of a rectangle object and make them passable.
        '''
        for x in range(room.x1 + 1, room.x2):
            for y in range(room.y1 + 1, room.y2):
                self.tiles[x][y].blocked = False
                self.tiles[x][y].block_sight = False

    def create_h_tunnel(self, x1, x2, y):
        '''
        Create a horizontal tunnel that should connect two rooms or to a vertical tunnel.
        '''
        for x in range(min(x1, x2), max(x1, x2) + 1):
            self.tiles[x][y].blocked = False
            self.tiles[x][y].block_sight = False

            if self.is_tile_a_tunnel(x, y):
                self.tiles[x][y] = Tunnel(False, x, y)
    

    def create_v_tunnel(self, y1, y2, x):
        '''
        Create a vertical tunnel that should connect two rooms or to a horizontal tunnel.
        '''
        for y in range(min(y1, y2), max(y1, y2) + 1):
            self.tiles[x][y].blocked = False
            self.tiles[x][y].block_sight = False

            if self.is_tile_a_tunnel(x, y):
                self.tiles[x][y] = Tunnel(False, x, y)

    def is_blocked_by_tiling(self, x, y):
        '''
        Returns true if the tile at x, y is blocked
        '''

        if self.tiles[x][y].blocked:
            return True

        return False

    def is_tile_a_tunnel(self, x, y):
        '''
        Return True if the tile at x, y does not provide free adjacent walking space.
        '''
        return (
            # is tile part of horizontal tunnel?
            (self.tiles[x][y + 1].blocked and self.tiles[x][y - 1].blocked) or

            # is tile part of vertical tunnel?
            (self.tiles[x + 1][y].blocked and self.tiles[x - 1][y].blocked) or 

            # is tile in tunnel and at intersection of other tunnels?
            (
                self.tiles[x + 1][y + 1].blocked and self.tiles[x + 1][y - 1].blocked and
                self.tiles[x - 1][y + 1].blocked and self.tiles[x - 1][y - 1].blocked
            )
        )
        
    def update_tunnels_after_level_generation(self):
        '''
        Performs a final check to see if previously carved out tunnels overlap with newer generated rooms.
        If they do, mark them as no longer being tunnels.
        '''
        for y in range(self.height):
            for x in range(self.width):
                tile = self.tiles[x][y]
                if isinstance(tile, Tunnel) and not self.is_tile_a_tunnel(x, y):
                    self.tiles[x][y] = Tile(False, x, y)

    def place_doors(self):
        '''
        Place doors on the map. 
        '''
        for room in self.rooms:
            for x, y in room.perimeters():
                self.place_doors_at_tile(x, y)

    def place_doors_at_tile(self, x, y):
        '''
        Helper function that attempts to place a door around the given coordinates of a tile.
        It checks each of the cardinal directions of the tile, testing whether that neighboring tile is a tunnel.
        The neighboring tile being a tunnel is a good indication that it is also the entrance to the room, so we can place a door here.
        '''

        for x, y, orientation in (
            (x, y + 1, 'h'), (x, y - 1, 'h'), 
            (x + 1, y, 'v'), (x - 1, y, 'v')
        ):
            tile = self.tiles[x][y]
            if isinstance(tile, Tunnel) and not isinstance(tile, Door):
                self.roll_for_door(x, y, orientation)

    def roll_for_door(self, x, y, orientation):
        if randint(0, 1) == 1:
            self.tiles[x][y] = Door(orientation, True, x, y)