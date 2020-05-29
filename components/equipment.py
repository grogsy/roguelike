# if this throws an import error sometime in the future 
# just move it to items.equipment, or something...
from entities.items import EquipmentSlots
from game_messages import message

class Equipment:
    def __init__(self, owner, main_hand=None, off_hand=None):
        self.owner = owner
        self.main_hand = main_hand
        self.off_hand = off_hand

        self.slots = {
            EquipmentSlots.MAIN_HAND: self.main_hand,
            EquipmentSlots.OFF_HAND: self.off_hand
        }


    @property
    def max_hp_bonus(self):
        bonus = 0
        for equip in self.slots.values():
            if equip is not None:
                bonus += equip.max_hp_bonus

        return bonus

    @property
    def power_bonus(self):
        bonus = 0
        for equip in self.slots.values():
            if equip is not None:
                bonus += equip.power_bonus

        return bonus
    
    @property
    def defense_bonus(self):
        bonus = 0
        for equip in self.slots.values():
            if equip is not None:
                bonus += equip.defense_bonus

        return bonus

    def equip(self, item):
        results = []

        slot = item.equip_slot

        if self.slots[slot] is None:
            self.slots[slot] = item
            equipped = True
            msg = f"You equip the {item.name}."
        else:
            equipped = False
            msg= f"You are already wearing something in that slot ({self.slots[slot]})."

        if equipped:
            results.append(
                message(equipped=equipped, message=msg, item=item, source=self.owner)
            )
        else:
            results.append(message(equipped=equipped, message=msg))

        return results

    def unequip(self, item):
        results = []
        slot = item.equip_slot

        self.slots[slot] = None

        results.append(message(unequipped=True, item=item, source=self.owner, message=f"You unequip your {item.name}."))

        return results