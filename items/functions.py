import random
import tcod
from game_messages import Message

from entities.entity import Entity
from entities.items import Item, Potion, Readable
from entities.util import get_blocking_entities_at_location, is_enemy
from entities.actors import Enemy

from components.ai import ConfusedMonster, SleepingMonster
from components.fighter import Buff
from map_objects.tile import Tunnel, Door

# TODO: Change all instances of message passing to fit the new message passing interface(game_message.message())

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

def mana_pot(restore_amount, *args, **kwargs):
    user = kwargs.get('user')
    results = []

    user.fighter.mana += random.randint(min(restore_amount), max(restore_amount))
    if user.fighter.mana > user.fighter.max_mana:
        user.fighter.mana = user.fighter.max_mana

    results.append({'source': user.name, 'consumed': True, 'message': Message("You feel more energetic.", tcod.light_azure)})

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
        
        for item in destroyed_items:
            if not fov_map.is_in_fov(item.x, item.y):
                results.append({
                    'message': Message(f"You hear the sound of things being burnt to a fiery crisp.")
                })
            elif isinstance(item, Readable):
                results.append({
                    'message': Message(f"The {item.name} crumbles into ashes!")
                })
            elif isinstance(item, Potion):
                results.append({
                    'message': Message(f"The {item.name} bursts open and shatters!")
                })

            entities.remove(entity)

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

def throw_knife(base_damage, *args, **kwargs):
    entities        = kwargs.get('entities')
    fov_map         = kwargs.get('fov_map')
    game_map        = kwargs.get('game_map')
    dx              = kwargs.get('dx')
    dy              = kwargs.get('dy')
    user            = kwargs.get('user')
    item_source     = kwargs.get('source')

    results = []

    results.append({
        'consumed': True,
        'source': user.name,
    })

    x = user.x + dx
    y = user.y + dy

    entity = get_blocking_entities_at_location(entities, x, y)

    while not entity and not game_map.is_blocked_by_tiling(x + dx, y + dy):
        x += dx
        y += dy
        entity = get_blocking_entities_at_location(entities, x, y)
        if is_enemy(entity):
            break

    damage = base_damage + user.fighter.power + user.fighter.calculate_attack_bonus_from_buffs()

    if entity and is_enemy(entity):
        if fov_map.is_in_fov(entity.x, entity.y):
            results.append({
                'message': Message(f"You hit the {entity.name} dealing {damage} damage.")
            })
        else:
            results.append({
                'message': Message(f"You hit someone with the {item_source.name}.")
            })

        results.extend(entity.fighter.take_damage(damage))

    results[0]['landing_x'] = x
    results[0]['landing_y'] = y

    return results

def cast_magic_missile(base_damage, max_range, mana_cost=0, *args, **kwargs):
    dx = kwargs.get('dx')
    dy = kwargs.get('dy')
    game_map = kwargs.get('game_map')
    fov_map  = kwargs.get('fov_map')
    entities = kwargs.get('entities')
    user = kwargs.get('user')

    if user.fighter.mana < mana_cost:
        return [{
            'message': Message("You do not have enough mana to cast that spell.", tcod.red),
            'targeting_cancelled': True
            }]

    damage = base_damage

    results = [{
        'consumed': True,
        'source': user.name,
        'message': Message('You cast a magic missile spell.')
    }]

    x = user.x + dx
    y = user.y + dy

    entity = get_blocking_entities_at_location(entities, x, y)

    # while not entity or not game_map.is_blocked_by_tiling(x, y) or not (abs(user.x - x) == max_range or abs(user.y - y) == max_range): 
    while not entity and (abs(user.x - x) <= max_range and abs(user.y - y) <= max_range):
        x += dx
        y += dy
        entity = get_blocking_entities_at_location(entities, x, y)
        if is_enemy(entity):
            break

    if entity and is_enemy(entity):
        if fov_map.is_in_fov(entity.x, entity.y):
            results.append({
                'message': Message(f"You hit the {entity.name} dealing {damage} damage.")
            })
        else:
            results.append({
                'message': Message("You hit someone with your spell.")
            })

        results.extend(entity.fighter.take_damage(damage))

    user.fighter.mana -= mana_cost

    return results

def cast_mass_sleep(radius, duration, *args, mana_cost=0, **kwargs):
    entities = kwargs.get('entities')
    caster = kwargs.get('user')
    results = []

    for entity in entities:
        if is_enemy(entity) and entity.ai and entity.distance(caster.x, caster.y) <= radius:
            sleeping_ai = SleepingMonster(entity.ai, duration=duration)
            sleeping_ai.owner = entity
            entity.ai = sleeping_ai

            results.append({
                'message': Message(f"The {entity.name} has fallen into a slumber.")
            })

    caster.fighter.mana -= mana_cost

    results.append({
        'consumed': True,
        'source': caster.name,
    })

    return results