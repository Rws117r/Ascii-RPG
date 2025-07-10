# ui/ascii_definitions.py
"""
Centralized ASCII character and visual effect definitions for the RPG with overlay system.
This module handles all character symbols, colors, animations, and visual effects.
"""
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
        # Use sine wave for smooth pulsing
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

class AsciiTile:
    """Represents a single ASCII tile with potential effects and overlays."""
    def __init__(self, char, color, solid=False, name="Unknown", biome="none"):
        self.base_char = char
        self.base_color = color
        self.solid = solid
        self.name = name
        self.biome = biome
        
        # Effects
        self.color_effect = None
        self.char_effect = None
        self.overlay_chars = []  # For spell effects, smoke, etc.
        
    def add_color_effect(self, effect):
        """Add a color animation effect."""
        self.color_effect = effect
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
        # Update color effect
        if self.color_effect and not self.color_effect.update():
            self.color_effect = None
        
        # Update character effect
        if self.char_effect and not self.char_effect.update():
            self.char_effect = None
        
        # Update overlays
        current_time = pygame.time.get_ticks()
        self.overlay_chars = [
            overlay for overlay in self.overlay_chars
            if current_time - overlay['start_time'] < overlay['duration']
        ]
    
    def get_render_info(self):
        """Get the current character and color for rendering."""
        self.update_effects()
        
        # Determine character and color - overlays take priority
        if self.overlay_chars:
            # Use the most recent overlay
            char = self.overlay_chars[-1]['char']
            color = self.overlay_chars[-1]['color']
        elif self.char_effect and self.char_effect.active:
            char = self.char_effect.get_current_char()
            color = self.color_effect.get_current_color() if self.color_effect else self.base_color
        else:
            char = self.base_char
            color = self.color_effect.get_current_color() if self.color_effect else self.base_color
        
        return {
            'char': char,
            'color': color,
            'solid': self.solid,
            'name': self.name,
            'biome': self.biome
        }

class AsciiDefinitions:
    """Central repository for all ASCII definitions and visual effects."""
    
    def __init__(self):
        self.tiles = {}
        self.entities = {}
        self.items = {}
        self.effects = {}
        self._initialize_definitions()
    
    def _initialize_definitions(self):
        """Initialize all ASCII definitions."""
        self._init_terrain_tiles()
        self._init_building_tiles()
        self._init_special_tiles()
        self._init_entity_definitions()
        self._init_item_definitions()
        self._init_effect_definitions()
    
    def _init_terrain_tiles(self):
        """Initialize terrain tiles with clean, single-layer design."""
        
        self.tiles.update({
            # WATER BIOMES
            'ocean': AsciiTile('~', (100, 149, 237), solid=True, name='Ocean', biome='ocean'),
            'river': AsciiTile('~', (64, 164, 223), solid=True, name='River', biome='river'),
            'lake': AsciiTile('~', (100, 149, 237), solid=True, name='Lake', biome='lake'),
            
            # GRASSLAND BIOMES
            'grasslands': AsciiTile(',', (124, 180, 90), solid=False, name='Grasslands', biome='plains'),
            'dense_grasslands': AsciiTile('░', (100, 180, 100), solid=False, name='Dense Grasslands', biome='plains'),
            
            # FOREST BIOMES
            'deciduous_forest': AsciiTile('♣', (34, 139, 34), solid=False, name='Deciduous Forest', biome='forest'),
            'coniferous_forest': AsciiTile('♠', (25, 100, 25), solid=False, name='Coniferous Forest', biome='forest'),
            
            # JUNGLE BIOMES
            'jungle': AsciiTile('Ψ', (85, 107, 47), solid=False, name='Jungle', biome='jungle'),
            'dense_jungle': AsciiTile('¶', (107, 142, 35), solid=False, name='Dense Jungle', biome='jungle'),
            
            # DESERT BIOMES
            'desert': AsciiTile('≈', (255, 218, 100), solid=False, name='Desert', biome='desert'),
            'sandy_desert': AsciiTile('≋', (255, 228, 150), solid=False, name='Sandy Desert', biome='desert'),
            'high_desert': AsciiTile('∴', (240, 200, 120), solid=False, name='High Desert', biome='desert'),
            
            # HILL BIOMES
            'hills': AsciiTile('∩', (160, 140, 100), solid=False, name='Hills', biome='mountains'),
            'grassy_hills': AsciiTile('⌒', (140, 180, 120), solid=False, name='Grassy Hills', biome='mountains'),
            'rocky_hills': AsciiTile('∧', (140, 120, 100), solid=False, name='Rocky Hills', biome='mountains'),
            'forested_hills': AsciiTile('♠', (100, 140, 80), solid=False, name='Forested Hills', biome='forest'),
            
            # MOUNTAIN BIOMES
            'mountains': AsciiTile('▲', (169, 169, 169), solid=True, name='Mountains', biome='mountains'),
            'high_mountains': AsciiTile('△', (200, 200, 200), solid=True, name='High Mountains', biome='mountains'),
            
            # SWAMP BIOMES
            'swamp': AsciiTile('≈', (107, 142, 35), solid=False, name='Swamp', biome='swamp'),
            'deep_swamp': AsciiTile('~', (85, 107, 47), solid=False, name='Deep Swamp', biome='swamp'),
            
            # BARREN BIOMES
            'barren': AsciiTile('∴', (139, 137, 137), solid=False, name='Barren Land', biome='barren'),
            'wasteland': AsciiTile('∵', (120, 120, 120), solid=False, name='Wasteland', biome='barren'),
            'high_barren': AsciiTile('◦', (160, 160, 160), solid=False, name='High Barren', biome='barren'),
        })
        
        # Add water animation
        water_pulse = ColorPulse((64, 164, 223), (100, 149, 237), duration=2000)
        self.tiles['river'].add_color_effect(water_pulse)
        
        # Add desert heat shimmer
        desert_shimmer = CharacterCycle(['≈', '≋', '≈'], duration=3000)
        self.tiles['desert'].add_char_effect(desert_shimmer)
    
    def _init_building_tiles(self):
        """Initialize building and settlement tiles."""
        self.tiles.update({
            # SETTLEMENT BIOMES
            'road': AsciiTile('▓', (139, 121, 94), solid=False, name='Road', biome='settled'),
            'settled_land': AsciiTile('▒', (160, 140, 100), solid=False, name='Settled Land', biome='settled'),
            
            # BUILDING EXTERIORS
            'house': AsciiTile('⌂', (139, 121, 94), solid=True, name='House', biome='settled'),
            'tavern': AsciiTile('∏', (160, 140, 100), solid=True, name='Tavern', biome='settled'),
            'forge': AsciiTile('⚙', (180, 140, 100), solid=True, name='Forge', biome='settled'),
            'castle': AsciiTile('♜', (200, 200, 200), solid=True, name='Castle', biome='settled'),
            'tower': AsciiTile('♖', (180, 180, 180), solid=True, name='Tower', biome='settled'),
            
            # BUILDING ROOFS (used by building system)
            'house_roof': AsciiTile('█', (139, 121, 94), solid=True, name='House Roof', biome='settled'),
            'tavern_roof': AsciiTile('█', (160, 140, 100), solid=True, name='Tavern Roof', biome='settled'),
            'forge_roof': AsciiTile('█', (180, 140, 100), solid=True, name='Forge Roof', biome='settled'),
            'castle_roof': AsciiTile('█', (200, 200, 200), solid=True, name='Castle Roof', biome='settled'),
            'tower_roof': AsciiTile('█', (180, 180, 180), solid=True, name='Tower Roof', biome='settled'),
            
            # BUILDING DOORS (always visible)
            'house_door': AsciiTile('+', (139, 69, 19), solid=False, name='House Door', biome='settled'),
            'tavern_door': AsciiTile('+', (139, 69, 19), solid=False, name='Tavern Door', biome='settled'),
            'forge_door': AsciiTile('+', (139, 69, 19), solid=False, name='Forge Door', biome='settled'),
            'castle_door': AsciiTile('+', (139, 69, 19), solid=False, name='Castle Door', biome='settled'),
            'tower_door': AsciiTile('+', (139, 69, 19), solid=False, name='Tower Door', biome='settled'),
        })
        
        # Add forge animation (glowing)
        forge_glow = ColorPulse((180, 140, 100), (255, 100, 100), duration=1500)
        self.tiles['forge'].add_color_effect(forge_glow)
    
    def _init_special_tiles(self):
        """Initialize special tiles like dungeons, treasures."""
        self.tiles.update({
            # SPECIAL TILES
            'dungeon_entrance': AsciiTile('<', (255, 255, 255), solid=False, name='Dungeon Entrance', biome='dungeon'),
            'dungeon_exit': AsciiTile('>', (255, 255, 255), solid=False, name='Dungeon Exit', biome='dungeon'),
            'treasure_chest': AsciiTile('$', (255, 215, 0), solid=False, name='Treasure Chest', biome='special'),
            
            # DUNGEON TILES
            'dungeon_floor': AsciiTile('.', (139, 121, 94), solid=False, name='Floor', biome='dungeon'),
            'dungeon_wall': AsciiTile('#', (100, 100, 100), solid=True, name='Wall', biome='dungeon'),
            'stairs_up': AsciiTile('<', (255, 255, 255), solid=False, name='Stairs Up', biome='dungeon'),
            'stairs_down': AsciiTile('>', (255, 255, 255), solid=False, name='Stairs Down', biome='dungeon'),
        })
        
        # Add treasure chest sparkle
        treasure_sparkle = ColorPulse((255, 215, 0), (255, 255, 255), duration=1000)
        self.tiles['treasure_chest'].add_color_effect(treasure_sparkle)
    
    def _init_entity_definitions(self):
        """Initialize entity (player, monster) definitions."""
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
            # Weapons
            'sword': {'char': '†', 'color': C_TEXT_DIM},
            'greatsword': {'char': '⚔', 'color': C_TEXT},
            'axe': {'char': 'P', 'color': C_TEXT_DIM},
            
            # Armor
            'helmet': {'char': '☊', 'color': C_BROWN},
            'armor_piece': {'char': '[ ]', 'color': C_TEXT},
            'shield': {'char': '⛨', 'color': C_BROWN},
        }
    
    def _init_effect_definitions(self):
        """Initialize spell and effect definitions."""
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
        
        # Add animation if multiple chars/colors
        if len(effect_def['chars']) > 1:
            char_cycle = CharacterCycle(effect_def['chars'], duration)
            target_tile.add_char_effect(char_cycle)
        
        if len(effect_def['colors']) > 1:
            color_pulse = ColorPulse(effect_def['colors'][0], effect_def['colors'][1], duration//2)
            target_tile.add_color_effect(color_pulse)
    
    def map_legacy_char(self, old_char):
        """Map old character symbols to new tile IDs for backward compatibility."""
        legacy_mapping = {
            ',': 'grasslands',
            'g': 'dense_grasslands',
            '"': 'deciduous_forest',
            'f': 'coniferous_forest',
            'j': 'jungle',
            'J': 'dense_jungle',
            'd': 'desert',
            'D': 'sandy_desert',
            '#': 'mountains',
            '^': 'high_mountains',
            'h': 'hills',
            's': 'swamp',
            'S': 'deep_swamp',
            'b': 'barren',
            'B': 'wasteland',
            '~': 'ocean',
            'r': 'river',
            'l': 'lake',
            '.': 'road',
            'c': 'settled_land',
            'H': 'house',
            'T': 'tavern',
            'F': 'forge',
            'C': 'castle',
            't': 'tower',
            '<': 'dungeon_entrance',
            '>': 'dungeon_exit',
            '$': 'treasure_chest',
        }
        return legacy_mapping.get(old_char, 'grasslands')

# Global instance
ASCII_DEFS = AsciiDefinitions()