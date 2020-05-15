from enum import Enum

class GameStates(Enum):
    PLAYER_TURN         = 1
    ENEMY_TURN          = 2
    PLAYER_DEAD         = 3
    SHOW_INVENTORY      = 4
    DROP_INVENTORY      = 5
    TARGETING           = 6
    CHECK_PLAYER_STATS  = 7
    READABLE_INVENTORY  = 8
    LOOTING             = 9
    CHECK_CHAR_STATS    = 10
    THROWABLE_INVENTORY = 11
    QUAFFABLE_INVENTORY = 12