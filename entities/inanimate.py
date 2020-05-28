import tcod
from .entity import Entity
from components.inventory import Inventory
from items.util import generate_random_item
from game_state import RenderOrder

class Inanimate(Entity):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, render_order=RenderOrder.ITEM, blocks=False)

class Container(Inanimate):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.inventory = Inventory(26)
        self.initialize_loot()

    def __str__(self):
        if not self.inventory:
            msg = f"an empty {self.name}"
        else:
            msg = f"a {self.name} containing {len(self.inventory)} items"

        return msg

    def initialize_loot(self):
        for i in range(5):
            self.inventory.append(generate_random_item())

    def remove_item(self, item):
        self.inventory.remove_item(item)

class Chest(Container):
    pass

def create_chest(*args, **kwargs):
    chest = Chest(*args, '(', tcod.Color(89, 60, 31), 'Chest', **kwargs)

    return chest