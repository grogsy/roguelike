import tcod
import random
import copy
from uuid import uuid4

from .entity import Entity
from .util import entity_on_tile, is_same_entity_name

from game_messages import message
from game_state import RenderOrder

class Item(Entity):
    def __init__(self, *args, use_effect=None, **kwargs):
        super().__init__(*args, **kwargs, blocks=False, render_order=RenderOrder.ITEM)
        self.use_effect = use_effect

    def use(self, *args, **kwargs):
        owner = kwargs.get('user')
        results = []
        results.extend(self.use_effect(*args, **kwargs))

        return results

class Readable:
    def use(self, *args, **kwargs):
        results = []
        results.append(message(message=f"You read from the {self.name}."))
        results.extend(super().use(*args, **kwargs))

        return results

class Consumable(Item):
    def use(self, *args, **kwargs):
        owner = kwargs.get('user')
        results = super().use(*args, **kwargs)
        for r in results:
            if r.get('consumed'):
                owner.remove_item(self)
                break
        
        return results

class Scroll(Readable, Consumable):
    pass

class Potion(Consumable):
    pass

class Stackable(Item):
    def __init__(self, *args, stack_count=1, **kwargs):
        super().__init__(*args, **kwargs)
        self.stack_count = stack_count

    def __str__(self):
        return f"{self.name} x{self.stack_count}"

class Throwable:
    def use(self, *args, **kwargs):
        # TODO complete this method
        results = [message(message=f"You throw the {self.name}")]
        results.extend(super().use(*args, **kwargs))

        return results

class Projectile(Throwable, Stackable):
    def use(self, *args, **kwargs):
        owner = kwargs.get('user')
        results = [message(message=f"You throw the {self.name}.")]
        results.extend(self.use_effect(*args, source=self, **kwargs))
        for res in results:
            if res.get('consumed'):
                # when you throw items and have the chance to retrieve some of them back
                drop_chance = random.randint(1, 10) <= 4 or True
                if drop_chance:
                    x = res['landing_x']
                    y = res['landing_y']
                    entities = kwargs.get('entities')
                    for entity in entities:
                        if entity_on_tile(entity, x, y) and is_same_entity_name(entity, self):
                            entity.stack_count += 1
                            break
                    else:
                        copy_item = copy.copy(self)
                        copy_item.x = x
                        copy_item.y = y
                        copy_item.id = str(uuid4())
                        copy_item.stack_count = 1
                        entities.append(copy_item)
                self.stack_count -=1 
                if not self.stack_count:
                    owner.remove_item(self)

        return results

# not implemented
class Knife(Projectile):
    def use(self, *args, **kwargs):
        pass

class Book(Readable, Item):
    pass

class Guld(Stackable):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs, name='Guld', char='$', color=tcod.gold, use_effect=None)
    def use(self, *args, **kwargs):
        return [
           message(message="You cannot use money this way.") 
        ]

    def __str__(self):
        return f"{self.stack_count} guld"