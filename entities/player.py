# entities/player.py
"""
Player class using centralized ASCII definitions.
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
        self.location = 'overworld'
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
        """Move the player and handle location transitions."""
        if self.location == 'overworld':
            current_map = world.overworld_tile_ids
        else:
            current_map = world.dungeon_tile_ids
            
        new_x, new_y = self.x + dx, self.y + dy
        
        if 0 <= new_x < world.width and 0 <= new_y < world.height:
            target_tile_id = current_map[new_y][new_x]
            
            # Handle dungeon entrance
            if target_tile_id == 'dungeon_entrance' and self.location == 'overworld':
                self.location = 'dungeon'
                self.overworld_pos = (self.x, self.y)
                for entrance in world.entrances:
                    if entrance['overworld'] == (new_x, new_y):
                        self.x, self.y = entrance['dungeon']
                        break
            
            # Handle dungeon exit
            elif target_tile_id == 'dungeon_exit' and self.location == 'dungeon':
                self.location = 'overworld'
                for entrance in world.entrances:
                    if entrance['dungeon'] == (new_x, new_y):
                        self.x, self.y = entrance['overworld']
                        break
            
            # Normal movement
            elif not world.is_solid(new_x, new_y, self.location):
                self.x, self.y = new_x, new_y

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