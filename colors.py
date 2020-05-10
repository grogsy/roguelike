import tcod

class Colors:
    '''
    A generic container to hold game object colors
    '''

    player         = tcod.white
    npc            = tcod.yellow
    dark_ground    = tcod.Color(83, 83, 99)
    dark_wall      = tcod.Color(19, 19, 23)
    dark_tunnel    = tcod.Color(33, 33, 54)
    light_wall     = tcod.Color(130, 110, 50)
    light_ground   = tcod.Color(94, 86, 60)
    light_tunnel   = tcod.Color(61, 56, 40)
    # unexplored     = tcod.Color(1, 1, 1)
    unexplored     = tcod.Color(10, 10, 1)