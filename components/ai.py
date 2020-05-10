import tcod

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