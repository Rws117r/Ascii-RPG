# world/world.py
"""
Enhanced world generation using centralized ASCII definitions with layered elevation system.
"""
import random
import pygame
from config import TILE_SIZE
from ui.ascii_definitions import ASCII_DEFS, AsciiTile
from entities.items import create_random_item

class World:
    """Enhanced world with multiple biomes using layered ASCII definitions."""
    
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.rooms = []
        self.room_data = []
        self.treasure_chests = []
        self.ascii_defs = ASCII_DEFS
        
        # World will store tile IDs instead of characters
        self.overworld_tile_ids, self.dungeon_tile_ids, self.entrances, self.start_pos = self.generate_world()
        
        # Create actual tile instances for effects
        self.overworld_tiles = {}
        self.dungeon_tiles = {}
        self._create_tile_instances()
    
    def _create_tile_instances(self):
        """Create AsciiTile instances for each position that needs effects."""
        # Only create instances for tiles that might have effects
        # Most tiles can just reference the definition
        for y in range(self.height):
            for x in range(self.width):
                overworld_id = self.overworld_tile_ids[y][x]
                dungeon_id = self.dungeon_tile_ids[y][x]
                
                # Create instances for special tiles that might have effects
                if overworld_id in ['forge', 'treasure_chest', 'river', 'desert']:
                    tile_def = self.ascii_defs.get_tile(overworld_id)
                    if tile_def:
                        self.overworld_tiles[(x, y)] = AsciiTile(
                            tile_def.base_char, tile_def.base_color, 
                            tile_def.solid, tile_def.name, tile_def.biome,
                            tile_def.background_char, tile_def.background_color
                        )
                        # Copy effects
                        if tile_def.color_effect:
                            self.overworld_tiles[(x, y)].color_effect = tile_def.color_effect
                        if tile_def.char_effect:
                            self.overworld_tiles[(x, y)].char_effect = tile_def.char_effect

    def generate_world(self):
        """Generate a world with diverse biomes using tile IDs."""
        # Create elevation and moisture maps
        elevation_map = self._generate_noise_map(feature_size=20, octaves=3)
        moisture_map = self._generate_noise_map(feature_size=16, octaves=2)
        temperature_map = self._generate_noise_map(feature_size=24, octaves=2)
        
        overworld_map = [['' for _ in range(self.width)] for _ in range(self.height)]
        
        # Generate biomes based on elevation, moisture, and temperature
        for y in range(self.height):
            for x in range(self.width):
                elevation = elevation_map[y][x]
                moisture = moisture_map[y][x]
                temperature = temperature_map[y][x]
                
                overworld_map[y][x] = self._determine_biome(elevation, moisture, temperature)
        
        # Add climate zones (north = cold, south = hot)
        self._apply_climate_zones(overworld_map, temperature_map)
        
        # Add rivers
        self._generate_rivers(overworld_map)
        
        # Add settlements and roads
        settlements = self._generate_settlements(overworld_map)
        self._generate_roads(overworld_map, settlements)
        
        # Find a good starting position (near a settlement)
        start_pos = self._find_start_position(overworld_map, settlements)
        
        # Generate dungeons
        entrances = []
        num_entrances = random.randint(5, 8)
        dungeon_map, dungeon_exits = self._generate_dungeon(num_entrances)
        
        # Place dungeon entrances in appropriate biomes
        entrance_positions = self._place_dungeon_entrances(overworld_map, num_entrances)
        for i, pos in enumerate(entrance_positions):
            if i < len(dungeon_exits):
                overworld_map[pos[1]][pos[0]] = 'dungeon_entrance'
                entrances.append({'overworld': pos, 'dungeon': dungeon_exits[i]})
        
        return overworld_map, dungeon_map, entrances, start_pos

    def _determine_biome(self, elevation, moisture, temperature):
        """Determine biome considering elevation for layered system."""
        
        # WATER LEVEL (elevation 0-0.2)
        if elevation < 0.2:
            if moisture > 0.7:
                return 'ocean'
            elif moisture > 0.4:
                return 'lake'  
            else:
                return 'river'
        
        # VERY HIGH ELEVATION (0.8+) - Mountains
        elif elevation > 0.8:
            if elevation > 0.9:
                return 'high_mountains'
            else:
                return 'mountains'
        
        # HIGH ELEVATION (0.65-0.8) - Hills and high terrain
        elif elevation > 0.65:
            if moisture > 0.6 and temperature > 0.4:
                return 'forested_hills'  # Trees on hills
            elif moisture > 0.4:
                return 'grassy_hills'    # Grass on hills
            elif moisture < 0.2 and temperature > 0.7:
                return 'high_desert'     # Desert on elevated land
            elif moisture < 0.3:
                return 'rocky_hills'     # Rocky hills
            else:
                return 'hills'           # Basic hills
        
        # MEDIUM-HIGH ELEVATION (0.5-0.65) - Elevated biomes
        elif elevation > 0.5:
            if temperature > 0.7 and moisture < 0.3:
                return 'sandy_desert'    # Elevated desert
            elif moisture > 0.7 and temperature > 0.6:
                return 'dense_jungle'    # Elevated jungle
            elif moisture > 0.5 and temperature > 0.3:
                return 'coniferous_forest'  # Elevated forest
            elif moisture < 0.3:
                return 'wasteland'       # Elevated barren
            else:
                return 'dense_grasslands'  # Elevated grasslands
        
        # MEDIUM ELEVATION (0.3-0.5) - Main biomes
        elif elevation > 0.3:
            if temperature > 0.7 and moisture < 0.3:
                return 'desert'
            elif temperature > 0.6 and moisture > 0.7:
                return 'jungle'  
            elif moisture > 0.5 and temperature > 0.3 and temperature < 0.7:
                return 'deciduous_forest'
            elif moisture > 0.3:
                return 'grasslands'
            else:
                return 'barren'
        
        # LOW ELEVATION (0.2-0.3) - Lowland biomes
        else:
            if moisture > 0.8:
                return 'swamp' if random.random() > 0.3 else 'deep_swamp'
            elif moisture > 0.4:
                return 'grasslands'
            else:
                return 'barren'

    def _apply_climate_zones(self, overworld_map, temperature_map):
        """Apply climate zones - colder north, hotter south."""
        for y in range(self.height):
            latitude_factor = y / self.height
            
            for x in range(self.width):
                current_tile = overworld_map[y][x]
                
                if latitude_factor < 0.2:  # Far north
                    if current_tile in ['desert', 'sandy_desert', 'high_desert']:
                        overworld_map[y][x] = 'barren' if random.random() > 0.5 else 'wasteland'
                    elif current_tile in ['jungle', 'dense_jungle']:
                        overworld_map[y][x] = 'deciduous_forest' if random.random() > 0.5 else 'coniferous_forest'
                
                elif latitude_factor > 0.8:  # Far south
                    if current_tile in ['barren', 'wasteland'] and random.random() < 0.3:
                        overworld_map[y][x] = 'desert' if random.random() > 0.5 else 'sandy_desert'

    def _generate_rivers(self, overworld_map):
        """Generate rivers flowing from mountains to oceans."""
        mountain_sources = []
        for y in range(self.height):
            for x in range(self.width):
                if overworld_map[y][x] in ['high_mountains', 'mountains'] and random.random() < 0.1:
                    mountain_sources.append((x, y))
        
        for source in mountain_sources:
            self._generate_river_from_source(overworld_map, source)

    def _generate_river_from_source(self, overworld_map, source):
        """Generate a single river from a mountain source."""
        x, y = source
        river_length = random.randint(10, 30)
        
        for _ in range(river_length):
            directions = [(0, 1), (1, 0), (0, -1), (-1, 0), (1, 1), (-1, 1)]
            dx, dy = random.choice(directions)
            
            new_x, new_y = x + dx, y + dy
            
            if 0 <= new_x < self.width and 0 <= new_y < self.height:
                current_tile = overworld_map[new_y][new_x]
                
                if current_tile not in ['high_mountains', 'mountains', 'ocean', 'house', 'tavern', 'forge', 'castle', 'tower']:
                    overworld_map[new_y][new_x] = 'river'
                
                x, y = new_x, new_y
            else:
                break

    def _generate_settlements(self, overworld_map):
        """Generate settlements in suitable locations."""
        settlements = []
        num_settlements = random.randint(3, 6)
        
        for _ in range(num_settlements):
            attempts = 0
            while attempts < 100:
                x = random.randint(5, self.width - 6)
                y = random.randint(5, self.height - 6)
                
                if overworld_map[y][x] in ['grasslands', 'dense_grasslands', 'settled_land']:
                    suitable = True
                    for settlement in settlements:
                        if abs(x - settlement[0]) < 20 or abs(y - settlement[1]) < 20:
                            suitable = False
                            break
                    
                    if suitable:
                        settlement_type = random.choice(['village', 'town', 'city'])
                        size = {'village': 2, 'town': 3, 'city': 4}[settlement_type]
                        
                        self._build_settlement(overworld_map, x, y, size)
                        settlements.append((x, y, settlement_type))
                        break
                
                attempts += 1
        
        return settlements

    def _build_settlement(self, overworld_map, center_x, center_y, size):
        """Build a settlement of the given size using tile IDs."""
        # Clear area and add roads
        for dx in range(-size, size + 1):
            for dy in range(-size, size + 1):
                x, y = center_x + dx, center_y + dy
                if 0 <= x < self.width and 0 <= y < self.height:
                    if abs(dx) + abs(dy) <= size:
                        if dx == 0 or dy == 0:  # Main roads
                            overworld_map[y][x] = 'road'
                        else:
                            overworld_map[y][x] = 'settled_land'
        
        # Add buildings using tile IDs
        buildings = ['house', 'house', 'house', 'tavern', 'forge']
        if size >= 3:
            buildings.extend(['castle', 'tower'])
        
        for _ in range(size * 2):
            building = random.choice(buildings)
            attempts = 0
            while attempts < 20:
                dx = random.randint(-size, size)
                dy = random.randint(-size, size)
                x, y = center_x + dx, center_y + dy
                
                if (0 <= x < self.width and 0 <= y < self.height and 
                    overworld_map[y][x] == 'settled_land'):
                    overworld_map[y][x] = building
                    break
                attempts += 1

    def _generate_roads(self, overworld_map, settlements):
        """Generate roads connecting settlements."""
        for i, settlement in enumerate(settlements):
            if i == 0:
                continue
            
            start = settlement[:2]
            end = settlements[0][:2]
            
            self._build_road(overworld_map, start, end)

    def _build_road(self, overworld_map, start, end):
        """Build a road between two points."""
        x1, y1 = start
        x2, y2 = end
        
        current_x, current_y = x1, y1
        
        while current_x != x2:
            if current_x < x2:
                current_x += 1
            else:
                current_x -= 1
            
            if (0 <= current_x < self.width and 0 <= current_y < self.height and
                overworld_map[current_y][current_x] not in ['ocean', 'mountains', 'high_mountains', 'house', 'tavern', 'forge', 'castle', 'tower']):
                overworld_map[current_y][current_x] = 'road'
        
        while current_y != y2:
            if current_y < y2:
                current_y += 1
            else:
                current_y -= 1
            
            if (0 <= current_x < self.width and 0 <= current_y < self.height and
                overworld_map[current_y][current_x] not in ['ocean', 'mountains', 'high_mountains', 'house', 'tavern', 'forge', 'castle', 'tower']):
                overworld_map[current_y][current_x] = 'road'

    def _find_start_position(self, overworld_map, settlements):
        """Find a good starting position near a settlement."""
        if settlements:
            settlement_x, settlement_y = settlements[0][:2]
            
            for radius in range(2, 8):
                for dx in range(-radius, radius + 1):
                    for dy in range(-radius, radius + 1):
                        x, y = settlement_x + dx, settlement_y + dy
                        if (0 <= x < self.width and 0 <= y < self.height and
                            overworld_map[y][x] in ['road', 'settled_land', 'grasslands']):
                            return (x, y)
        
        return (self.width // 2, self.height // 2)

    def _place_dungeon_entrances(self, overworld_map, num_entrances):
        """Place dungeon entrances in appropriate biomes."""
        positions = []
        suitable_biomes = ['deciduous_forest', 'coniferous_forest', 'mountains', 'high_mountains', 'hills', 'forested_hills', 'rocky_hills', 'swamp', 'deep_swamp']
        
        attempts = 0
        while len(positions) < num_entrances and attempts < 200:
            x = random.randint(5, self.width - 5)
            y = random.randint(5, self.height - 5)
            
            if overworld_map[y][x] in suitable_biomes:
                too_close = False
                for pos in positions:
                    if abs(x - pos[0]) < 15 or abs(y - pos[1]) < 15:
                        too_close = True
                        break
                
                if not too_close:
                    positions.append((x, y))
            
            attempts += 1
        
        return positions

    def _generate_dungeon(self, num_entrances, max_rooms=30, min_room_size=5, max_room_size=12):
        """Generate a dungeon with rooms and corridors using tile IDs."""
        dungeon_map = [['dungeon_wall' for _ in range(self.width)] for _ in range(self.height)]
        self.rooms = []
        self.room_data = []
        dungeon_exits = []
        
        # Generate rooms
        for _ in range(max_rooms):
            w = random.randint(min_room_size, max_room_size)
            h = random.randint(min_room_size, max_room_size)
            x = random.randint(1, self.width - w - 2)
            y = random.randint(1, self.height - h - 2)
            new_room = pygame.Rect(x, y, w, h)
            
            if any(new_room.colliderect(other) for other in self.rooms):
                continue
            
            for i in range(new_room.left, new_room.right):
                for j in range(new_room.top, new_room.bottom):
                    dungeon_map[j][i] = 'dungeon_floor'
            
            if self.rooms:
                self._create_tunnel(dungeon_map, 
                                   self.rooms[-1].centerx, self.rooms[-1].centery,
                                   new_room.centerx, new_room.centery)
            
            self.rooms.append(new_room)
            descriptions = [
                "Dust and decay.", "Scratching noises.", "Glowing moss.",
                "Dripping water.", "Crude symbols.", "Ancient chamber."
            ]
            self.room_data.append((new_room, random.choice(descriptions)))
        
        # Add treasure chests
        for room in self.rooms:
            if random.random() < 0.2:
                chest_x = random.randint(room.left, room.right - 1)
                chest_y = random.randint(room.top, room.bottom - 1)
                if dungeon_map[chest_y][chest_x] == 'dungeon_floor':
                    dungeon_map[chest_y][chest_x] = 'treasure_chest'
                    self.treasure_chests.append({
                        'pos': (chest_x, chest_y),
                        'item': create_random_item()
                    })
        
        # Add exits
        if self.rooms:
            for i in range(num_entrances):
                if i < len(self.rooms):
                    exit_pos = (self.rooms[i].centerx, self.rooms[i].centery)
                    dungeon_map[exit_pos[1]][exit_pos[0]] = 'dungeon_exit'
                    dungeon_exits.append(exit_pos)
        
        return dungeon_map, dungeon_exits

    def _create_tunnel(self, dungeon_map, x1, y1, x2, y2):
        """Create a tunnel between two points."""
        if random.random() < 0.5:
            for x in range(min(x1, x2), max(x1, x2) + 1):
                dungeon_map[y1][x] = 'dungeon_floor'
            for y in range(min(y1, y2), max(y1, y2) + 1):
                dungeon_map[y][x2] = 'dungeon_floor'
        else:
            for y in range(min(y1, y2), max(y1, y2) + 1):
                dungeon_map[y][x1] = 'dungeon_floor'
            for x in range(min(x1, x2), max(x1, x2) + 1):
                dungeon_map[y2][x] = 'dungeon_floor'

    def get_tile_render_info(self, x, y, location):
        """Get rendering information for a tile at the given coordinates."""
        if location == 'overworld':
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
            tile_id = self.dungeon_tile_ids[y][x]
            
            # Check for special dungeon instances
            if (x, y) in self.dungeon_tiles:
                return self.dungeon_tiles[(x, y)].get_render_info()
            else:
                tile_def = self.ascii_defs.get_tile(tile_id)
                if tile_def:
                    return tile_def.get_render_info()
        
        # Fallback
        return {'char': '?', 'color': (255, 255, 255), 'solid': True, 'name': 'Unknown', 'biome': 'none'}

    def add_spell_effect(self, x, y, location, effect_type):
        """Add a spell effect to a tile."""
        if location == 'overworld':
            tile_id = self.overworld_tile_ids[y][x]
            
            # Create instance if it doesn't exist
            if (x, y) not in self.overworld_tiles:
                tile_def = self.ascii_defs.get_tile(tile_id)
                if tile_def:
                    self.overworld_tiles[(x, y)] = AsciiTile(
                        tile_def.base_char, tile_def.base_color,
                        tile_def.solid, tile_def.name, tile_def.biome,
                        tile_def.background_char, tile_def.background_color
                    )
            
            # Add effect
            if (x, y) in self.overworld_tiles:
                self.ascii_defs.create_spell_effect(effect_type, self.overworld_tiles[(x, y)])
        else:
            # Similar for dungeon tiles
            tile_id = self.dungeon_tile_ids[y][x]
            
            if (x, y) not in self.dungeon_tiles:
                tile_def = self.ascii_defs.get_tile(tile_id)
                if tile_def:
                    self.dungeon_tiles[(x, y)] = AsciiTile(
                        tile_def.base_char, tile_def.base_color,
                        tile_def.solid, tile_def.name, tile_def.biome,
                        tile_def.background_char, tile_def.background_color
                    )
            
            if (x, y) in self.dungeon_tiles:
                self.ascii_defs.create_spell_effect(effect_type, self.dungeon_tiles[(x, y)])

    def draw(self, surface, font, camera, location):
        """Draw the world with layered elevation + biome system."""
        # Calculate visible tile range
        start_x = max(0, int(camera.x))
        end_x = min(self.width, int(camera.x + surface.get_width() // TILE_SIZE) + 1)
        start_y = max(0, int(camera.y))
        end_y = min(self.height, int(camera.y + surface.get_height() // TILE_SIZE) + 1)
        
        # Draw tiles with layered system
        for y in range(start_y, end_y):
            for x in range(start_x, end_x):
                render_info = self.get_tile_render_info(x, y, location)
                
                # Calculate screen position
                screen_x = (x - camera.x) * TILE_SIZE
                screen_y = (y - camera.y) * TILE_SIZE
                
                # LAYER 1: Draw elevation background (if exists)
                if 'elevation_char' in render_info and render_info['elevation_char'] != ' ':
                    elevation_surface = font.render(
                        render_info['elevation_char'], 
                        True, 
                        render_info['elevation_color']
                    )
                    surface.blit(elevation_surface, (screen_x, screen_y))
                
                # LAYER 2: Draw main feature/biome (if not just background)
                if render_info['char'] != ' ':
                    feature_surface = font.render(
                        render_info['char'], 
                        True, 
                        render_info['color']
                    )
                    surface.blit(feature_surface, (screen_x, screen_y))

    def get_description(self, x, y, location):
        """Get a description of the tile at the given coordinates."""
        if 0 <= y < self.height and 0 <= x < self.width:
            render_info = self.get_tile_render_info(x, y, location)
            
            # Check for room descriptions in dungeons
            if location == 'dungeon':
                for room, description in self.room_data:
                    if room.collidepoint(x, y):
                        return f"{render_info['name']}: {description}"
            
            return render_info['name']
        
        return "Out of bounds"

    def get_action_prompt(self, x, y, location):
        """Get an action prompt for the tile at the given coordinates."""
        if 0 <= y < self.height and 0 <= x < self.width:
            if location == 'overworld':
                tile_id = self.overworld_tile_ids[y][x]
            else:
                tile_id = self.dungeon_tile_ids[y][x]
            
            if tile_id == 'dungeon_entrance':
                return "Press Enter to enter the dungeon"
            elif tile_id == 'dungeon_exit':
                return "Press Enter to exit the dungeon"
            elif tile_id == 'treasure_chest':
                return "Press Y to take the treasure"
            elif tile_id in ['house', 'tavern', 'forge']:
                building_names = {'house': 'house', 'tavern': 'tavern', 'forge': 'forge'}
                return f"Press Enter to enter the {building_names[tile_id]}"
        
        return ""

    def is_solid(self, x, y, location):
        """Check if the tile at the given coordinates is solid (blocks movement)."""
        if 0 <= y < self.height and 0 <= x < self.width:
            render_info = self.get_tile_render_info(x, y, location)
            return render_info.get('solid', True)
        
        return True  # Out of bounds is solid

    def get_biome(self, x, y, player_location):
        """Get the biome type for encounter generation."""
        if player_location != 'overworld':
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

    def _generate_noise_map(self, feature_size=16, octaves=1):
        """Generate a noise map with multiple octaves for more realistic terrain."""
        noise_map = [[0.0 for _ in range(self.width)] for _ in range(self.height)]
        
        for octave in range(octaves):
            octave_size = feature_size * (2 ** octave)
            octave_amplitude = 1.0 / (2 ** octave)
            
            low_res_w = self.width // octave_size + 2
            low_res_h = self.height // octave_size + 2
            low_res_map = [[random.random() for _ in range(low_res_w)] for _ in range(low_res_h)]
            
            for y in range(self.height):
                for x in range(self.width):
                    lx = x / octave_size
                    ly = y / octave_size
                    ix = int(lx)
                    iy = int(ly)
                    fx = lx - ix
                    fy = ly - iy
                    
                    # Bilinear interpolation
                    v00 = low_res_map[iy][ix]
                    v10 = low_res_map[iy][ix + 1]
                    v01 = low_res_map[iy + 1][ix]
                    v11 = low_res_map[iy + 1][ix + 1]
                    
                    nx0 = v00 * (1 - fx) + v10 * fx
                    nx1 = v01 * (1 - fx) + v11 * fx
                    noise_map[y][x] += (nx0 * (1 - fy) + nx1 * fy) * octave_amplitude
        
        # Normalize to 0-1 range
        max_val = max(max(row) for row in noise_map)
        min_val = min(min(row) for row in noise_map)
        
        if max_val > min_val:
            for y in range(self.height):
                for x in range(self.width):
                    noise_map[y][x] = (noise_map[y][x] - min_val) / (max_val - min_val)
        
        return noise_map
