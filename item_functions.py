import random
import tcod
from game_messages import Message
from entity import Entity, Item, Scroll, Potion
from components.ai import ConfusedMonster
from components.fighter import Buff
from map_objects.tile import Tunnel, Door

def heal(heal_amount, *args, **kwargs):
    user = kwargs.get('user')
    
    results = []

    if not isinstance(user, Entity) or not user.fighter:
        results.append({'consumed': False, 'message': Message("You can't heal that.", tcod.red) })
    else:
        user.fighter.hp += random.randint(min(heal_amount), max(heal_amount))

        if user.fighter.hp >  user.fighter.max_hp:
            user.fighter.hp = user.fighter.max_hp

        if user.name == 'Player':
            results.append({ 'source': 'Player', 'consumed': True, 'message': Message("You feel better.", tcod.light_green) })
        else:
            results.append({ 'consumed': True, 'message': Message(f"The {user.name} feels better.") })

    return results

def cast_lightning(base_damage, max_range, *args, **kwargs):
    caster          = kwargs.get('user')
    entities        = kwargs.get('entities')
    fov_map         = kwargs.get('fov_map')
    dmg_type        = kwargs.get('damage_type')
    # damage          = kwargs.get('damage')
    # max_range       = kwargs.get('max_range')

    results = []

    target = None
    closest_distance = max_range + 1

    damage = base_damage

    for entity in entities:
        if entity.fighter and entity != caster and fov_map.is_in_fov(entity.x, entity.y):
            dist = caster.distance_to(entity)

            if dist < closest_distance:
                target = entity
                closest_distance = dist
    if target:
        results.append({
            'consumed': True,
            'source': caster.name,
            'target': target, 
            'message':  Message(f"A lightning bolt strikes {target.name} and deals it {damage} damage.")
        })
        results.extend(target.fighter.take_damage(damage, dmg_type))
    else:
        results.append({
            'consumed': False,
            'source': caster.name,
            'target': None,
            'message': Message('No enemy close enough to strike.', tcod.red)
        })

    return results

def cast_strength_buff(base_amount, duration, *args, **kwargs):
    caster = kwargs.get('user')

    results = []

    increase_amount = base_amount
    attack_buff = Buff(
        effect=increase_amount, duration=duration,
        expire_message=Message(f"Your improved strength fades.", tcod.light_red),
        name="strength_scroll"
    )

    caster.fighter.buffs.add_attack_buff(attack_buff)

    results.append({
        'consumed': True,
        'source': caster.name,
        'message': Message('You feel yourself become stronger!', tcod.light_green)
    })

    return results

def cast_fireball(base_damage, radius, *args, **kwargs):
    entities    = kwargs.get('entities')
    fov_map     = kwargs.get('fov_map')
    target_x    = kwargs.get('target_x')
    target_y    = kwargs.get('target_y')
    caster      = kwargs.get('user')
    dmg_type    = kwargs.get('damage_type')

    results = []
    destroyed_items = []

    damage = base_damage

    if not fov_map.is_in_fov(target_x, target_y):
        results.append({
            'consumed': False,
            'source': caster.name,
            'message': Message('That is out of range.', tcod.red)
        })

        return results

    results.append({
        'consumed': True,
        'source': caster.name,
        'message': Message('The fireball explodes, burning everything around it!')
    })

    for entity in entities:
        if entity.distance(target_x, target_y) <= radius:
            if entity.fighter:
                if entity.name == 'Player':
                    results.append({
                        'message': Message(f"You got caught in the blast radius and suffer {damage} damage.", tcod.light_flame)
                    })
                elif fov_map.is_in_fov(entity.x, entity.y):
                    results.append({
                        'message': Message(f"The {entity.name} burns and takes {damage} damage.")
                    })
                else:
                    results.append({
                        'message': Message("You hear something shriek in burning agony.")
                    })
                results.extend(entity.fighter.take_damage(damage, dmg_type))
            elif isinstance(entity, Item):
                destroyed_items.append(entity)
        
        # this will be very slow. need to change this some time in the future
        for item in destroyed_items:
            for i, entity in enumerate(entities):
                if item.id == entity.id:
                    if not fov_map.is_in_fov(item.x, item.y):
                        results.append({
                            'message': Message(f"You hear the sound of things being burnt to a fiery crisp.")
                        })
                    elif isinstance(item, Scroll):
                        results.append({
                            'message': Message(f"The {item.name} crumbles into ashes!")
                        })
                    elif isinstance(item, Potion):
                        results.append({
                            'message': Message(f"The {item.name} bursts open and shatters!")
                        })

                    entities.pop(i)
                    break

    return results

def cast_confuse(debuff_duration, *args, **kwargs):
    entities    = kwargs.get('entities')
    fov_map     = kwargs.get('fov_map')
    target_x    = kwargs.get('target_x')
    target_y    = kwargs.get('target_y')
    caster      = kwargs.get('user')

    results = []

    if not fov_map.is_in_fov(target_x, target_y):
        results.append({
            'consumed': False,
            'message': Message("Target is out of range", tcod.yellow)
        })

        return results
    
    for entity in entities:
        if entity.ai and entity.x == target_x and entity.y == target_y:
            confused_ai = ConfusedMonster(entity.ai, number_of_turns=debuff_duration)
            confused_ai.owner = entity
            entity.ai = confused_ai

            results.append({
                'consumed': True,
                'source': caster.name,
                'message': Message(f"The {entity.name} is disoriented.")
            })

            break
    else:
        results.append({'consumed': False, 'message': Message('Invalid target.', tcod.yellow)})

    return results

def reveal_floor(*args, **kwargs):
    game_map    = kwargs.get('game_map')
    caster      = kwargs.get('user')
    fov_map     = kwargs.get('fov_map')

    results = []

    # for room in game_map.rooms:
    #     for x in range(room.x1, room.x2 + 1):
    #         for y in range(room.y1, room.y2 + 1):
    #             game_map.tiles[x][y].explored = True
    for x in range(game_map.width):
        for y in range(game_map.height):
            tile = game_map.tiles[x][y]
            if isinstance(tile, Tunnel) or isinstance(tile, Door) or not tile.blocked:
                tile.explored = True

    fov_map.recompute = True

    results.append({
        'consumed': True,
        'source': caster.name,
        'message': Message("All the rooms on this floor have been revealed!")
    })

    return results

def teleport(*args, **kwargs):
    results = []
    game_map = kwargs.get('game_map')
    fov_map = kwargs.get('fov_map')
    caster = kwargs.get('user')

    room = random.choice(game_map.rooms)
    x = random.randint(room.x1 + 1, room.x2 - 1)
    y = random.randint(room.y1 + 1, room.y2 - 1)

    caster.x = x
    caster.y = y

    fov_map.recompute = True

    results.append({
        'consumed': True,
        'source': caster.name,
        'message': Message("Your teleport yourself out of there.")
    })

    return results