class Floor:
    def __init__(self, tiles, entities, downstair_x, downstair_y, upstair_x=None, upstair_y=None):
        '''
        A helper class that is used to remember the current state of a given floor
        when the player leaves it.
        '''
        self.tiles = tiles
        self.entities = entities
        self.downstair_x = downstair_x
        self.downstair_y = downstair_y
        self.upstair_x = upstair_x
        self.upstair_y = upstair_y