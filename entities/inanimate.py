from .entity import Entity
from game_state import RenderOrder

class Inanimate(Entity):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, render_order=RenderOrder.ITEM, blocks=False)

class Container(Inanimate):
    pass

class Chest(Container):
    pass