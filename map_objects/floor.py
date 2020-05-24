class Floor:
    def __init__(self, tiles, entities, downstair_x, downstair_y, upstair_x=None, upstair_y=None):
        self.tiles = tiles
        self.entities = entities
        self.downstair_x = downstair_x
        self.downstair_y = downstair_y
        self.upstair_x = upstair_x
        self.upstair_y = upstair_y