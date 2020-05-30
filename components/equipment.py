# if this throws an import error sometime in the future 
# just move it to items.equipment, or something...
from entities.items import EquipmentSlots
from game_messages import message

class Equipment:
    def __init__(
        self, 
        owner, 
        main_hand=None, 
        off_hand=None,
        chest=None,
        cloak=None,
        gloves=None,
        boots=None,
        left_ring=None,
        right_ring=None

    ):
        self.owner = owner
        self.main_hand = main_hand
        self.off_hand = off_hand
        self.chest = chest
        self.cloak = cloak
        self.gloves = gloves
        self.boots = boots
        self.left_ring = left_ring
        self.right_ring = right_ring

        self.slots = {
            EquipmentSlots.MAIN_HAND: self.main_hand,
            EquipmentSlots.OFF_HAND: self.off_hand,
            EquipmentSlots.CHEST: self.chest,
            EquipmentSlots.CLOAK: self.cloak,
            EquipmentSlots.GLOVES: self.gloves,
            EquipmentSlots.BOOTS: self.boots,
            "LEFT_RING": self.left_ring,
            "RIGHT_RING": self.right_ring
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

        if slot == EquipmentSlots.RING:
            if not self.slots["LEFT_RING"]:
                self.slots["LEFT_RING"] = item
            elif not self.slots["RIGHT_RIGHT"]:
                self.slots["RIGHT_RING"] = item
            equipped = True
            msg = f"You equip the {item.name}."
        elif self.slots[slot] is None:
            self.slots[slot] = item
            equipped = True
            msg = f"You equip the {item.name}."
        else:
            equipped = False
            if slot == EquipmentSlots.RING:
                msg = "You already wear a ring on both hands!"
            else:
                msg = f"You are already wearing something in that slot ({self.slots[slot]})."

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

        if slot == EquipmentSlots.RING:
            if self.slots["LEFT_RING"] == item:
                self.slots["LEFT_RING"] = None
            else:
                self.slots["RIGHT_RING"] = None
        else:
            self.slots[slot] = None

        results.append(message(unequipped=True, item=item, source=self.owner, message=f"You unequip your {item.name}."))

        return results