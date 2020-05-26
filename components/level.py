import tcod
from game_messages import message

class Level:
    def __init__(self, current_level=1, current_xp=0, level_up_base=50, level_up_factor=25):
        self.current_level = current_level
        self.xp = current_xp
        self.level_up_base = level_up_base
        self.level_up_factor = level_up_factor

    @property
    def xp_to_next_level(self):
        return self.level_up_base + self.current_level * self.level_up_factor

    def add_xp(self, xp_amt):
        results = []
        self.xp += xp_amt

        if self.xp > self.xp_to_next_level:
            self.xp -= self.xp_to_next_level
            self.current_level += 1

            results.append(message(
                player_level_up=True, 
                message=f"Congratulations! You have reached experience level {self.current_level}",
                color=tcod.yellow
            ))

        return results