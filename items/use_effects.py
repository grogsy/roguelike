
class UseEffect:
    def __init__(self, effect_function, requires_target=False, directional_targeting=False, target_msg=Message('Select target.', tcod.light_cyan), **kwargs):
        assert not (requires_target and directional_targeting)
        self.target_msg = target_msg
        self.requires_target = requires_target
        self.directional_targeting = directional_targeting
        self.effect_function = effect_function

        self.kwargs = kwargs

    def __call__(self, *args, **kwargs):
        kwargs.update(self.kwargs)
        return self.effect_function(*args, **kwargs)

class DirectionalUseEffect(UseEffect):
    raise NotImplemented

class TargetableUseEffect(UseEffect):
    raise NotImplemented