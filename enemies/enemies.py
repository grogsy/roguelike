import tcod
from components.fighter import Fighter

orc = {
    'level': 1,
    'char': 'o',
    'color': tcod.desaturated_green,
    'name': 'Orc',
}

troll = {
    'level': 2,
    'char': 'T',
    'color': tcod.darker_green,
    'name': "Troll",
}

bat = {
    'char': 'B',
    'color': tcod.white,
    'name': 'Bat'
}

rat = {
    'char': 'r',
    'color': tcod.brass,
    'name': 'Rat'
}

kobold = {
    'char': 'k',
    'color': tcod.brass,
    'name': 'Kobold'
}



enemies = {
    'orc': orc,
    'troll': troll,
    # 'bat': bat,
    # 'rat': rat,
    # 'kobold': kobold
}

fighters = {
    'orc': {
        'hp': 3,
        'power': 2,
        'defense': 0,
        'constitution': 3,
        'strength': 3,
        'intelligence': 0,
        'dexterity': 3,
        'xp': 76
    },
    'troll': {
        'hp': 3,
        'power': 2,
        'defense': 0,
        'constitution': 6,
        'strength': 5,
        'intelligence': 0,
        'dexterity': 3,
        'xp': 15
    }
}

# fighters = {
#     'orc': {
#         'hp': 10,
#         'defense': 0,
#         'power': 3,
#         'accuracy': 35,
#         'xp': 5
#     },
#     'troll': {
#         'hp': 16,
#         'defense': 1,
#         'power': 4,
#         'accuracy': 50,
#         'xp': 12
#     }, 
#     'bat': {
#         'hp': 6,
#         'defense': 0,
#         'power': 2,
#         'accuracy': 75,
#         'xp': 6
#     },
#     'rat': {
#         'hp': 3,
#         'defense': 1,
#         'power': 1,
#         'accuracy': 70,
#         'xp': 2
#     },
#     'kobold': {
#         'hp': 5,
#         'defense': 3,
#         'power': 2,
#         'accuracy': 65,
#         'xp': 8
#     }
# }