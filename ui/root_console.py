import textwrap
import tcod
from game_state import GameStates, RenderOrder

from entities.items import Projectile, Readable, Potion, Stackable
from util.identity import is_item, is_container, is_door, is_stairs, is_equipable

from .menu import Menu
from .panel import Panel
from .stats import StatsView

from constants import INVENTORY_CONTEXT

from util.misc import is_on_same_tile

class RootConsole:
    '''
    A wrapper class over the root game window.
    '''

    def __init__(self, font_family, width, height, map_height):

        tcod.console_set_custom_font(font_family, tcod.FONT_TYPE_GRAYSCALE | tcod.FONT_LAYOUT_TCOD)
        tcod.console_init_root(width, height, title='Roguelike', fullscreen=False)

        self.width = width
        self.height = height
        self.console = tcod.console_new(width, height)

        # components
        self.panel = Panel(
            parent=self,
            width=self.width,
            screen_height=self.height,
            height=self.height - map_height
        )
        self.inventory_menu = Menu(
            parent=self,
            menu_width=50,
            header_label="Inventory"
        )
        self.main_menu = Menu(
            parent=self,
            menu_width=50,
            header_label='Home'
        )

        self.stats_view = StatsView(parent=self, width=50)

    def render_all(self, player, entities, game_map, fov_map, mouse_event, game_state): #, message_log):
        self.draw_map(game_map, fov_map)

        if game_state == GameStates.TARGETING:
            self.prev_tile_color = game_map.tiles[player.targeting_x][player.targeting_y].color
            tcod.console_set_char_background(self.console, player.targeting_x, player.targeting_y, tcod.dark_cyan, tcod.BKGND_SET)

        for entity in sorted(entities, key=lambda e: e.render_order.value):
            self.draw_entity(entity, fov_map)

        tcod.console_blit(self.console, 0, 0, self.width, self.height, 0, 0, 0)

        self.panel.render(player, entities, game_map, fov_map, mouse_event) #, message_log)

        if game_state == GameStates.CHECK_PLAYER_STATS:
            player.stat_logger.render()
        if game_state == GameStates.CHECK_CHAR_STATS:
            self.stats_view.render(player)
        # if game_state == GameStates.VIEW_EQUIP:
        #     opts = []
        #     for slot, item in player.equipment.slots.items():
        #         if item:
        #             item_msg = item.name
        #         else:
        #             item_msg = "Nothing equipped."
        #         opts.append(f"{slot.name}: {item_msg}")
        #     Menu(self, 50, "Equipped Items.").render(opts)

    def clear_all(self, entities, game_map, game_state):
        for entity in entities:
            if entity.name == 'Player' and game_state == GameStates.TARGETING:
                tcod.console_set_char_background(self.console, entity.targeting_x, entity.targeting_y, self.prev_tile_color, tcod.BKGND_SET)
            self.clear_entity(entity)

    def clear_entity(self, entity):
        tcod.console_put_char(self.console, entity.x, entity.y, ' ', tcod.BKGND_NONE)

    def draw_entity(self, entity, fov_map):
        if entity.x or entity.y:
                
            if fov_map.is_in_fov(entity.x, entity.y):
                tcod.console_set_default_foreground(self.console, entity.color)
                tcod.console_put_char(self.console, entity.x, entity.y, entity.char, flag=tcod.BKGND_NONE)

    def draw_map(self, game_map, fov_map):
        height = game_map.height
        width = game_map.width
        
        # label_rooms(console, game_map)

        if fov_map.recompute:
            for y in range(height):
                for x in range(width):
                    tile = game_map.tiles[x][y]
                    visible = fov_map.is_in_fov(x, y)

                    if visible:
                        tile.render(self.console, in_fov=True)
                        tile.explored = True
                    else:
                        tile.render(self.console, in_fov=False)

    def clear_old_tiles(self, game_map):
        for x in range(game_map.width):
            for y in range(game_map.height):
                tcod.console_put_char(self.console, x, y, ' ', flag=tcod.BKGND_NONE)

    def get_entities_at_mouse_cursor(self, mouse_event, entities, fov_map, game_map):
        x, y = mouse_event.cx, mouse_event.cy

        names = []
        for entity in entities:
            if entity.x == x and entity.y == y and fov_map.is_in_fov(entity.x, entity.y):
                if entity.name == 'Player':
                    names.append("You see yourself.")
                elif entity.name[0].lower() in 'aeiou':
                    names.append(f"You see an {entity.name}")
                elif entity.render_order == RenderOrder.CORPSE:
                    names.append(f"You see {entity.name}")
                else:
                    names.append(f"You see a {entity.name}")
        
        width = game_map.width
        height = game_map.height
        for y in range(height):
            for x in range(width):
                tile = game_map.tiles[x][y]
                if tile.explored and tile.x == mouse_event.cx and tile.y == mouse_event.cy and is_door(tile):
                    if tile.opened:
                        door_status = "an open"
                    else:
                        door_status = "a closed"
                    names.append(f"This is {door_status} door.")
            
        names = '\n'.join(names)

        return names

    def get_entities_at_player_location(self, player, entities):
        names = []
        for entity in entities:
            if not entity.name == player.name and entity.x == player.x and entity.y == player.y:
                lines = textwrap.wrap(f"You see {entity}.", 35)
                for line in lines:
                    names.append(line)

        names = '\n'.join(names)

        return names

    def get_tile_at_player_locations(self, player, game_map):
        tile = game_map.tiles[player.x][player.y]
        if is_stairs(tile):
            return f"You see stairs here({tile.level}).\n"
        else:
            return ""


    def clear(self):
        tcod.console_clear(self.console)

    def flush(self):
        tcod.console_flush()

    def render_inventory(self, player, entities, game_state, *args, **kwargs):
        if game_state == GameStates.SHOW_INVENTORY:
            self.inventory_menu.header_label = 'Inventory'
        elif game_state == GameStates.DROP_INVENTORY:
            self.inventory_menu.header_label = 'Drop which item?'
        if game_state == GameStates.READABLE_INVENTORY:
            self.inventory_menu.header_label = 'Read which item?'
            self.inventory_context = [item for item in player.inventory.items if isinstance(item, Readable)]
        elif game_state == GameStates.LOOTING:
            container = kwargs.get('container')
            if container:
                self.inventory_menu.header_label = f"What do you want to retrieve from the {container.name}?"
                self.inventory_context = container.inventory.items
            else:
                self.inventory_menu.header_label = 'Pick up which item?'
                self.inventory_context = [item for item in entities if is_item(item) and is_on_same_tile(player, item)]
        elif game_state == GameStates.THROWABLE_INVENTORY:
            self.inventory_menu.header_label = 'Throw which item?'
            self.inventory_context = [item for item in player.inventory.items if isinstance(item, Projectile)]
        elif game_state == GameStates.QUAFFABLE_INVENTORY:
            self.inventory_menu.header_label = 'Drink which item?'
            self.inventory_context = [item for item in player.inventory.items if isinstance(item, Potion)]
        elif game_state == GameStates.EQUIPABLE_INVENTORY:
            self.inventory_menu.header_label = "Select item to equip."
            self.inventory_context = [item for item in player.inventory.items if is_equipable(item)]
        elif game_state == GameStates.UNEQUIP:
            self.inventory_menu.header_label = "Choose an item to unequip."
            self.inventory_context = [equip for equip in player.equipment.slots.values() if equip is not None]
        else:
            self.inventory_context = player.inventory.items
            
        self.inventory_menu.render(self.inventory_context)