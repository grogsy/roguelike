from enum import Enum

class RenderOrder(Enum):
    '''
    A class representing the rendering order of entities drawn onto the screen.
    This ensures that moveable entities appear 'on top' of still entities.
    '''
    CORPSE = 1
    ITEM   = 2
    ACTOR  = 3