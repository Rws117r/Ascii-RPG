# world/overworld_generator.py
"""
Overworld terrain and biome generation.
"""
import random
from ui.ascii_definitions import ASCII_DEFS

class OverworldGenerator:
    """Generates natural terrain, biomes, and geographical features."""
    
    def __init__(self):
        self.ascii_defs = ASCII_DEFS
    
    def generate_terrain(self, width, height):
        """Generate the base terrain with biomes and natural features."""
        # Create elevation and moisture maps
        elevation_map = self._generate_noise_map(width, height, feature_size=20, octaves=3)
        moisture_map = self._generate_noise_map(width, height, feature_size=16, octaves=2)
        temperature_map = self._generate_noise_map(width, height, feature_size=24, octaves=2)
        
        terrain_map = [['' for _ in range(width)] for _ in range(height)]
        
        # Generate biomes based on elevation, moisture, and temperature
        for y in range(height):
            for x in range(width):
                elevation = elevation_map[y][x]
                moisture = moisture_map[y][x]
                temperature = temperature_map[y][x]
                
                terrain_map[y][x] = self._determine_biome(elevation, moisture, temperature)
        
        # Apply climate zones (north = cold, south = hot)
        self._apply_climate_zones(terrain_map, temperature_map, height)
        
        # Add natural features
        self._generate_rivers(terrain_map, width, height)
        self._place_natural_landmarks(terrain_map, width, height)
        
        return terrain_map
    
    def _determine_biome(self, elevation, moisture, temperature):
        """Determine biome based on elevation, moisture, and temperature."""
        
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
    
    def _apply_climate_zones(self, terrain_map, temperature_map, height):
        """Apply climate zones - colder north, hotter south."""
        for y in range(height):
            latitude_factor = y / height
            
            for x in range(len(terrain_map[y])):
                current_tile = terrain_map[y][x]
                
                if latitude_factor < 0.2:  # Far north
                    if current_tile in ['desert', 'sandy_desert', 'high_desert']:
                        terrain_map[y][x] = 'barren' if random.random() > 0.5 else 'wasteland'
                    elif current_tile in ['jungle', 'dense_jungle']:
                        terrain_map[y][x] = 'deciduous_forest' if random.random() > 0.5 else 'coniferous_forest'
                
                elif latitude_factor > 0.8:  # Far south
                    if current_tile in ['barren', 'wasteland'] and random.random() < 0.3:
                        terrain_map[y][x] = 'desert' if random.random() > 0.5 else 'sandy_desert'
    
    def _generate_rivers(self, terrain_map, width, height):
        """Generate rivers flowing from mountains to oceans."""
        mountain_sources = []
        for y in range(height):
            for x in range(width):
                if terrain_map[y][x] in ['high_mountains', 'mountains'] and random.random() < 0.1:
                    mountain_sources.append((x, y))
        
        for source in mountain_sources:
            self._generate_river_from_source(terrain_map, source, width, height)
    
    def _generate_river_from_source(self, terrain_map, source, width, height):
        """Generate a single river from a mountain source."""
        x, y = source
        river_length = random.randint(10, 30)
        
        for _ in range(river_length):
            directions = [(0, 1), (1, 0), (0, -1), (-1, 0), (1, 1), (-1, 1)]
            dx, dy = random.choice(directions)
            
            new_x, new_y = x + dx, y + dy
            
            if 0 <= new_x < width and 0 <= new_y < height:
                current_tile = terrain_map[new_y][new_x]
                
                if current_tile not in ['high_mountains', 'mountains', 'ocean']:
                    terrain_map[new_y][new_x] = 'river'
                
                x, y = new_x, new_y
            else:
                break
    
    def _place_natural_landmarks(self, terrain_map, width, height):
        """Place natural landmarks like caves, ruins, etc."""
        # Place some ancient ruins
        num_ruins = random.randint(2, 5)
        for _ in range(num_ruins):
            attempts = 0
            while attempts < 50:
                x = random.randint(5, width - 5)
                y = random.randint(5, height - 5)
                
                if terrain_map[y][x] in ['deciduous_forest', 'coniferous_forest', 'wasteland', 'barren']:
                    # Create a small ruined area
                    for dx in range(-1, 2):
                        for dy in range(-1, 2):
                            if 0 <= x + dx < width and 0 <= y + dy < height:
                                if abs(dx) + abs(dy) <= 1:  # Cross pattern
                                    terrain_map[y + dy][x + dx] = 'barren'
                    break
                attempts += 1
    
    def get_suitable_settlement_locations(self, terrain_map, width, height, num_settlements=5):
        """Find suitable locations for settlements."""
        suitable_locations = []
        suitable_biomes = ['grasslands', 'dense_grasslands', 'deciduous_forest']
        
        attempts = 0
        while len(suitable_locations) < num_settlements and attempts < 200:
            x = random.randint(10, width - 10)
            y = random.randint(10, height - 10)
            
            if terrain_map[y][x] in suitable_biomes:
                # Check if location is suitable (not too close to other settlements)
                too_close = False
                for other_x, other_y in suitable_locations:
                    if abs(x - other_x) < 25 or abs(y - other_y) < 25:
                        too_close = True
                        break
                
                if not too_close:
                    # Check surrounding area is also suitable
                    area_suitable = True
                    for dx in range(-3, 4):
                        for dy in range(-3, 4):
                            check_x, check_y = x + dx, y + dy
                            if 0 <= check_x < width and 0 <= check_y < height:
                                if terrain_map[check_y][check_x] in ['ocean', 'river', 'lake', 'mountains', 'high_mountains']:
                                    if abs(dx) + abs(dy) <= 2:  # Close to center
                                        area_suitable = False
                                        break
                        if not area_suitable:
                            break
                    
                    if area_suitable:
                        suitable_locations.append((x, y))
            
            attempts += 1
        
        return suitable_locations
    
    def get_suitable_dungeon_locations(self, terrain_map, width, height, num_dungeons=8):
        """Find suitable locations for dungeon entrances."""
        suitable_locations = []
        suitable_biomes = ['deciduous_forest', 'coniferous_forest', 'mountains', 'high_mountains', 
                          'hills', 'forested_hills', 'rocky_hills', 'swamp', 'deep_swamp']
        
        attempts = 0
        while len(suitable_locations) < num_dungeons and attempts < 200:
            x = random.randint(5, width - 5)
            y = random.randint(5, height - 5)
            
            if terrain_map[y][x] in suitable_biomes:
                too_close = False
                for other_x, other_y in suitable_locations:
                    if abs(x - other_x) < 15 or abs(y - other_y) < 15:
                        too_close = True
                        break
                
                if not too_close:
                    suitable_locations.append((x, y))
            
            attempts += 1
        
        return suitable_locations
    
    def _generate_noise_map(self, width, height, feature_size=16, octaves=1):
        """Generate a noise map with multiple octaves for realistic terrain."""
        noise_map = [[0.0 for _ in range(width)] for _ in range(height)]
        
        for octave in range(octaves):
            octave_size = feature_size * (2 ** octave)
            octave_amplitude = 1.0 / (2 ** octave)
            
            low_res_w = width // octave_size + 2
            low_res_h = height // octave_size + 2
            low_res_map = [[random.random() for _ in range(low_res_w)] for _ in range(low_res_h)]
            
            for y in range(height):
                for x in range(width):
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
            for y in range(height):
                for x in range(width):
                    noise_map[y][x] = (noise_map[y][x] - min_val) / (max_val - min_val)
        
        return noise_map