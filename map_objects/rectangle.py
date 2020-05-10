class Rect:
    '''
    A helper class used for generating rooms on the map.
    This class' attributes are just coordinates describing the boundaries of the room.
    '''
    def __init__(self, x, y, w, h):
        self.x1 = x
        self.x2 = x + w
        self.y1 = y
        self.y2 = y + h

    def center(self):
        center_x = (self.x1 + self.x2) // 2
        center_y = (self.y1 + self.y2) // 2

        return (center_x, center_y)

    def is_intersecting(self, other):
        '''
        Returns True if this rectangle intersects with another one.
        '''

        return (self.x1 <= other.x2 and self.x2 >= other.x1 and
                self.y1 <= other.y2 and self.y2 >= other.y1)

    def perimeters(self):
        '''
        Obtain the perimeters of the rectangle.
        This is useful for things like placing doors.
        This function returns a set because I'm too much of a lazy SOB to deal with overlapping coordinates.
        '''
        p = set()
        # top side
        for x in range(self.x1 + 1, self.x2):
            p.add((x, self.y1 + 1))

        # left side
        for y in range(self.y1 + 1, self.y2):
            p.add((self.x1 + 1, y))

        # right side
        for y in range(self.y1 + 1, self.y2):
            p.add((self.x2 - 1, y))

        # bottom side
        for x in range(self.x1 + 1, self.x2):
            p.add((x, self.y2 - 1))

        return p

    def __repr__(self):
        return f"<Room start({self.x1},{self.y1}), end({self.x2},{self.y2})>"