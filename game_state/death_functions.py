import random
import tcod

from game_messages import Message
from .game_states import GameStates
from .render_order import RenderOrder

def kill_player(player):
    player.char = '%'
    player.color = tcod.dark_red

    return Message('You died!', tcod.red), GameStates.PLAYER_DEAD

def kill_monster(monster, damage_source):
    death_message = Message(f"{monster.name} is dead!", tcod.orange)

    corpse_prefix = ''
    if damage_source == 'fire':
        corpse_prefix = random.choice('charred smoked broiled well-done'.split(' '))
    elif damage_source == 'lightning':
        corpse_prefix = random.choice('electrocuted shocked zapped sparkling'.split(' '))
    monster.char = '%'
    monster.color = tcod.dark_red
    monster.blocks = False
    monster.fighter = None
    monster.ai = None
    monster.name = f"the {corpse_prefix} remains of some {monster.name}." if corpse_prefix else f"the remains of some {monster.name}."
    monster.render_order = RenderOrder.CORPSE

    return death_message

def select_corpse_name(entity, damage_source):
    '''
    replace monster name assignment in kill_monster() with a call to this function
    which will generate a name of the corpse based on killing blow type.
    '''
    pass