import tcod
import textwrap
from game_state import GameStates

from util import drop_dead_entity_inventory

class Message:
    def __init__(self, text, color=tcod.white):
        self.text = text
        self.color = color

    def __repr__(self):
        return self.text

# deferred import due to circular dependancy
from game_state.death_functions import kill_monster, kill_player

class MessageLog:
    '''
    args:
        x        -> int. How far from the left messages should be displayed
        width    -> int. Width size of the message container.
        height   -> int. Height size of the message container.
    '''
    def __init__(self, parent, x, width, height):
        self.messages = []
        self.parent = parent
        self.x = x
        self.width = width
        self.height = height

    def add_message(self, message):
        new_msg_lines = textwrap.wrap(message.text, self.width)

        for line in new_msg_lines:
            if len(self.messages) == self.height:
                del self.messages[0]

            self.messages.append(Message(line, message.color))

    def render(self):
        y = 1
        for message in self.messages:
            tcod.console_set_default_foreground(self.parent.console, message.color)
            tcod.console_print_ex(self.parent.console, self.x, y, tcod.BKGND_NONE, tcod.LEFT, message.text)
            y += 1

    def parse_turn_results(self, results, entities, player_logger=None):
        new_game_state = None
        for result in results:
            message                 = result.get('message')
            dead_entity             = result.get('dead')
            item_added              = result.get('item_added')
            item_consumed           = result.get('consumed')
            item_dropped            = result.get('item_dropped')
            targeting               = result.get('requires_targeting')
            targeting_cancelled     = result.get('targeting_cancelled')

            if message:
                self.add_message(message)
            if targeting:
                new_game_state = GameStates.TARGETING
            if targeting_cancelled:
                new_game_state = GameStates.PLAYER_TURN
                self.add_message(Message('Targeting cancelled.'))
            if dead_entity:
                if dead_entity.name == 'Player':
                    message, new_game_state = kill_player(dead_entity)
                else:
                    if player_logger:
                        player_logger.write_entry(dead_entity)
                    # while dead_entity.inventory.items:
                    #     dropped_item = dead_entity.inventory.items.pop()
                    #     dropped_item.x = dead_entity.x
                    #     dropped_item.y = dead_entity.y
                    #     entities.append(dropped_item)
                    drop_dead_entity_inventory(dead_entity, entities)
                    damage_source = result.get('cause')
                    message = kill_monster(dead_entity, damage_source)
                
                self.add_message(message)
            if new_game_state == GameStates.PLAYER_DEAD:
                break
            elif item_added:
                new_game_state = GameStates.ENEMY_TURN
            if item_consumed or item_dropped: 
                if result.get('source') == 'Player':
                    new_game_state = GameStates.ENEMY_TURN

        return new_game_state