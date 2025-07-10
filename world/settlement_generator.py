# world/settlement_generator.py (Fixed version)
"""
Fixed settlement generator with more buildings and better layout.
"""
import random
from world.building_generator import BuildingGenerator

class SettlementGenerator:
    """Generates settlements, villages, and road networks with proper building distribution."""
    
    def __init__(self):
        self.building_generator = BuildingGenerator()
    
    def generate_settlements(self, terrain_map, settlement_locations):
        """Generate settlements at the given locations with more buildings."""
        settlements = []
        buildings = []
        
        for i, (x, y) in enumerate(settlement_locations):
            # Determine settlement type and size
            if i == 0:  # First settlement is always largest
                settlement_type = 'town'
                size = 5
            elif i == 1:  # Second settlement is medium
                settlement_type = 'village'
                size = 4
            else:
                settlement_type = random.choice(['village', 'hamlet'])
                size = {'hamlet': 3, 'village': 4, 'town': 5}[settlement_type]
            
            print(f"Generating {settlement_type} (size {size}) at {x}, {y}")
            
            # Generate the settlement
            settlement_buildings = self._layout_settlement(terrain_map, x, y, size, settlement_type)
            settlement = {
                'center': (x, y),
                'type': settlement_type,
                'size': size,
                'buildings': settlement_buildings
            }
            
            settlements.append(settlement)
            buildings.extend(settlement_buildings)
            print(f"  Generated {len(settlement_buildings)} buildings")
        
        # Generate road network
        self._generate_roads(terrain_map, settlements)
        
        return settlements, buildings
    
    def _layout_settlement(self, terrain_map, center_x, center_y, size, settlement_type):
        """Layout a settlement with more buildings and better distribution."""
        buildings = []
        width = len(terrain_map[0])
        height = len(terrain_map)
        
        # Clear larger area and add roads/settled land
        road_area = size + 1
        for dx in range(-road_area, road_area + 1):
            for dy in range(-road_area, road_area + 1):
                x, y = center_x + dx, center_y + dy
                if 0 <= x < width and 0 <= y < height:
                    distance = abs(dx) + abs(dy)
                    if distance <= size:
                        if dx == 0 or dy == 0:  # Main roads (cross pattern)
                            terrain_map[y][x] = 'road'
                        elif distance <= size - 1:  # Inner area
                            terrain_map[y][x] = 'settled_land'
        
        # Add additional roads for larger settlements
        if size >= 4:
            # Add diagonal roads
            for i in range(1, size):
                # NE-SW diagonal
                if 0 <= center_x + i < width and 0 <= center_y + i < height:
                    terrain_map[center_y + i][center_x + i] = 'road'
                if 0 <= center_x - i < width and 0 <= center_y - i < height:
                    terrain_map[center_y - i][center_x - i] = 'road'
                
                # NW-SE diagonal  
                if 0 <= center_x + i < width and 0 <= center_y - i < height:
                    terrain_map[center_y - i][center_x + i] = 'road'
                if 0 <= center_x - i < width and 0 <= center_y + i < height:
                    terrain_map[center_y + i][center_x - i] = 'road'
        
        # Define building types by settlement type (MORE BUILDINGS!)
        building_types = self._get_building_types_for_settlement(settlement_type, size)
        print(f"  Planning {len(building_types)} buildings: {building_types}")
        
        # Place buildings with better distribution
        placed_positions = []
        for building_type in building_types:
            building_size = self._get_building_exterior_size(building_type)
            building_pos = self._find_building_position(terrain_map, center_x, center_y, 
                                                       size, building_size, placed_positions)
            
            if building_pos:
                # Place building exterior on terrain
                self._place_building_exterior(terrain_map, building_pos, building_size, building_type)
                
                # Generate building interior
                building = self.building_generator.generate_building(
                    building_type, building_pos, building_size)
                buildings.append(building)
                placed_positions.append(building_pos)
                print(f"    Placed {building_type} at {building_pos}")
            else:
                print(f"    Failed to place {building_type}")
        
        return buildings
    
    def _get_building_types_for_settlement(self, settlement_type, size):
        """Get building types appropriate for settlement type with MORE variety."""
        
        if settlement_type == 'hamlet':
            return [
                'house', 'house', 'house', 'house',  # More houses
                'tavern'  # Small hamlet gets tavern
            ]
        elif settlement_type == 'village':
            return [
                'house', 'house', 'house', 'house', 'house', 'house',  # 6 houses
                'tavern', 'forge',  # Essential buildings
                'house'  # Extra house
            ]
        elif settlement_type == 'town':
            return [
                'house', 'house', 'house', 'house', 'house', 'house', 'house', 'house',  # 8 houses
                'tavern', 'tavern',  # 2 taverns for larger town
                'forge', 'forge',  # 2 forges
                'tower',  # Town gets a tower
                'house', 'house'  # Extra houses
            ]
        
        return ['house', 'house', 'tavern']  # Fallback
    
    def _get_building_exterior_size(self, building_type):
        """Get the exterior footprint size for a building type."""
        sizes = {
            'house': (3, 3),
            'tavern': (4, 4), 
            'forge': (3, 4),
            'tower': (4, 4),  # Smaller tower for better placement
            'castle': (6, 6)   # Smaller castle
        }
        return sizes.get(building_type, (3, 3))
    
    def _find_building_position(self, terrain_map, center_x, center_y, settlement_size, 
                               building_size, existing_positions):
        """Find a suitable position for a building with better placement logic."""
        width = len(terrain_map[0])
        height = len(terrain_map)
        building_w, building_h = building_size
        
        # Try multiple placement strategies
        strategies = [
            self._try_grid_placement,
            self._try_random_placement,
            self._try_edge_placement
        ]
        
        for strategy in strategies:
            pos = strategy(terrain_map, center_x, center_y, settlement_size, 
                          building_size, existing_positions)
            if pos:
                return pos
        
        return None
    
    def _try_grid_placement(self, terrain_map, center_x, center_y, settlement_size, 
                           building_size, existing_positions):
        """Try to place building on a grid pattern."""
        width = len(terrain_map[0])
        height = len(terrain_map)
        building_w, building_h = building_size
        
        # Try grid positions around the center
        for grid_x in range(-settlement_size + 1, settlement_size, 2):
            for grid_y in range(-settlement_size + 1, settlement_size, 2):
                x = center_x + grid_x
                y = center_y + grid_y
                
                if self._is_position_valid(terrain_map, x, y, building_size, existing_positions):
                    return (x, y)
        
        return None
    
    def _try_random_placement(self, terrain_map, center_x, center_y, settlement_size, 
                             building_size, existing_positions):
        """Try random placement within settlement bounds."""
        width = len(terrain_map[0])
        height = len(terrain_map)
        building_w, building_h = building_size
        
        for attempt in range(50):
            # Random position within settlement bounds
            dx = random.randint(-settlement_size + 1, settlement_size - building_w)
            dy = random.randint(-settlement_size + 1, settlement_size - building_h)
            x, y = center_x + dx, center_y + dy
            
            if self._is_position_valid(terrain_map, x, y, building_size, existing_positions):
                return (x, y)
        
        return None
    
    def _try_edge_placement(self, terrain_map, center_x, center_y, settlement_size, 
                           building_size, existing_positions):
        """Try placement at settlement edges."""
        width = len(terrain_map[0])
        height = len(terrain_map)
        building_w, building_h = building_size
        
        # Try edge positions
        edges = [
            (center_x - settlement_size + 1, center_y),  # West
            (center_x + settlement_size - building_w, center_y),  # East
            (center_x, center_y - settlement_size + 1),  # North
            (center_x, center_y + settlement_size - building_h)   # South
        ]
        
        for x, y in edges:
            if self._is_position_valid(terrain_map, x, y, building_size, existing_positions):
                return (x, y)
        
        return None
    
    def _is_position_valid(self, terrain_map, x, y, building_size, existing_positions):
        """Check if a position is valid for building placement."""
        width = len(terrain_map[0])
        height = len(terrain_map)
        building_w, building_h = building_size
        
        # Check bounds
        if not (0 <= x < width - building_w and 0 <= y < height - building_h):
            return False
        
        # Check if area is clear
        for bx in range(x, x + building_w):
            for by in range(y, y + building_h):
                tile = terrain_map[by][bx]
                if tile not in ['settled_land', 'grasslands', 'road']:
                    return False
        
        # Check distance from other buildings (minimum 2 tiles apart)
        for other_x, other_y in existing_positions:
            if abs(x - other_x) < building_w + 1 or abs(y - other_y) < building_h + 1:
                return False
        
        return True
    
    def _place_building_exterior(self, terrain_map, pos, size, building_type):
        """Place building exterior tiles on the terrain map."""
        x, y = pos
        width, height = size
        
        # Place roof tiles (most of the building)
        for bx in range(x, x + width):
            for by in range(y, y + height):
                terrain_map[by][bx] = f'{building_type}_roof'
        
        # Place door (always on south side for now)
        door_x = x + width // 2
        door_y = y + height - 1
        terrain_map[door_y][door_x] = f'{building_type}_door'
    
    def _generate_roads(self, terrain_map, settlements):
        """Generate roads connecting all settlements."""
        if len(settlements) < 2:
            return
        
        print("Generating roads between settlements...")
        
        # Connect each settlement to the main settlement (first one) AND to the next one
        main_settlement = settlements[0]
        main_x, main_y = main_settlement['center']
        
        # Connect all to main settlement
        for i, settlement in enumerate(settlements[1:], 1):
            start_x, start_y = settlement['center']
            print(f"  Building road from settlement {i} to main settlement")
            self._build_road(terrain_map, (start_x, start_y), (main_x, main_y))
        
        # Also connect consecutive settlements for a network
        for i in range(len(settlements) - 1):
            start_x, start_y = settlements[i]['center']
            end_x, end_y = settlements[i + 1]['center']
            print(f"  Building road between settlement {i} and {i + 1}")
            self._build_road(terrain_map, (start_x, start_y), (end_x, end_y))
    
    def _build_road(self, terrain_map, start, end):
        """Build a road between two points with improved pathfinding."""
        x1, y1 = start
        x2, y2 = end
        width = len(terrain_map[0])
        height = len(terrain_map)
        
        current_x, current_y = x1, y1
        
        # Move horizontally first
        while current_x != x2:
            if current_x < x2:
                current_x += 1
            else:
                current_x -= 1
            
            if (0 <= current_x < width and 0 <= current_y < height):
                tile = terrain_map[current_y][current_x]
                if not (tile.endswith('_roof') or tile.endswith('_door') or 
                       tile in ['ocean', 'lake', 'mountains', 'high_mountains']):
                    terrain_map[current_y][current_x] = 'road'
        
        # Then move vertically
        while current_y != y2:
            if current_y < y2:
                current_y += 1
            else:
                current_y -= 1
            
            if (0 <= current_x < width and 0 <= current_y < height):
                tile = terrain_map[current_y][current_x]
                if not (tile.endswith('_roof') or tile.endswith('_door') or 
                       tile in ['ocean', 'lake', 'mountains', 'high_mountains']):
                    terrain_map[current_y][current_x] = 'road'