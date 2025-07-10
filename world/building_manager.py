# world/building_manager.py
"""
Building system manager - handles transitions, visibility, and rendering.
"""
import pygame
from ui.ascii_definitions import ASCII_DEFS

class BuildingManager:
    """Manages building interactions, transitions, and rendering."""
    
    def __init__(self):
        self.ascii_defs = ASCII_DEFS
        self.buildings = []
        self.current_building = None
        self.interior_tiles = {}  # Cache for interior tile instances
        
        # Define tile mappings for interiors
        self._init_interior_tile_mappings()
    
    def _init_interior_tile_mappings(self):
        """Initialize mappings for interior tile types."""
        self.interior_tile_chars = {
            'wall': '#',
            'floor': '.',
            'door': '+',
            'window': '○',
            'bed': '=',
            'table': '┬',
            'chair': 'h',
            'counter': '━',
            'forge': '▲',
            'anvil': '♦',
            'storage': '■',
            'stairs_up': '<',
            'stairs_down': '>',
            'throne': '♔',
            'pillar': '▓'
        }
        
        self.interior_tile_colors = {
            'wall': (100, 100, 100),
            'floor': (139, 121, 94),
            'door': (139, 69, 19),
            'window': (173, 216, 230),
            'bed': (255, 182, 193),
            'table': (139, 121, 94),
            'chair': (160, 82, 45),
            'counter': (139, 121, 94),
            'forge': (255, 69, 0),
            'anvil': (105, 105, 105),
            'storage': (139, 121, 94),
            'stairs_up': (255, 255, 255),
            'stairs_down': (255, 255, 255),
            'throne': (255, 215, 0),
            'pillar': (128, 128, 128)
        }
    
    def add_buildings(self, buildings):
        """Add buildings to the manager."""
        self.buildings.extend(buildings)
    
    def can_enter_building(self, player_x, player_y, terrain_map):
        """Check if player can enter a building at current position."""
        if 0 <= player_y < len(terrain_map) and 0 <= player_x < len(terrain_map[0]):
            tile_id = terrain_map[player_y][player_x]
            return tile_id.endswith('_door')
        return False
    
    def get_building_at_position(self, x, y):
        """Get building that has a door at the given position."""
        for building in self.buildings:
            bx, by = building['exterior_pos']
            bw, bh = building['exterior_size']
            
            # Check if position is within building bounds and is a door
            if bx <= x < bx + bw and by <= y < by + bh:
                return building
        return None
    
    def enter_building(self, building, player):
        """Enter a building and transition to interior view."""
        self.current_building = building
        
        # Move player to interior entrance point
        if building['entrance_points']:
            entrance_x, entrance_y = building['entrance_points'][0]
            player.x = entrance_x
            player.y = entrance_y
            player.location = 'building_interior'
        
        return True
    
    def exit_building(self, player):
        """Exit current building and return to overworld."""
        if self.current_building:
            # Move player to building exterior (just outside door)
            bx, by = self.current_building['exterior_pos']
            bw, bh = self.current_building['exterior_size']
            
            # Place player just south of the building
            player.x = bx + bw // 2
            player.y = by + bh
            player.location = 'overworld'
            
            self.current_building = None
        
        return True
    
    def get_current_map_info(self, player):
        """Get current map information for rendering."""
        if player.location == 'building_interior' and self.current_building:
            return {
                'type': 'building_interior',
                'map': self.current_building['interior_map'],
                'width': self.current_building['interior_size'][0],
                'height': self.current_building['interior_size'][1],
                'building': self.current_building
            }
        return None
    
    def get_tile_render_info(self, x, y, tile_type):
        """Get rendering information for interior tiles."""
        char = self.interior_tile_chars.get(tile_type, '?')
        color = self.interior_tile_colors.get(tile_type, (255, 255, 255))
        solid = tile_type in ['wall', 'pillar', 'storage', 'counter']
        
        return {
            'char': char,
            'color': color,
            'solid': solid,
            'name': tile_type.replace('_', ' ').title(),
            'biome': 'interior'
        }
    
    def is_solid(self, x, y, interior_map):
        """Check if interior tile blocks movement."""
        if 0 <= y < len(interior_map) and 0 <= x < len(interior_map[0]):
            tile_type = interior_map[y][x]
            return tile_type in ['wall', 'pillar', 'storage', 'counter', 'bed', 'table', 
                               'forge', 'anvil', 'throne']
        return True
    
    def get_action_prompt(self, x, y, interior_map):
        """Get action prompt for interior tiles."""
        if 0 <= y < len(interior_map) and 0 <= x < len(interior_map[0]):
            tile_type = interior_map[y][x]
            
            if tile_type == 'door':
                return "Press Enter to exit building"
            elif tile_type == 'stairs_up':
                return "Press Enter to go upstairs"
            elif tile_type == 'stairs_down':
                return "Press Enter to go downstairs"
            elif tile_type in ['bed', 'table', 'chair']:
                return f"Press Enter to use {tile_type}"
            elif tile_type == 'forge':
                return "Press Enter to use forge"
            elif tile_type == 'storage':
                return "Press Enter to search storage"
        
        return ""
    
    def draw_building_exterior(self, surface, font, camera, terrain_map, player):
        """Draw building exteriors with roof hiding logic."""
        from config import TILE_SIZE
        
        # Calculate visible tile range
        start_x = max(0, int(camera.x))
        end_x = min(len(terrain_map[0]), int(camera.x + surface.get_width() // TILE_SIZE) + 1)
        start_y = max(0, int(camera.y))
        end_y = min(len(terrain_map), int(camera.y + surface.get_height() // TILE_SIZE) + 1)
        
        for y in range(start_y, end_y):
            for x in range(start_x, end_x):
                tile_id = terrain_map[y][x]
                
                # Handle building tiles
                if tile_id.endswith('_roof'):
                    building_type = tile_id.replace('_roof', '')
                    
                    # Show roof if player is outside
                    if player.location == 'overworld':
                        char = '█'  # Roof character
                        color = self._get_roof_color(building_type)
                    else:
                        # Hide roof if player is inside this building
                        building = self.get_building_at_position(x, y)
                        if building and building == self.current_building:
                            # Show interior through roof
                            continue  # Skip rendering roof
                        else:
                            char = '█'
                            color = self._get_roof_color(building_type)
                    
                    screen_x = (x - camera.x) * TILE_SIZE
                    screen_y = (y - camera.y) * TILE_SIZE
                    tile_surface = font.render(char, True, color)
                    surface.blit(tile_surface, (screen_x, screen_y))
                
                elif tile_id.endswith('_door'):
                    building_type = tile_id.replace('_door', '')
                    
                    # Doors are always visible
                    char = '+'  # Door character
                    color = (139, 69, 19)  # Brown door
                    
                    screen_x = (x - camera.x) * TILE_SIZE
                    screen_y = (y - camera.y) * TILE_SIZE
                    tile_surface = font.render(char, True, color)
                    surface.blit(tile_surface, (screen_x, screen_y))
    
    def draw_building_interior(self, surface, font, camera, player):
        """Draw building interior when player is inside."""
        if not self.current_building:
            return
        
        from config import TILE_SIZE
        
        interior_map = self.current_building['interior_map']
        interior_w, interior_h = self.current_building['interior_size']
        
        # Calculate visible tile range
        start_x = max(0, int(camera.x))
        end_x = min(interior_w, int(camera.x + surface.get_width() // TILE_SIZE) + 1)
        start_y = max(0, int(camera.y))
        end_y = min(interior_h, int(camera.y + surface.get_height() // TILE_SIZE) + 1)
        
        for y in range(start_y, end_y):
            for x in range(start_x, end_x):
                if y < len(interior_map) and x < len(interior_map[0]):
                    tile_type = interior_map[y][x]
                    render_info = self.get_tile_render_info(x, y, tile_type)
                    
                    screen_x = (x - camera.x) * TILE_SIZE
                    screen_y = (y - camera.y) * TILE_SIZE
                    
                    tile_surface = font.render(
                        render_info['char'], 
                        True, 
                        render_info['color']
                    )
                    surface.blit(tile_surface, (screen_x, screen_y))
    
    def _get_roof_color(self, building_type):
        """Get roof color for building type."""
        roof_colors = {
            'house': (139, 121, 94),
            'tavern': (160, 140, 100),
            'forge': (120, 100, 80),
            'tower': (150, 150, 150),
            'castle': (180, 180, 180)
        }
        return roof_colors.get(building_type, (100, 100, 100))
    
    def get_description(self, x, y, interior_map):
        """Get description for interior tiles."""
        if 0 <= y < len(interior_map) and 0 <= x < len(interior_map[0]):
            tile_type = interior_map[y][x]
            
            descriptions = {
                'wall': 'A solid stone wall.',
                'floor': 'Worn wooden floorboards.',
                'door': 'A sturdy wooden door.',
                'window': 'A small window lets in some light.',
                'bed': 'A simple wooden bed.',
                'table': 'A rough wooden table.',
                'chair': 'A wooden chair.',
                'counter': 'A long wooden counter.',
                'forge': 'A blazing forge for metalwork.',
                'anvil': 'A heavy iron anvil.',
                'storage': 'A storage chest.',
                'stairs_up': 'Stairs leading up.',
                'stairs_down': 'Stairs leading down.',
                'throne': 'An ornate royal throne.',
                'pillar': 'A stone support pillar.'
            }
            
            return descriptions.get(tile_type, 'Something interesting.')
        
        return "Nothing here."