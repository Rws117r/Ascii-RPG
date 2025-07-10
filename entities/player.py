# entities/player.py
"""
Player class using centralized ASCII definitions with building system support.
"""
from entities.character import Character
from ui.ascii_definitions import ASCII_DEFS

class Player:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.entity_id = 'player'
        
        # Get character and color from ASCII definitions
        player_def = ASCII_DEFS.get_entity('player')
        self.char = player_def['char']  # Can be '@' or '웃'
        self.color = player_def['color']
        
        self.character = Character()
        self.location = 'overworld'  # 'overworld', 'building_interior', 'dungeon'
        self.overworld_pos = (x, y)
        
        # Visual effects
        self.color_effect = None
        self.char_effect = None

    def add_visual_effect(self, effect_type):
        """Add a visual effect to the player."""
        if effect_type == 'blessed':
            from ui.ascii_definitions import ColorPulse
            self.color_effect = ColorPulse(self.color, (255, 255, 255), duration=2000, repeat=True)
            self.color_effect.start()
        elif effect_type == 'cursed':
            from ui.ascii_definitions import ColorPulse
            self.color_effect = ColorPulse(self.color, (255, 0, 0), duration=1000, repeat=True)
            self.color_effect.start()
        elif effect_type == 'hasted':
            from ui.ascii_definitions import CharacterCycle
            self.char_effect = CharacterCycle([self.char, '※', self.char], duration=500, repeat=True)
            self.char_effect.start()

    def get_render_info(self):
        """Get current rendering information with effects."""
        char = self.char
        color = self.color
        
        # Apply color effects
        if self.color_effect and self.color_effect.active:
            self.color_effect.update()
            color = self.color_effect.get_current_color()
        
        # Apply character effects
        if self.char_effect and self.char_effect.active:
            self.char_effect.update()
            char = self.char_effect.get_current_char()
        
        return {'char': char, 'color': color}

    def move(self, dx, dy, world):
        """Move the player and handle location transitions with building system support."""
        # Get current location info
        current_location = world.location_manager.current_location
        
        if current_location == 'overworld':
            current_map = world.overworld_tile_ids
            max_x = world.width
            max_y = world.height
        elif current_location == 'building_interior':
            if world.building_manager.current_building:
                current_map = world.building_manager.current_building['interior_map']
                max_x = world.building_manager.current_building['interior_size'][0]
                max_y = world.building_manager.current_building['interior_size'][1]
            else:
                return  # No building to move in
        elif current_location == 'dungeon':
            current_map = world.dungeon_tile_ids
            max_x = world.width
            max_y = world.height
        else:
            return
            
        new_x, new_y = self.x + dx, self.y + dy
        
        # Check bounds
        if 0 <= new_x < max_x and 0 <= new_y < max_y:
            # Check if tile is solid
            if not world.is_solid(new_x, new_y, self):
                self.x, self.y = new_x, new_y
                
                # Update location string for compatibility
                self.location = current_location

    def add_to_inventory(self, item):
        """Add an item to the player's inventory."""
        self.character.inventory.append(item)

    def equip(self, item_index):
        """Equip an item from inventory."""
        if 0 <= item_index < len(self.character.inventory):
            item = self.character.inventory[item_index]
            
            # Handle gloves (can equip to either hand)
            if item.slot == 'left_glove':
                base = 'glove'
                slot_to_equip = f'left_{base}' if not self.character.equipped[f'left_{base}'] else f'right_{base}'
            else:
                slot_to_equip = item.slot
            
            # Unequip existing item if present
            if self.character.equipped[slot_to_equip]:
                self.unequip(slot_to_equip)
            
            # Handle two-handed weapons
            if item.item_type == 'weapon' and item.hands == 2 and self.character.equipped['shield']:
                self.unequip('shield')
            
            # Handle shield conflicts with two-handed weapons
            if item.slot == 'shield' and self.character.equipped['weapon'] and self.character.equipped['weapon'].hands == 2:
                self.unequip('weapon')
            
            self.character.equipped[slot_to_equip] = self.character.inventory.pop(item_index)

    def unequip(self, slot):
        """Unequip an item and put it back in inventory."""
        if self.character.equipped[slot]:
            self.add_to_inventory(self.character.equipped[slot])
            self.character.equipped[slot] = None