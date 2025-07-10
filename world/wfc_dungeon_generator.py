# world/wfc_dungeon_generator.py
"""
Wave Function Collapse dungeon generator for creating complex, varied dungeon layouts.
Based on the technique used in Caves of Qud.
"""
import random
import copy
from collections import defaultdict
from entities.items import create_random_item

class WFCTile:
    """Represents a tile type with adjacency rules."""
    def __init__(self, tile_id, char, solid=False, weight=1.0):
        self.tile_id = tile_id
        self.char = char
        self.solid = solid
        self.weight = weight  # How likely this tile is to be chosen

class WFCPattern:
    """Represents a 3x3 pattern from the input template."""
    def __init__(self, pattern_id, tiles, weight=1.0):
        self.pattern_id = pattern_id
        self.tiles = tiles  # 3x3 grid of tile_ids
        self.weight = weight
        self.rotations = []  # Store rotated versions
        
    def rotate_90(self):
        """Return a 90-degree clockwise rotated version of this pattern."""
        rotated = [[None for _ in range(3)] for _ in range(3)]
        for i in range(3):
            for j in range(3):
                rotated[j][2-i] = self.tiles[i][j]
        return WFCPattern(f"{self.pattern_id}_r90", rotated, self.weight)
    
    def get_all_rotations(self):
        """Get all 4 rotations of this pattern."""
        if not self.rotations:
            current = self
            self.rotations = [current]
            for _ in range(3):
                current = current.rotate_90()
                self.rotations.append(current)
        return self.rotations

class WFCDungeonGenerator:
    """Wave Function Collapse dungeon generator."""
    
    def __init__(self):
        self.tile_types = {}
        self.patterns = []
        self.adjacency_rules = defaultdict(set)
        self._init_tile_types()
        self._init_patterns()
        self._build_adjacency_rules()
    
    def _init_tile_types(self):
        """Initialize the basic tile types."""
        self.tile_types = {
            'wall': WFCTile('wall', '#', solid=True, weight=0.3),
            'floor': WFCTile('floor', '.', solid=False, weight=1.0),
            'door': WFCTile('door', '+', solid=False, weight=0.1),
            'corridor': WFCTile('corridor', '.', solid=False, weight=0.8),
            'room_floor': WFCTile('room_floor', '.', solid=False, weight=0.9),
            'pillar': WFCTile('pillar', 'O', solid=True, weight=0.05),
            'stairs_up': WFCTile('stairs_up', '<', solid=False, weight=0.01),
            'treasure': WFCTile('treasure', '$', solid=False, weight=0.02),
        }
    
    def _init_patterns(self):
        """Initialize pattern templates for different dungeon features."""
        
        # Basic room patterns
        room_patterns = [
            # Simple room
            [
                ['wall', 'wall', 'wall'],
                ['wall', 'room_floor', 'wall'],
                ['wall', 'wall', 'wall']
            ],
            # Room with door
            [
                ['wall', 'wall', 'wall'],
                ['wall', 'room_floor', 'door'],
                ['wall', 'wall', 'wall']
            ],
            # Corridor junction
            [
                ['wall', 'corridor', 'wall'],
                ['corridor', 'corridor', 'corridor'],
                ['wall', 'corridor', 'wall']
            ],
            # Corridor bend
            [
                ['wall', 'wall', 'wall'],
                ['wall', 'corridor', 'corridor'],
                ['wall', 'corridor', 'wall']
            ],
            # Large room corner
            [
                ['wall', 'wall', 'wall'],
                ['wall', 'room_floor', 'room_floor'],
                ['wall', 'room_floor', 'room_floor']
            ],
            # Pillar room
            [
                ['room_floor', 'room_floor', 'room_floor'],
                ['room_floor', 'pillar', 'room_floor'],
                ['room_floor', 'room_floor', 'room_floor']
            ],
            # Treasure alcove
            [
                ['wall', 'wall', 'wall'],
                ['wall', 'treasure', 'wall'],
                ['wall', 'door', 'wall']
            ],
        ]
        
        # Convert to WFCPattern objects and add rotations
        pattern_id = 0
        for pattern_tiles in room_patterns:
            pattern = WFCPattern(f"pattern_{pattern_id}", pattern_tiles)
            self.patterns.append(pattern)
            
            # Add all rotations
            for rotated in pattern.get_all_rotations()[1:]:  # Skip original
                self.patterns.append(rotated)
            
            pattern_id += 1
    
    def _build_adjacency_rules(self):
        """Build adjacency rules from patterns."""
        # Extract adjacency rules from all patterns
        for pattern in self.patterns:
            for i in range(3):
                for j in range(3):
                    center_tile = pattern.tiles[i][j]
                    
                    # Check all 4 directions
                    directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]  # N, S, W, E
                    for di, dj in directions:
                        ni, nj = i + di, j + dj
                        if 0 <= ni < 3 and 0 <= nj < 3:
                            neighbor_tile = pattern.tiles[ni][nj]
                            self.adjacency_rules[center_tile].add(neighbor_tile)
    
    def generate_dungeon(self, width, height, entrance_locations, max_attempts=1000):
        """Generate a dungeon using Wave Function Collapse."""
        print(f"Generating WFC dungeon {width}x{height}")
        
        # Initialize the wave function collapse grid
        possibilities = self._init_wfc_grid(width, height)
        
        # Track generated content
        rooms = []
        treasure_chests = []
        entrance_stairs = []
        
        # Generate using WFC
        dungeon_map = self._run_wfc(width, height, possibilities, max_attempts)
        
        # Post-processing: Connect disconnected areas
        dungeon_map = self._connect_areas(dungeon_map, width, height)
        
        # Post-processing: Place special features
        self._place_special_features(dungeon_map, width, height, entrance_locations, 
                                   rooms, treasure_chests, entrance_stairs)
        
        # Create room data for descriptions
        room_data = []
        for i, room in enumerate(rooms):
            descriptions = [
                "Ancient stone chambers echo with mystery.",
                "Flickering torchlight dances on worn walls.",
                "The air is thick with the scent of ages past.",
                "Strange runes are carved into the weathered stone.",
                "Shadows move in the corners of your vision.",
                "The silence here is almost deafening."
            ]
            room_data.append((room, random.choice(descriptions)))
        
        return {
            'map': dungeon_map,
            'rooms': rooms,
            'room_data': room_data,
            'treasure_chests': treasure_chests,
            'entrance_stairs': entrance_stairs
        }
    
    def _init_wfc_grid(self, width, height):
        """Initialize the WFC grid with all possibilities."""
        all_tiles = list(self.tile_types.keys())
        possibilities = []
        
        for y in range(height):
            row = []
            for x in range(width):
                # Border tiles are more likely to be walls
                if x == 0 or x == width-1 or y == 0 or y == height-1:
                    row.append(['wall'])
                else:
                    row.append(all_tiles.copy())
            possibilities.append(row)
        
        return possibilities
    
    def _run_wfc(self, width, height, possibilities, max_attempts):
        """Run the Wave Function Collapse algorithm."""
        attempts = 0
        
        while attempts < max_attempts:
            # Find the cell with minimum non-zero possibilities
            min_entropy = float('inf')
            candidates = []
            
            for y in range(height):
                for x in range(width):
                    entropy = len(possibilities[y][x])
                    if 1 < entropy < min_entropy:
                        min_entropy = entropy
                        candidates = [(x, y)]
                    elif entropy == min_entropy and entropy > 1:
                        candidates.append((x, y))
            
            # If no candidates, we're done
            if not candidates:
                break
            
            # Choose a random candidate and collapse it
            x, y = random.choice(candidates)
            possible_tiles = possibilities[y][x]
            
            # Weight the choice based on tile weights
            weights = [self.tile_types[tile].weight for tile in possible_tiles]
            chosen_tile = random.choices(possible_tiles, weights=weights)[0]
            
            # Collapse this cell
            possibilities[y][x] = [chosen_tile]
            
            # Propagate constraints
            self._propagate_constraints(x, y, width, height, possibilities)
            
            attempts += 1
        
        # Convert possibilities to final map
        dungeon_map = []
        for y in range(height):
            row = []
            for x in range(width):
                if len(possibilities[y][x]) == 1:
                    tile_id = possibilities[y][x][0]
                    row.append(self._convert_tile_to_dungeon_tile(tile_id))
                else:
                    # Fallback if not fully collapsed
                    row.append('dungeon_wall')
            dungeon_map.append(row)
        
        return dungeon_map
    
    def _propagate_constraints(self, start_x, start_y, width, height, possibilities):
        """Propagate constraints from a collapsed cell."""
        stack = [(start_x, start_y)]
        
        while stack:
            x, y = stack.pop()
            current_tiles = possibilities[y][x]
            
            # Check all 4 neighbors
            for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                nx, ny = x + dx, y + dy
                
                if 0 <= nx < width and 0 <= ny < height:
                    neighbor_possibilities = possibilities[ny][nx]
                    
                    # Find valid neighbors based on adjacency rules
                    valid_neighbors = set()
                    for current_tile in current_tiles:
                        valid_neighbors.update(self.adjacency_rules[current_tile])
                    
                    # Filter neighbor possibilities
                    new_possibilities = [tile for tile in neighbor_possibilities 
                                       if tile in valid_neighbors]
                    
                    # If we reduced possibilities, add to stack for further propagation
                    if len(new_possibilities) < len(neighbor_possibilities):
                        possibilities[ny][nx] = new_possibilities
                        if new_possibilities:  # Avoid empty possibilities
                            stack.append((nx, ny))
    
    def _convert_tile_to_dungeon_tile(self, tile_id):
        """Convert WFC tile ID to dungeon tile ID."""
        conversion = {
            'wall': 'dungeon_wall',
            'floor': 'dungeon_floor',
            'door': 'dungeon_floor',  # Doors will be placed in post-processing
            'corridor': 'dungeon_floor',
            'room_floor': 'dungeon_floor',
            'pillar': 'dungeon_wall',  # Pillars as special walls for now
            'stairs_up': 'stairs_up',
            'treasure': 'treasure_chest',
        }
        return conversion.get(tile_id, 'dungeon_wall')
    
    def _connect_areas(self, dungeon_map, width, height):
        """Connect disconnected floor areas using A* pathfinding."""
        # Find all floor areas
        floor_areas = self._find_floor_areas(dungeon_map, width, height)
        
        if len(floor_areas) <= 1:
            return dungeon_map
        
        # Connect each area to the largest one
        largest_area = max(floor_areas, key=len)
        
        for area in floor_areas:
            if area != largest_area:
                # Find closest points between areas
                start = random.choice(list(area))
                target = random.choice(list(largest_area))
                
                # Create a simple corridor
                self._create_corridor(dungeon_map, start, target, width, height)
        
        return dungeon_map
    
    def _find_floor_areas(self, dungeon_map, width, height):
        """Find connected floor areas using flood fill."""
        visited = set()
        areas = []
        
        for y in range(height):
            for x in range(width):
                if (x, y) not in visited and dungeon_map[y][x] == 'dungeon_floor':
                    area = set()
                    stack = [(x, y)]
                    
                    while stack:
                        cx, cy = stack.pop()
                        if (cx, cy) in visited:
                            continue
                        
                        visited.add((cx, cy))
                        area.add((cx, cy))
                        
                        # Check neighbors
                        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                            nx, ny = cx + dx, cy + dy
                            if (0 <= nx < width and 0 <= ny < height and
                                (nx, ny) not in visited and
                                dungeon_map[ny][nx] == 'dungeon_floor'):
                                stack.append((nx, ny))
                    
                    if area:
                        areas.append(area)
        
        return areas
    
    def _create_corridor(self, dungeon_map, start, target, width, height):
        """Create a simple L-shaped corridor between two points."""
        x1, y1 = start
        x2, y2 = target
        
        # Move horizontally first
        x = x1
        while x != x2:
            if 0 <= x < width and 0 <= y1 < height:
                dungeon_map[y1][x] = 'dungeon_floor'
            x += 1 if x < x2 else -1
        
        # Then move vertically
        y = y1
        while y != y2:
            if 0 <= x2 < width and 0 <= y < height:
                dungeon_map[y][x2] = 'dungeon_floor'
            y += 1 if y < y2 else -1
    
    def _place_special_features(self, dungeon_map, width, height, entrance_locations,
                               rooms, treasure_chests, entrance_stairs):
        """Place special features like entrances, treasures, and define rooms."""
        
        # Find floor areas to define as rooms
        floor_areas = self._find_floor_areas(dungeon_map, width, height)
        
        # Convert floor areas to room rectangles
        for area in floor_areas:
            if len(area) >= 9:  # Minimum room size
                min_x = min(pos[0] for pos in area)
                max_x = max(pos[0] for pos in area)
                min_y = min(pos[1] for pos in area)
                max_y = max(pos[1] for pos in area)
                
                import pygame
                room_rect = pygame.Rect(min_x, min_y, max_x - min_x + 1, max_y - min_y + 1)
                rooms.append(room_rect)
        
        # Place entrance stairs
        for i, entrance_pos in enumerate(entrance_locations):
            if i < len(rooms) and rooms:
                # Place in random room
                room = random.choice(rooms)
                stairs_x = random.randint(room.left, room.right - 1)
                stairs_y = random.randint(room.top, room.bottom - 1)
                
                if (0 <= stairs_x < width and 0 <= stairs_y < height and
                    dungeon_map[stairs_y][stairs_x] == 'dungeon_floor'):
                    dungeon_map[stairs_y][stairs_x] = 'stairs_up'
                    entrance_stairs.append({
                        'dungeon_pos': (stairs_x, stairs_y),
                        'overworld_pos': entrance_pos
                    })
        
        # Place treasure chests in rooms
        for room in rooms:
            if random.random() < 0.3:  # 30% chance for treasure
                chest_x = random.randint(room.left, room.right - 1)
                chest_y = random.randint(room.top, room.bottom - 1)
                
                if (0 <= chest_x < width and 0 <= chest_y < height and
                    dungeon_map[chest_y][chest_x] == 'dungeon_floor'):
                    dungeon_map[chest_y][chest_x] = 'treasure_chest'
                    treasure_chests.append({
                        'pos': (chest_x, chest_y),
                        'item': create_random_item()
                    })