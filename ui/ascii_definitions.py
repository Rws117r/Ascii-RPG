# ui/ascii_definitions.py - Updated with colored background system

import pygame
import time
import math
from ui.colors import *

class VisualEffect:
    """Base class for visual effects like animations, color changes, etc."""
    def __init__(self, duration=1000, repeat=False):
        self.start_time = None
        self.duration = duration  # milliseconds
        self.repeat = repeat
        self.active = False
    
    def start(self):
        """Start the effect."""
        self.start_time = pygame.time.get_ticks()
        self.active = True
    
    def update(self):
        """Update the effect. Returns True if still active."""
        if not self.active:
            return False
        
        current_time = pygame.time.get_ticks()
        elapsed = current_time - self.start_time
        
        if elapsed >= self.duration:
            if self.repeat:
                self.start_time = current_time
                return True
            else:
                self.active = False
                return False
        
        return True
    
    def get_progress(self):
        """Get progress as a value between 0.0 and 1.0."""
        if not self.active:
            return 1.0
        
        current_time = pygame.time.get_ticks()
        elapsed = current_time - self.start_time
        return min(1.0, elapsed / self.duration)

class ColorPulse(VisualEffect):
    """Pulses between two colors."""
    def __init__(self, color1, color2, duration=1000, repeat=True):
        super().__init__(duration, repeat)
        self.color1 = color1
        self.color2 = color2
    
    def get_current_color(self):
        """Get the current color based on animation progress."""
        if not self.active:
            return self.color1
        
        progress = self.get_progress()
        factor = (math.sin(progress * 2 * math.pi) + 1) / 2
        
        r = int(self.color1[0] * (1 - factor) + self.color2[0] * factor)
        g = int(self.color1[1] * (1 - factor) + self.color2[1] * factor)
        b = int(self.color1[2] * (1 - factor) + self.color2[2] * factor)
        
        return (r, g, b)

class CharacterCycle(VisualEffect):
    """Cycles through different characters."""
    def __init__(self, chars, duration=2000, repeat=True):
        super().__init__(duration, repeat)
        self.chars = chars
    
    def get_current_char(self):
        """Get the current character based on animation progress."""
        if not self.active or not self.chars:
            return self.chars[0] if self.chars else '?'
        
        progress = self.get_progress()
        index = int(progress * len(self.chars)) % len(self.chars)
        return self.chars[index]

class ColoredBackgroundTile:
    """Tile with colored background rectangle and ASCII foreground."""
    def __init__(self, char, char_color, background_color, elevation_level=0, 
                 solid=False, name="Unknown", biome="none"):
        self.base_char = char
        self.base_char_color = char_color
        self.base_background_color = background_color
        self.elevation_level = elevation_level
        self.solid = solid
        self.name = name
        self.biome = biome
        
        # Effects
        self.color_effect = None
        self.char_effect = None
        self.background_effect = None
        self.overlay_chars = []
        
    def add_color_effect(self, effect):
        """Add a color animation effect to the character."""
        self.color_effect = effect
        effect.start()
    
    def add_background_effect(self, effect):
        """Add a color animation effect to the background."""
        self.background_effect = effect
        effect.start()
    
    def add_char_effect(self, effect):
        """Add a character animation effect."""
        self.char_effect = effect
        effect.start()
    
    def add_overlay(self, char, color, duration=1000):
        """Add a temporary overlay character (for spells, effects)."""
        overlay = {
            'char': char,
            'color': color,
            'start_time': pygame.time.get_ticks(),
            'duration': duration
        }
        self.overlay_chars.append(overlay)
    
    def update_effects(self):
        """Update all active effects."""
        if self.color_effect and not self.color_effect.update():
            self.color_effect = None
        
        if self.background_effect and not self.background_effect.update():
            self.background_effect = None
        
        if self.char_effect and not self.char_effect.update():
            self.char_effect = None
        
        current_time = pygame.time.get_ticks()
        self.overlay_chars = [
            overlay for overlay in self.overlay_chars
            if current_time - overlay['start_time'] < overlay['duration']
        ]
    
    def get_render_info(self):
        """Get current rendering information."""
        self.update_effects()
        
        # Determine character
        if self.overlay_chars:
            char = self.overlay_chars[-1]['char']
            char_color = self.overlay_chars[-1]['color']
        elif self.char_effect and self.char_effect.active:
            char = self.char_effect.get_current_char()
            char_color = self.color_effect.get_current_color() if self.color_effect else self.base_char_color
        else:
            char = self.base_char
            char_color = self.color_effect.get_current_color() if self.color_effect else self.base_char_color
        
        # Determine background color
        background_color = (self.background_effect.get_current_color() 
                           if self.background_effect else self.base_background_color)
        
        return {
            'char': char,
            'char_color': char_color,
            'background_color': background_color,
            'elevation_level': self.elevation_level,
            'solid': self.solid,
            'name': self.name,
            'biome': self.biome
        }

class AsciiDefinitions:
    """ASCII definitions with colored background system."""
    
    def __init__(self):
        self.tiles = {}
        self.entities = {}
        self.items = {}
        self.effects = {}
        self._initialize_definitions()
    
    def _initialize_definitions(self):
        """Initialize all definitions."""
        self._init_terrain_tiles()
        self._init_building_tiles()
        self._init_special_tiles()
        self._init_entity_definitions()
        self._init_item_definitions()
        self._init_effect_definitions()
    
    def _init_terrain_tiles(self):
        """Initialize terrain with colored backgrounds."""
        
        # ELEVATION BACKGROUND COLORS
        ELEVATION_COLORS = {
            0: (20, 50, 100),      # Sea level - deep blue
            1: (50, 80, 40),       # Low elevation - dark green
            2: (70, 110, 50),      # Medium elevation - medium green
            3: (90, 130, 60),      # High elevation - light green
            4: (110, 150, 70),     # Very high - pale green
            5: (130, 130, 110),    # Mountain level - gray-green
        }
        
        self.tiles.update({
            # WATER - Dark blue backgrounds, no ASCII overlay
            'ocean': ColoredBackgroundTile('~', (150, 200, 255), (20, 50, 100), 
                                         elevation_level=0, solid=True, name='Ocean', biome='ocean'),
            'river': ColoredBackgroundTile('~', (100, 180, 255), (30, 60, 120),
                                         elevation_level=0, solid=True, name='River', biome='river'),
            'lake': ColoredBackgroundTile('~', (120, 190, 255), (25, 55, 110),
                                        elevation_level=0, solid=True, name='Lake', biome='lake'),
            
            # GRASSLANDS - Green backgrounds, minimal ASCII
            'grasslands': ColoredBackgroundTile(' ', (255, 255, 255), (70, 110, 50),
                                              elevation_level=2, solid=False, name='Grasslands', biome='plains'),
            'dense_grasslands': ColoredBackgroundTile('░', (120, 200, 120), (80, 120, 60),
                                                    elevation_level=2, solid=False, name='Dense Grasslands', biome='plains'),
            
            # FORESTS - Green backgrounds, tree symbols
            'deciduous_forest': ColoredBackgroundTile('♣', (50, 150, 50), (60, 100, 40),
                                                    elevation_level=2, solid=False, name='Deciduous Forest', biome='forest'),
            'coniferous_forest': ColoredBackgroundTile('♠', (40, 120, 40), (50, 90, 30),
                                                     elevation_level=3, solid=False, name='Coniferous Forest', biome='forest'),
            
            # JUNGLES - Dark green backgrounds, tropical symbols
            'jungle': ColoredBackgroundTile('Ψ', (100, 150, 50), (40, 80, 30),
                                          elevation_level=2, solid=False, name='Jungle', biome='jungle'),
            'dense_jungle': ColoredBackgroundTile('¶', (120, 170, 60), (50, 90, 40),
                                                elevation_level=2, solid=False, name='Dense Jungle', biome='jungle'),
            
            # DESERTS - Sandy backgrounds, heat shimmer
            'desert': ColoredBackgroundTile('≈', (255, 255, 150), (200, 180, 120),
                                          elevation_level=1, solid=False, name='Desert', biome='desert'),
            'sandy_desert': ColoredBackgroundTile('≋', (255, 255, 180), (220, 200, 140),
                                                elevation_level=2, solid=False, name='Sandy Desert', biome='desert'),
            'high_desert': ColoredBackgroundTile('∴', (240, 220, 140), (180, 160, 100),
                                               elevation_level=3, solid=False, name='High Desert', biome='desert'),
            
            # HILLS - Elevation backgrounds, clear hill symbols
            'hills': ColoredBackgroundTile('∩', (200, 180, 140), (90, 130, 60),
                                         elevation_level=3, solid=False, name='Hills', biome='mountains'),
            'grassy_hills': ColoredBackgroundTile('⌒', (180, 220, 160), (100, 140, 70),
                                                elevation_level=3, solid=False, name='Grassy Hills', biome='mountains'),
            'rocky_hills': ColoredBackgroundTile('∧', (160, 140, 120), (80, 110, 50),
                                               elevation_level=3, solid=False, name='Rocky Hills', biome='mountains'),
            'forested_hills': ColoredBackgroundTile('♠', (120, 180, 100), (70, 120, 50),
                                                  elevation_level=3, solid=False, name='Forested Hills', biome='forest'),
            
            # MOUNTAINS - Gray backgrounds, mountain symbols
            'mountains': ColoredBackgroundTile('▲', (220, 220, 220), (110, 110, 90),
                                             elevation_level=4, solid=True, name='Mountains', biome='mountains'),
            'high_mountains': ColoredBackgroundTile('△', (240, 240, 240), (130, 130, 110),
                                                  elevation_level=5, solid=True, name='High Mountains', biome='mountains'),
            
            # SWAMPS - Dark green/brown backgrounds, water symbols
            'swamp': ColoredBackgroundTile('~', (150, 200, 150), (60, 90, 50),
                                         elevation_level=1, solid=False, name='Swamp', biome='swamp'),
            'deep_swamp': ColoredBackgroundTile('≈', (120, 160, 120), (40, 70, 30),
                                              elevation_level=1, solid=False, name='Deep Swamp', biome='swamp'),
            
            # BARREN - Gray/brown backgrounds, dot patterns
            'barren': ColoredBackgroundTile('∴', (180, 180, 180), (100, 100, 80),
                                          elevation_level=2, solid=False, name='Barren Land', biome='barren'),
            'wasteland': ColoredBackgroundTile('∵', (160, 160, 160), (80, 80, 60),
                                             elevation_level=3, solid=False, name='Wasteland', biome='barren'),
            'high_barren': ColoredBackgroundTile('◦', (200, 200, 200), (120, 120, 100),
                                               elevation_level=4, solid=False, name='High Barren', biome='barren'),
        })
        
        # Add animated effects
        water_pulse = ColorPulse((30, 60, 120), (50, 80, 140), duration=2000)
        self.tiles['river'].add_background_effect(water_pulse)
        
        desert_shimmer = CharacterCycle(['≈', '≋', '≈'], duration=3000)
        self.tiles['desert'].add_char_effect(desert_shimmer)
    
    def _init_building_tiles(self):
        """Initialize buildings with colored backgrounds."""
        self.tiles.update({
            # SETTLEMENTS - Earth tone backgrounds, clear symbols
            'road': ColoredBackgroundTile('▓', (139, 121, 94), (100, 120, 80),
                                        elevation_level=2, solid=False, name='Road', biome='settled'),
            'settled_land': ColoredBackgroundTile('▒', (180, 160, 120), (120, 140, 90),
                                                elevation_level=2, solid=False, name='Settled Land', biome='settled'),
            
            # BUILDINGS - Distinct backgrounds, clear symbols
            'house': ColoredBackgroundTile('⌂', (200, 180, 140), (120, 140, 90),
                                         elevation_level=2, solid=True, name='House', biome='settled'),
            'tavern': ColoredBackgroundTile('∏', (220, 200, 160), (120, 140, 90),
                                          elevation_level=2, solid=True, name='Tavern', biome='settled'),
            'forge': ColoredBackgroundTile('⚙', (255, 200, 100), (120, 140, 90),
                                         elevation_level=2, solid=True, name='Forge', biome='settled'),
            'castle': ColoredBackgroundTile('♜', (255, 255, 255), (140, 140, 120),
                                          elevation_level=3, solid=True, name='Castle', biome='settled'),
            'tower': ColoredBackgroundTile('♖', (220, 220, 220), (120, 120, 100),
                                         elevation_level=3, solid=True, name='Tower', biome='settled'),
        })
        
        # Add forge glow effect
        forge_glow = ColorPulse((120, 140, 90), (200, 100, 100), duration=1500)
        self.tiles['forge'].add_background_effect(forge_glow)
    
    def _init_special_tiles(self):
        """Initialize special tiles."""
        self.tiles.update({
            'dungeon_entrance': ColoredBackgroundTile('<', (255, 255, 255), (60, 60, 40),
                                                    elevation_level=3, solid=False, name='Dungeon Entrance', biome='dungeon'),
            'dungeon_exit': ColoredBackgroundTile('>', (255, 255, 255), (60, 60, 40),
                                                elevation_level=3, solid=False, name='Dungeon Exit', biome='dungeon'),
            'treasure_chest': ColoredBackgroundTile('$', (255, 255, 0), (150, 180, 100),
                                                  elevation_level=2, solid=False, name='Treasure Chest', biome='special'),
            
            # DUNGEON TILES - No background color (black)
            'dungeon_floor': ColoredBackgroundTile('.', (139, 121, 94), (0, 0, 0),
                                                 elevation_level=0, solid=False, name='Floor', biome='dungeon'),
            'dungeon_wall': ColoredBackgroundTile('#', (100, 100, 100), (0, 0, 0),
                                                elevation_level=0, solid=True, name='Wall', biome='dungeon'),
        })
        
        # Add treasure sparkle
        treasure_sparkle = ColorPulse((255, 255, 0), (255, 255, 255), duration=1000)
        self.tiles['treasure_chest'].add_color_effect(treasure_sparkle)
    
    def _init_entity_definitions(self):
        """Initialize entity definitions."""
        self.entities = {
            'player': {'char': '@', 'color': C_PLAYER, 'alt_char': '웃'},
            'kobold': {'char': 'ĸ', 'color': C_BROWN},
            'kobold_chieftain': {'char': 'K', 'color': C_BROWN},
            'goblin': {'char': 'g', 'color': (139, 69, 19)},
            'orc': {'char': 'Ѻ', 'color': (85, 107, 47)},
            'bandit': {'char': 'b', 'color': (139, 0, 0)},
            'wolf': {'char': 'w', 'color': (105, 105, 105)},
        }
    
    def _init_item_definitions(self):
        """Initialize item definitions."""
        self.items = {
            'sword': {'char': '†', 'color': C_TEXT_DIM},
            'greatsword': {'char': '⚔', 'color': C_TEXT},
            'axe': {'char': 'P', 'color': C_TEXT_DIM},
            'helmet': {'char': '☊', 'color': C_BROWN},
            'armor_piece': {'char': '[ ]', 'color': C_TEXT},
            'shield': {'char': '⛨', 'color': C_BROWN},
        }
    
    def _init_effect_definitions(self):
        """Initialize spell effects."""
        self.effects = {
            'fire': {
                'chars': ['*', '※', '✱', '✳'],
                'colors': [(255, 0, 0), (255, 165, 0), (255, 255, 0)],
                'duration': 500
            },
            'magic_missile': {
                'chars': ['•', '◦', '∘'],
                'colors': [(128, 0, 255), (255, 0, 255)],
                'duration': 300
            },
            'smoke': {
                'chars': ['░', '▒', '▓', ' '],
                'colors': [(128, 128, 128), (96, 96, 96), (64, 64, 64)],
                'duration': 2000
            },
            'healing': {
                'chars': ['+', '✚', '※'],
                'colors': [(0, 255, 0), (128, 255, 128)],
                'duration': 1000
            }
        }
    
    def get_tile(self, tile_id):
        """Get a tile definition by ID."""
        return self.tiles.get(tile_id)
    
    def get_entity(self, entity_id):
        """Get entity definition by ID."""
        return self.entities.get(entity_id, self.entities['player'])
    
    def get_item(self, item_id):
        """Get item definition by ID."""
        return self.items.get(item_id, self.items['sword'])
    
    def create_spell_effect(self, effect_type, target_tile):
        """Create a spell effect on a tile."""
        if effect_type not in self.effects:
            return
        
        effect_def = self.effects[effect_type]
        char = effect_def['chars'][0]
        color = effect_def['colors'][0]
        duration = effect_def['duration']
        
        target_tile.add_overlay(char, color, duration)
        
        if len(effect_def['chars']) > 1:
            char_cycle = CharacterCycle(effect_def['chars'], duration)
            target_tile.add_char_effect(char_cycle)
        
        if len(effect_def['colors']) > 1:
            color_pulse = ColorPulse(effect_def['colors'][0], effect_def['colors'][1], duration//2)
            target_tile.add_color_effect(color_pulse)

# Global instance
ASCII_DEFS = AsciiDefinitions()