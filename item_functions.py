import random
import tcod
from game_messages import Message
from entity import Entity, Item, Scroll, Potion

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

def cast_fireball(base_damage, radius, *args, **kwargs):
    entities    = kwargs.get('entities')
    fov_map     = kwargs.get('fov_map')
    target_x    = kwargs.get('target_x')
    target_y    = kwargs.get('target_y')
    caster      = kwargs.get('user')
    dmg_type    = kwargs.get('damage_type')

    results = []

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
                if not fov_map.is_in_fov(entity.x, entity.y):
                    results.append({
                        'message': Message(f"You hear the sound of things being burnt to a fiery crisp.")
                    })
                elif isinstance(entity, Scroll):
                    results.append({
                        'message': Message(f"The {entity.name} crumbles into ashes!")
                    })
                elif isinstance(entity, Potion):
                    results.append({
                        'message': Message(f"The {entity.name} bursts open and shatters!")
                    })
                entities.pop(entities.index(entity))

    return results