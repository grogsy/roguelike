from enum import Enum, auto

class GameStates(Enum):
    PLAYER_TURN         = auto()
    PLAYER_DEAD         = auto()
    PLAYER_LEVEL_UP     = auto()
    TARGETING           = auto()
    LOOTING             = auto()
    DROP_INVENTORY      = auto()
    SHOW_INVENTORY      = auto()
    READABLE_INVENTORY  = auto()
    THROWABLE_INVENTORY = auto()
    QUAFFABLE_INVENTORY = auto()
    EQUIPABLE_INVENTORY = auto()
    ENEMY_TURN          = auto()
    CHECK_PLAYER_STATS  = auto()
    CHECK_CHAR_STATS    = auto()
    VIEW_EQUIP          = auto()