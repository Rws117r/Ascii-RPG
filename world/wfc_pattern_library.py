# world/wfc_pattern_library.py
"""
Advanced pattern library for Wave Function Collapse dungeon generation.
Includes themed pattern sets and sophisticated dungeon features.
"""

class WFCPatternLibrary:
    """Library of pattern sets for different dungeon themes and features."""
    
    def __init__(self):
        self.pattern_sets = {
            'classic_dungeon': self._get_classic_patterns(),
            'natural_caves': self._get_cave_patterns(),
            'ancient_temple': self._get_temple_patterns(),
            'underground_city': self._get_city_patterns(),
            'crypts': self._get_crypt_patterns()
        }
    
    def get_patterns(self, theme='classic_dungeon'):
        """Get pattern set for a specific theme."""
        return self.pattern_sets.get(theme, self.pattern_sets['classic_dungeon'])
    
    def _get_classic_patterns(self):
        """Classic dungeon patterns - rooms, corridors, doors."""
        return [
            # Small room with single door
            [
                ['wall', 'wall', 'wall'],
                ['wall', 'room_floor', 'wall'],
                ['wall', 'door', 'wall']
            ],
            # Large room corner (creates bigger spaces when tiled)
            [
                ['wall', 'wall', 'wall'],
                ['wall', 'room_floor', 'room_floor'],
                ['wall', 'room_floor', 'room_floor']
            ],
            # Corridor T-junction
            [
                ['wall', 'corridor', 'wall'],
                ['corridor', 'corridor', 'corridor'],
                ['wall', 'corridor', 'wall']
            ],
            # Corridor straight
            [
                ['wall', 'wall', 'wall'],
                ['corridor', 'corridor', 'corridor'],
                ['wall', 'wall', 'wall']
            ],
            # Room with pillar
            [
                ['room_floor', 'room_floor', 'room_floor'],
                ['room_floor', 'pillar', 'room_floor'],
                ['room_floor', 'room_floor', 'room_floor']
            ],
            # Guard room with door
            [
                ['wall', 'door', 'wall'],
                ['room_floor', 'room_floor', 'room_floor'],
                ['wall', 'wall', 'wall']
            ],
            # Secret passage
            [
                ['wall', 'wall', 'wall'],
                ['wall', 'secret', 'wall'],
                ['wall', 'wall', 'wall']
            ],
            # Treasure room
            [
                ['wall', 'wall', 'wall'],
                ['door', 'treasure', 'wall'],
                ['wall', 'wall', 'wall']
            ]
        ]
    
    def _get_cave_patterns(self):
        """Natural cave patterns - organic shapes, water features."""
        return [
            # Cave chamber
            [
                ['wall', 'cave_floor', 'wall'],
                ['cave_floor', 'cave_floor', 'cave_floor'],
                ['wall', 'cave_floor', 'wall']
            ],
            # Underground stream
            [
                ['cave_floor', 'cave_floor', 'cave_floor'],
                ['water', 'water', 'water'],
                ['cave_floor', 'cave_floor', 'cave_floor']
            ],
            # Stalactite formation
            [
                ['cave_floor', 'cave_floor', 'cave_floor'],
                ['cave_floor', 'stalactite', 'cave_floor'],
                ['cave_floor', 'cave_floor', 'cave_floor']
            ],
            # Cave tunnel
            [
                ['wall', 'cave_floor', 'wall'],
                ['wall', 'cave_floor', 'wall'],
                ['wall', 'cave_floor', 'wall']
            ],
            # Cavern opening
            [
                ['wall', 'wall', 'cave_floor'],
                ['wall', 'cave_floor', 'cave_floor'],
                ['cave_floor', 'cave_floor', 'cave_floor']
            ],
            # Underground lake edge
            [
                ['cave_floor', 'cave_floor', 'cave_floor'],
                ['cave_floor', 'water', 'water'],
                ['cave_floor', 'water', 'water']
            ]
        ]
    
    def _get_temple_patterns(self):
        """Ancient temple patterns - ceremonial rooms, altars."""
        return [
            # Temple chamber with altar
            [
                ['wall', 'wall', 'wall'],
                ['wall', 'altar', 'wall'],
                ['temple_floor', 'temple_floor', 'temple_floor']
            ],
            # Ceremonial hall
            [
                ['temple_floor', 'temple_floor', 'temple_floor'],
                ['temple_floor', 'temple_floor', 'temple_floor'],
                ['temple_floor', 'temple_floor', 'temple_floor']
            ],
            # Sacred pillar
            [
                ['temple_floor', 'temple_floor', 'temple_floor'],
                ['temple_floor', 'sacred_pillar', 'temple_floor'],
                ['temple_floor', 'temple_floor', 'temple_floor']
            ],
            # Temple entrance
            [
                ['wall', 'temple_door', 'wall'],
                ['temple_floor', 'temple_floor', 'temple_floor'],
                ['temple_floor', 'temple_floor', 'temple_floor']
            ],
            # Shrine alcove
            [
                ['wall', 'wall', 'wall'],
                ['wall', 'shrine', 'wall'],
                ['wall', 'temple_door', 'wall']
            ],
            # Temple corridor with murals
            [
                ['mural', 'mural', 'mural'],
                ['temple_floor', 'temple_floor', 'temple_floor'],
                ['mural', 'mural', 'mural']
            ]
        ]
    
    def _get_city_patterns(self):
        """Underground city patterns - streets, buildings, plazas."""
        return [
            # City street
            [
                ['building', 'building', 'building'],
                ['street', 'street', 'street'],
                ['building', 'building', 'building']
            ],
            # City plaza
            [
                ['street', 'street', 'street'],
                ['street', 'plaza', 'street'],
                ['street', 'street', 'street']
            ],
            # Building entrance
            [
                ['building', 'building', 'building'],
                ['building', 'city_door', 'building'],
                ['street', 'street', 'street']
            ],
            # City intersection
            [
                ['street', 'street', 'street'],
                ['street', 'street', 'street'],
                ['street', 'street', 'street']
            ],
            # Market stall
            [
                ['building', 'building', 'building'],
                ['street', 'stall', 'street'],
                ['street', 'street', 'street']
            ],
            # Fountain square
            [
                ['plaza', 'plaza', 'plaza'],
                ['plaza', 'fountain', 'plaza'],
                ['plaza', 'plaza', 'plaza']
            ]
        ]
    
    def _get_crypt_patterns(self):
        """Crypt patterns - tombs, sarcophagi, burial chambers."""
        return [
            # Burial chamber
            [
                ['wall', 'wall', 'wall'],
                ['wall', 'sarcophagus', 'wall'],
                ['crypt_floor', 'crypt_floor', 'crypt_floor']
            ],
            # Crypt corridor
            [
                ['tomb_wall', 'tomb_wall', 'tomb_wall'],
                ['crypt_floor', 'crypt_floor', 'crypt_floor'],
                ['tomb_wall', 'tomb_wall', 'tomb_wall']
            ],
            # Ossuary wall
            [
                ['bones', 'bones', 'bones'],
                ['crypt_floor', 'crypt_floor', 'crypt_floor'],
                ['bones', 'bones', 'bones']
            ],
            # Tomb entrance
            [
                ['wall', 'crypt_door', 'wall'],
                ['crypt_floor', 'crypt_floor', 'crypt_floor'],
                ['wall', 'wall', 'wall']
            ],
            # Memorial hall
            [
                ['crypt_floor', 'crypt_floor', 'crypt_floor'],
                ['crypt_floor', 'memorial', 'crypt_floor'],
                ['crypt_floor', 'crypt_floor', 'crypt_floor']
            ],
            # Catacomb tunnel
            [
                ['bones', 'crypt_floor', 'bones'],
                ['bones', 'crypt_floor', 'bones'],
                ['bones', 'crypt_floor', 'bones']
            ]
        ]

class ThematicWFCGenerator:
    """Enhanced WFC generator with thematic pattern support."""
    
    def __init__(self):
        self.pattern_library = WFCPatternLibrary()
        self.current_theme = 'classic_dungeon'
        self.tile_types = {}
        self._init_thematic_tiles()
    
    def _init_thematic_tiles(self):
        """Initialize tile types for all themes."""
        from world.wfc_dungeon_generator import WFCTile
        
        self.tile_types = {
            # Basic tiles
            'wall': WFCTile('wall', '#', solid=True, weight=0.3),
            'floor': WFCTile('floor', '.', solid=False, weight=1.0),
            'door': WFCTile('door', '+', solid=False, weight=0.1),
            'corridor': WFCTile('corridor', '.', solid=False, weight=0.8),
            'room_floor': WFCTile('room_floor', '.', solid=False, weight=0.9),
            'pillar': WFCTile('pillar', 'O', solid=True, weight=0.05),
            'stairs_up': WFCTile('stairs_up', '<', solid=False, weight=0.01),
            'treasure': WFCTile('treasure', '$', solid=False, weight=0.02),
            'secret': WFCTile('secret', '.', solid=False, weight=0.005),
            
            # Cave tiles
            'cave_floor': WFCTile('cave_floor', '.', solid=False, weight=0.7),
            'water': WFCTile('water', '~', solid=True, weight=0.1),
            'stalactite': WFCTile('stalactite', 'i', solid=True, weight=0.02),
            
            # Temple tiles
            'temple_floor': WFCTile('temple_floor', '▒', solid=False, weight=0.8),
            'altar': WFCTile('altar', '♱', solid=True, weight=0.01),
            'sacred_pillar': WFCTile('sacred_pillar', '⌂', solid=True, weight=0.02),
            'temple_door': WFCTile('temple_door', '┼', solid=False, weight=0.05),
            'shrine': WFCTile('shrine', '☩', solid=True, weight=0.01),
            'mural': WFCTile('mural', '▓', solid=True, weight=0.1),
            
            # City tiles
            'building': WFCTile('building', '█', solid=True, weight=0.4),
            'street': WFCTile('street', '▓', solid=False, weight=0.6),
            'plaza': WFCTile('plaza', '░', solid=False, weight=0.2),
            'city_door': WFCTile('city_door', '╬', solid=False, weight=0.05),
            'stall': WFCTile('stall', '⌐', solid=True, weight=0.02),
            'fountain': WFCTile('fountain', '◊', solid=True, weight=0.01),
            
            # Crypt tiles
            'crypt_floor': WFCTile('crypt_floor', '░', solid=False, weight=0.7),
            'sarcophagus': WFCTile('sarcophagus', '▬', solid=True, weight=0.02),
            'tomb_wall': WFCTile('tomb_wall', '▓', solid=True, weight=0.3),
            'bones': WFCTile('bones', '☠', solid=True, weight=0.1),
            'crypt_door': WFCTile('crypt_door', '†', solid=False, weight=0.03),
            'memorial': WFCTile('memorial', '♰', solid=True, weight=0.01),
        }
    
    def generate_themed_dungeon(self, width, height, entrance_locations, theme='classic_dungeon'):
        """Generate a dungeon with a specific theme."""
        self.current_theme = theme
        print(f"Generating {theme} themed dungeon using WFC")
        
        # Get theme-specific patterns
        patterns = self.pattern_library.get_patterns(theme)
        
        # Create a specialized WFC generator for this theme
        from world.wfc_dungeon_generator import WFCDungeonGenerator, WFCPattern
        
        specialized_generator = WFCDungeonGenerator()
        specialized_generator.tile_types = self.tile_types
        
        # Convert patterns to WFCPattern objects
        specialized_generator.patterns = []
        for i, pattern_tiles in enumerate(patterns):
            pattern = WFCPattern(f"{theme}_pattern_{i}", pattern_tiles)
            specialized_generator.patterns.append(pattern)
            
            # Add rotations
            for rotated in pattern.get_all_rotations()[1:]:
                specialized_generator.patterns.append(rotated)
        
        # Rebuild adjacency rules for this theme
        specialized_generator._build_adjacency_rules()
        
        # Generate the dungeon
        result = specialized_generator.generate_dungeon(width, height, entrance_locations)
        
        # Theme-specific post-processing
        result = self._apply_theme_post_processing(result, theme)
        
        return result
    
    def _apply_theme_post_processing(self, dungeon_result, theme):
        """Apply theme-specific post-processing."""
        dungeon_map = dungeon_result['map']
        width = len(dungeon_map[0])
        height = len(dungeon_map)
        
        if theme == 'natural_caves':
            # Add more organic water features
            self._add_underground_streams(dungeon_map, width, height)
        
        elif theme == 'ancient_temple':
            # Add sacred areas and hidden chambers
            self._add_sacred_chambers(dungeon_map, width, height, dungeon_result)
        
        elif theme == 'underground_city':
            # Add city districts and main thoroughfares
            self._add_city_districts(dungeon_map, width, height)
        
        elif theme == 'crypts':
            # Add burial niches and ossuary sections
            self._add_burial_features(dungeon_map, width, height)
        
        return dungeon_result
    
    def _add_underground_streams(self, dungeon_map, width, height):
        """Add flowing water features to cave systems."""
        # Find existing water sources and extend them
        for y in range(height):
            for x in range(width):
                if dungeon_map[y][x] == 'water':
                    # Occasionally extend water in a direction
                    if random.random() < 0.3:
                        directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]
                        dx, dy = random.choice(directions)
                        for i in range(random.randint(2, 5)):
                            nx, ny = x + dx * i, y + dy * i
                            if (0 <= nx < width and 0 <= ny < height and
                                dungeon_map[ny][nx] in ['cave_floor', 'floor']):
                                dungeon_map[ny][nx] = 'water'
    
    def _add_sacred_chambers(self, dungeon_map, width, height, dungeon_result):
        """Add hidden sacred chambers to temples."""
        rooms = dungeon_result['rooms']
        
        # Add a few hidden chambers behind walls
        for _ in range(random.randint(1, 3)):
            if rooms:
                room = random.choice(rooms)
                # Try to place a hidden chamber adjacent to this room
                chamber_x = room.right + 2
                chamber_y = room.centery
                
                if chamber_x + 3 < width:
                    # Create small sacred chamber
                    for dx in range(3):
                        for dy in range(-1, 2):
                            cx, cy = chamber_x + dx, chamber_y + dy
                            if 0 <= cx < width and 0 <= cy < height:
                                if dx == 1 and dy == 0:
                                    dungeon_map[cy][cx] = 'altar'
                                else:
                                    dungeon_map[cy][cx] = 'temple_floor'
                    
                    # Add secret passage
                    dungeon_map[chamber_y][chamber_x - 1] = 'secret'
    
    def _add_city_districts(self, dungeon_map, width, height):
        """Add distinct districts to underground cities."""
        # Find large open areas and designate them as plazas
        for y in range(1, height - 1):
            for x in range(1, width - 1):
                if dungeon_map[y][x] == 'street':
                    # Check if this could be center of a plaza
                    plaza_size = 0
                    for dx in range(-2, 3):
                        for dy in range(-2, 3):
                            nx, ny = x + dx, y + dy
                            if (0 <= nx < width and 0 <= ny < height and
                                dungeon_map[ny][nx] in ['street', 'plaza']):
                                plaza_size += 1
                    
                    if plaza_size >= 15:  # Large open area
                        dungeon_map[y][x] = 'plaza'
    
    def _add_burial_features(self, dungeon_map, width, height):
        """Add burial niches and bone decorations to crypts."""
        # Add bone decorations to walls adjacent to crypt floors
        for y in range(height):
            for x in range(width):
                if dungeon_map[y][x] == 'wall':
                    # Check if adjacent to crypt floor
                    adjacent_to_crypt = False
                    for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
                        nx, ny = x + dx, y + dy
                        if (0 <= nx < width and 0 <= ny < height and
                            dungeon_map[ny][nx] in ['crypt_floor', 'floor']):
                            adjacent_to_crypt = True
                            break
                    
                    if adjacent_to_crypt and random.random() < 0.2:
                        dungeon_map[y][x] = 'bones'

# Example usage patterns for different themes
THEME_EXAMPLES = {
    'classic_dungeon': "Traditional stone corridors and chambers",
    'natural_caves': "Organic caverns with underground streams", 
    'ancient_temple': "Sacred halls with altars and murals",
    'underground_city': "Streets, plazas, and building districts",
    'crypts': "Burial chambers with sarcophagi and bone walls"
}