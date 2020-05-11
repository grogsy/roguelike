import tcod
import random
from game_messages import Message

class BasicMonster:
    '''
    The AI component of enemies.
    '''
    def take_turn(self, target, fov_map, game_map, entities):
        results = []

        this = self.owner
        if fov_map.is_in_fov(this.x, this.y):
        # if tcod.map_is_in_fov(fov_map, this.x, this.y):
            if this.distance_to(target) >= 2:
                this.move_astar(target, game_map, entities)
            elif target.fighter.hp > 0:
                results.extend(this.fighter.attack(target))

        return results

class ConfusedMonster:
    def __init__(self, prev_ai, number_of_turns=10):
        self.prev_ai = prev_ai
        self.number_of_turns = number_of_turns

    def take_turn(self, target, fov_map, game_map, entities):
        results = []

        if self.number_of_turns > 0:
            random_x = self.owner.x + random.randint(0, 2) - 1
            random_y = self.owner.y + random.randint(0, 2) - 1

            if random_x != self.owner.x and random_y != self.owner.y:
                self.owner.move_towards(random_x, random_y, game_map, entities)
        
            self.number_of_turns -= 1
        else:
            self.owner.ai = self.prev_ai
            results.append({
                'message': Message(f"The {self.owner.name} is no longer confused.")
            })

        return results
