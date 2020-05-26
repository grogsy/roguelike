import tcod
from components.fighter import Fighter

orc = {
    'char': 'o',
    'color': tcod.desaturated_green,
    'name': 'Orc',
}

troll = {
    'char': 'T',
    'color': tcod.darker_green,
    'name': "Troll",
}

enemies = {
    'orc': orc,
    'troll': troll
}

fighters = {
    'orc': {
        'hp': 10,
        'defense': 0,
        'power': 3,
        'accuracy': 35,
        'xp': 5
    },
    'troll': {
        'hp': 16,
        'defense': 1,
        'power': 4,
        'accuracy': 50,
        'xp': 12
    }
}