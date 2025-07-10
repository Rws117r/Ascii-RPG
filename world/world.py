# world/world.py (Fixed version with debug output)
"""
Fixed world class with proper building and dungeon generation.
"""
import random
import pygame
from config import TILE_SIZE
from ui.ascii_definitions import ASCII_DEFS, AsciiTile

# Import the new modular generators
from world.overworld_generator import OverworldGenerator
from world.settlement_generator import SettlementGenerator
from world.dungeon_generator import DungeonGenerator
from world.building_manager import BuildingManager
from world.location_manager import LocationManager

class World:
    """Fixed world with proper modular generation and building system."""
    
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.ascii_defs = ASCII_DEFS
        
        # Initialize generators
        self.overworld_generator = OverworldGenerator()
        self.settlement_generator = SettlementGenerator()
        self.dungeon_generator = DungeonGenerator()
        
        # Initialize managers
        self.building_manager = BuildingManager()
        self.location_manager = LocationManager()
        self.location_manager.set_managers(self.building_manager)
        
        # Generate world
        print("Starting world generation...")
        self.overworld_tile_ids, self.dungeon_tile_ids, self.entrances, self.start_pos = self.generate_world()
        
        # Create actual tile instances for effects
        self.overworld_tiles = {}
        self.dungeon_tiles = {}
        self._create_tile_instances()
        
        # World data
        self.treasure_chests = []
        self.rooms = []
        self.room_data = []
    
    def generate_world(self):
        """Generate the complete world using modular generators with debug output."""
        print("Generating terrain...")
        # 1. Generate base terrain
        overworld_map = self.overworld_generator.generate_terrain(self.width, self.height)
        
        print("Finding settlement locations...")
        # 2. Generate settlements
        settlement_locations = self.overworld_generator.get_suitable_settlement_locations(
            overworld_map, self.width, self.height, num_settlements=3)
        print(f"Found {len(settlement_locations)} settlement locations: {settlement_locations}")
        
        settlements, buildings = self.settlement_generator.generate_settlements(
            overworld_map, settlement_locations)
        print(f"Generated {len(settlements)} settlements with {len(buildings)} buildings")
        
        # Add buildings to building manager
        self.building_manager.add_buildings(buildings)
        
        # Debug: Print some building info
        for i, building in enumerate(buildings[:3]):  # Show first 3 buildings
            print(f"Building {i}: {building['building_type']} at {building['exterior_pos']}")
        
        print("Finding dungeon locations...")
        # 3. Generate dungeons
        dungeon_locations = self.overworld_generator.get_suitable_dungeon_locations(
            overworld_map, self.width, self.height, num_dungeons=5)
        print(f"Found {len(dungeon_locations)} dungeon locations: {dungeon_locations}")
        
        # Place dungeon entrances on overworld
        entrances = []
        for pos in dungeon_locations:
            x, y = pos
            print(f"Placing dungeon entrance at {x}, {y}")
            overworld_map[y][x] = 'dungeon_entrance'
        
        # Generate dungeon
        print("Generating dungeon...")
        dungeon_data = self.dungeon_generator.generate_dungeon(
            self.width, self.height, dungeon_locations)
        
        # Store dungeon data
        self.treasure_chests = dungeon_data['treasure_chests']
        self.rooms = dungeon_data['rooms']
        self.room_data = dungeon_data['room_data']
        print(f"Generated dungeon with {len(self.rooms)} rooms and {len(self.treasure_chests)} treasure chests")
        
        # Create entrance mappings
        for stair_data in dungeon_data['entrance_stairs']:
            entrances.append({
                'overworld': stair_data['overworld_pos'],
                'dungeon': stair_data['dungeon_pos']
            })
        print(f"Created {len(entrances)} entrance mappings")
        
        print("Finding start position...")
        # 4. Find start position near first settlement
        if settlement_locations:
            start_pos = self._find_start_position_near_settlement(
                overworld_map, settlement_locations[0])
            print(f"Start position: {start_pos}")
        else:
            start_pos = (self.width // 2, self.height // 2)
            print(f"No settlements, using center start: {start_pos}")
        
        # Debug: Count different tile types
        tile_counts = {}
        for row in overworld_map:
            for tile in row:
                tile_counts[tile] = tile_counts.get(tile, 0) + 1
        
        print("Tile counts:")
        for tile_type, count in sorted(tile_counts.items()):
            if count > 0:
                print(f"  {tile_type}: {count}")
        
        print("World generation complete!")
        return overworld_map, dungeon_data['map'], entrances, start_pos
    
    def _find_start_position_near_settlement(self, overworld_map, settlement_center):
        """Find a good starting position near a settlement."""
        settlement_x, settlement_y = settlement_center
        
        for radius in range(2, 8):
            for dx in range(-radius, radius + 1):
                for dy in range(-radius, radius + 1):
                    x, y = settlement_x + dx, settlement_y + dy
                    if (0 <= x < self.width and 0 <= y < self.height and
                        overworld_map[y][x] in ['road', 'settled_land', 'grasslands']):
                        return (x, y)
        
        return settlement_center
    
    def _create_tile_instances(self):
        """Create AsciiTile instances for tiles that might have effects."""
        for y in range(self.height):
            for x in range(self.width):
                overworld_id = self.overworld_tile_ids[y][x]
                
                # Create instances for special tiles that might have effects
                if overworld_id in ['forge', 'treasure_chest', 'river', 'desert']:
                    tile_def = self.ascii_defs.get_tile(overworld_id)
                    if tile_def:
                        self.overworld_tiles[(x, y)] = AsciiTile(
                            tile_def.base_char, tile_def.base_color, 
                            tile_def.solid, tile_def.name, tile_def.biome
                        )
                        # Copy effects
                        if tile_def.color_effect:
                            self.overworld_tiles[(x, y)].color_effect = tile_def.color_effect
                        if tile_def.char_effect:
                            self.overworld_tiles[(x, y)].char_effect = tile_def.char_effect
    
    def get_tile_render_info(self, x, y, player):
        """Get rendering information for a tile considering current location."""
        # Handle bounds checking
        if not (0 <= y < self.height and 0 <= x < self.width):
            return {'char': ' ', 'color': (0, 0, 0), 'solid': True, 'name': 'Void', 'biome': 'none'}
        
        # First check if location manager can handle this
        location_info = self.location_manager.get_tile_render_info(
            x, y, player, self.overworld_tile_ids, self.dungeon_tile_ids)
        
        if location_info:
            return location_info
        
        # Handle overworld and dungeon tiles
        if player.location == 'overworld':
            tile_id = self.overworld_tile_ids[y][x]
            
            # Check if we have a special instance with effects
            if (x, y) in self.overworld_tiles:
                return self.overworld_tiles[(x, y)].get_render_info()
            else:
                # Use base definition
                tile_def = self.ascii_defs.get_tile(tile_id)
                if tile_def:
                    return tile_def.get_render_info()
                else:
                    # Fallback for unknown tiles
                    return {'char': '?', 'color': (255, 0, 255), 'solid': False, 'name': f'Unknown({tile_id})', 'biome': 'none'}
        
        elif player.location == 'dungeon':
            tile_id = self.dungeon_tile_ids[y][x]
            
            # Check for special dungeon instances
            if (x, y) in self.dungeon_tiles:
                return self.dungeon_tiles[(x, y)].get_render_info()
            else:
                tile_def = self.ascii_defs.get_tile(tile_id)
                if tile_def:
                    return tile_def.get_render_info()
                else:
                    return {'char': '?', 'color': (255, 0, 255), 'solid': False, 'name': f'Unknown({tile_id})', 'biome': 'none'}
        
        # Fallback
        return {'char': '?', 'color': (255, 255, 255), 'solid': True, 'name': 'Unknown', 'biome': 'none'}
    
    def add_spell_effect(self, x, y, location, effect_type):
        """Add a spell effect to a tile."""
        if location == 'overworld':
            if 0 <= y < self.height and 0 <= x < self.width:
                tile_id = self.overworld_tile_ids[y][x]
                
                # Create instance if it doesn't exist
                if (x, y) not in self.overworld_tiles:
                    tile_def = self.ascii_defs.get_tile(tile_id)
                    if tile_def:
                        self.overworld_tiles[(x, y)] = AsciiTile(
                            tile_def.base_char, tile_def.base_color,
                            tile_def.solid, tile_def.name, tile_def.biome
                        )
                
                # Add effect
                if (x, y) in self.overworld_tiles:
                    self.ascii_defs.create_spell_effect(effect_type, self.overworld_tiles[(x, y)])
        
        elif location == 'dungeon':
            if 0 <= y < self.height and 0 <= x < self.width:
                tile_id = self.dungeon_tile_ids[y][x]
                
                if (x, y) not in self.dungeon_tiles:
                    tile_def = self.ascii_defs.get_tile(tile_id)
                    if tile_def:
                        self.dungeon_tiles[(x, y)] = AsciiTile(
                            tile_def.base_char, tile_def.base_color,
                            tile_def.solid, tile_def.name, tile_def.biome
                        )
                
                if (x, y) in self.dungeon_tiles:
                    self.ascii_defs.create_spell_effect(effect_type, self.dungeon_tiles[(x, y)])
    
    def draw(self, surface, font, camera, player):
        """Draw the world based on current location."""
        if player.location == 'overworld':
            self._draw_overworld(surface, font, camera, player)
        elif player.location == 'building_interior':
            self._draw_building_interior(surface, font, camera, player)
        elif player.location == 'dungeon':
            self._draw_dungeon(surface, font, camera, player)
    
    def _draw_overworld(self, surface, font, camera, player):
        """Draw the overworld with building exteriors."""
        # Calculate visible tile range
        start_x = max(0, int(camera.x))
        end_x = min(self.width, int(camera.x + surface.get_width() // TILE_SIZE) + 1)
        start_y = max(0, int(camera.y))
        end_y = min(self.height, int(camera.y + surface.get_height() // TILE_SIZE) + 1)
        
        # Draw terrain tiles
        for y in range(start_y, end_y):
            for x in range(start_x, end_x):
                # Skip building tiles - let building manager handle them
                tile_id = self.overworld_tile_ids[y][x]
                if not (tile_id.endswith('_roof') or tile_id.endswith('_door')):
                    render_info = self.get_tile_render_info(x, y, player)
                    
                    screen_x = (x - camera.x) * TILE_SIZE
                    screen_y = (y - camera.y) * TILE_SIZE
                    
                    tile_surface = font.render(
                        render_info['char'], 
                        True, 
                        render_info['color']
                    )
                    surface.blit(tile_surface, (screen_x, screen_y))
        
        # Draw building exteriors
        self.building_manager.draw_building_exterior(
            surface, font, camera, self.overworld_tile_ids, player)
    
    def _draw_building_interior(self, surface, font, camera, player):
        """Draw building interior with dimmed exterior background."""
        # Draw building interior
        self.building_manager.draw_building_interior(surface, font, camera, player)
    
    def _draw_dungeon(self, surface, font, camera, player):
        """Draw dungeon interior."""
        # Calculate visible tile range
        start_x = max(0, int(camera.x))
        end_x = min(self.width, int(camera.x + surface.get_width() // TILE_SIZE) + 1)
        start_y = max(0, int(camera.y))
        end_y = min(self.height, int(camera.y + surface.get_height() // TILE_SIZE) + 1)
        
        # Draw dungeon tiles
        for y in range(start_y, end_y):
            for x in range(start_x, end_x):
                render_info = self.get_tile_render_info(x, y, player)
                
                screen_x = (x - camera.x) * TILE_SIZE
                screen_y = (y - camera.y) * TILE_SIZE
                
                tile_surface = font.render(
                    render_info['char'], 
                    True, 
                    render_info['color']
                )
                surface.blit(tile_surface, (screen_x, screen_y))
    
    def get_description(self, x, y, player):
        """Get a description of the tile at the given coordinates."""
        # Check bounds
        if not (0 <= y < self.height and 0 <= x < self.width):
            return "Out of bounds"
        
        # Check if location manager can handle this
        location_desc = self.location_manager.get_description(
            x, y, player, self.overworld_tile_ids, self.dungeon_tile_ids)
        
        if location_desc:
            return location_desc
        
        # Handle overworld and dungeon descriptions
        if player.location == 'overworld':
            render_info = self.get_tile_render_info(x, y, player)
            return render_info['name']
        
        elif player.location == 'dungeon':
            render_info = self.get_tile_render_info(x, y, player)
            
            # Check for room descriptions
            for room, description in self.room_data:
                if room.collidepoint(x, y):
                    return f"{render_info['name']}: {description}"
            
            return render_info['name']
        
        return "Unknown"
    
    def get_action_prompt(self, x, y, player):
        """Get an action prompt for the tile at the given coordinates."""
        # Check bounds
        if not (0 <= y < self.height and 0 <= x < self.width):
            return ""
        
        # Check if location manager can handle this
        location_prompt = self.location_manager.get_action_prompt(
            x, y, player, self.overworld_tile_ids, self.dungeon_tile_ids)
        
        if location_prompt:
            return location_prompt
        
        # Handle overworld and dungeon prompts
        if player.location == 'overworld':
            # Check for building entrance
            if self.building_manager.can_enter_building(x, y, self.overworld_tile_ids):
                building = self.building_manager.get_building_at_position(x, y)
                if building:
                    building_type = building['building_type']
                    return f"Press Enter to enter the {building_type}"
            
            # Check for dungeon entrance
            tile_id = self.overworld_tile_ids[y][x]
            if tile_id == 'dungeon_entrance':
                return "Press Enter to enter the dungeon"
        
        elif player.location == 'dungeon':
            tile_id = self.dungeon_tile_ids[y][x]
            if tile_id == 'stairs_up':
                return "Press Enter to exit the dungeon"
            elif tile_id == 'treasure_chest':
                return "Press Y to take the treasure"
        
        return ""
    
    def is_solid(self, x, y, player):
        """Check if the tile at the given coordinates is solid (blocks movement)."""
        # Check bounds
        if not (0 <= y < self.height and 0 <= x < self.width):
            return True  # Out of bounds is solid
        
        # Check if location manager can handle this
        if self.location_manager.is_solid(x, y, player, self.overworld_tile_ids, self.dungeon_tile_ids):
            return True
        
        # Handle overworld and dungeon solidity
        render_info = self.get_tile_render_info(x, y, player)
        return render_info.get('solid', True)
    
    def get_biome(self, x, y, player):
        """Get the biome type for encounter generation."""
        if player.location != 'overworld':
            return 'dungeon'
        
        if 0 <= y < self.height and 0 <= x < self.width:
            tile_id = self.overworld_tile_ids[y][x]
            tile_def = self.ascii_defs.get_tile(tile_id)
            if tile_def:
                return tile_def.biome
        
        return 'plains'
    
    def update_tile_effects(self):
        """Update all active tile effects."""
        # Update overworld tiles
        for tile in self.overworld_tiles.values():
            tile.update_effects()
        
        # Update dungeon tiles
        for tile in self.dungeon_tiles.values():
            tile.update_effects()
    
    def handle_player_interaction(self, player):
        """Handle player interactions with the world (enter/exit buildings, etc.)."""
        print(f"Player interaction at {player.x}, {player.y} in {player.location}")
        
        # Check for location transitions
        if player.location == 'overworld':
            transition_type = self.location_manager.can_transition(
                player, self.overworld_tile_ids)
            print(f"Can transition: {transition_type}")
            
            if transition_type:
                result = self.location_manager.transition_to_location(
                    transition_type, player, self.overworld_tile_ids)
                print(f"Transition result: {result}")
                return result
        
        elif player.location == 'building_interior':
            transition_type = self.location_manager.can_transition(player, None)
            print(f"Can transition from building: {transition_type}")
            
            if transition_type:
                result = self.location_manager.transition_to_location(
                    transition_type, player)
                print(f"Building exit result: {result}")
                return result
        
        elif player.location == 'dungeon':
            transition_type = self.location_manager.can_transition(
                player, self.dungeon_tile_ids)
            print(f"Can transition from dungeon: {transition_type}")
            
            if transition_type:
                result = self.location_manager.transition_to_location(
                    transition_type, player, self.dungeon_tile_ids)
                print(f"Dungeon exit result: {result}")
                return result
        
        return False