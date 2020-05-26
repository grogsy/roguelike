def create_new_floor(console, game_map, player, entities):
    console.clear_old_tiles(game_map)

    game_map.tiles = game_map.initialize_tiles()
    game_map.make_map(player, entities)

def load_previous_floor(console, game_map, player, entities, curr_level, prev_level):
    next_floor = game_map.floors[prev_level - 1]
    entities.extend(next_floor.entities)

    console.clear_old_tiles(game_map)

    game_map.tiles = next_floor.tiles

    # if we're going DOWN to prev visited floor
    if curr_level < prev_level:
        player.x = next_floor.upstair_x
        player.y = next_floor.upstair_y
    # if we're going UP to prev visited floor
    else:
        player.x = next_floor.downstair_x
        player.y = next_floor.downstair_y

def save_current_floor(game_map, entities):
    this_floor = game_map.floors[game_map.dungeon_level - 1]
    this_floor.tiles = game_map.tiles
    this_floor.entities = entities