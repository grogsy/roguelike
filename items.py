import item_functions
from game_messages import Message
import tcod

class UseEffect:
    def __init__(self, effect_function, requires_target=False, target_msg=Message('Select target.', tcod.light_cyan), **kwargs):
        self.target_msg = target_msg
        self.requires_target = requires_target
        self.effect_function = effect_function

        self.kwargs = kwargs

    def __call__(self, *args, **kwargs):
        kwargs.update(self.kwargs)
        return self.effect_function(*args, **kwargs)

potion_of_healing = {
    'name': 'Potion of Healing',
    'char': '!',
    'color': tcod.violet,
    'use_effect': UseEffect(effect_function=item_functions.heal, heal_amount=range(10, 25))
}

scroll_of_lightning = {
    'name': 'Scroll of Lightning',
    'char': '#',
    'color': tcod.yellow,
    'use_effect': UseEffect(effect_function=item_functions.cast_lightning, damage_type="lightning", base_damage=20, max_range=5)
}

scroll_of_fireball = {
    'name': 'Scroll of Fireball',
    'char': '#',
    'color': tcod.red,
    'use_effect': UseEffect(
                    effect_function=item_functions.cast_fireball, 
                    base_damage=12, damage_type='fire', radius=3,
                    requires_target=True
                  )
}

scroll_of_confuse_monster = {
    'name': 'Scroll of Confuse Monster',
    'char': '#',
    'color': tcod.light_pink,
    'use_effect': UseEffect(effect_function=item_functions.cast_confuse, debuff_duration=10, requires_target=True)
}

scroll_of_strength = {
    'name': 'Scroll of Strength',
    'char': '#',
    'color': tcod.lime,
    'use_effect': UseEffect(effect_function=item_functions.cast_strength_buff, base_amount=3, duration=60)
}

scroll_of_magic_mapping = {
    'name': 'Scroll of Magic Mapping',
    'char': '#',
    'color': tcod.light_blue,
    'use_effect': UseEffect(effect_function=item_functions.reveal_floor)
}

scroll_of_teleport = {
    'name': 'Scroll of Teleport',
    'char': '#',
    'color': tcod.lighter_magenta,
    'use_effect': UseEffect(effect_function=item_functions.teleport)
}