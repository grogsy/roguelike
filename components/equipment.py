# if this throws an import error sometime in the future 
# just move it to items.equipment, or something...
from entities.items import EquipmentSlots
from game_messages import message

class Equipment:
    def __init__(self, owner, main_hand=None, off_hand=None):
        self.owner = owner
        self.main_hand = main_hand
        self.off_hand = off_hand


    @property
    def max_hp_bonus(self):
        bonus = 0

        if self.main_hand is not None:
            bonus += self.main_hand.max_hp_bonus

        if self.off_hand is not None:
            bonus += self.off_hand.max_hp_bonus

    def equip(self, item):
        results = []

        slot = item.equip_slot

        if slot == EquipmentSlots.MAIN_HAND:
            if self.main_hand is None:
                self.main_hand = item
                equipped=True
                msg = f"You equip the {item.name}."
            else:
                equipped=False
                msg= f"You are already wearing something in that slot ({self.main_hand})."

        if equipped:
            results.append(
                message(equipped=equipped, message=msg, item=item, source=self.owner)
            )
        else:
            results.append(message(equipped=equipped, message=msg))

        return results