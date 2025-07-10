# world/building_generator.py
"""
Building interior generation system.
"""
import random

class BuildingGenerator:
    """Generates building interiors and layouts."""
    
    def generate_building(self, building_type, exterior_pos, exterior_size):
        """Generate a complete building with interior layout."""
        building = {
            'building_type': building_type,
            'exterior_pos': exterior_pos,
            'exterior_size': exterior_size,
            'interior_map': None,
            'interior_size': None,
            'doors': [],
            'windows': [],
            'interior_objects': [],
            'entrance_points': []
        }
        
        # Generate interior based on building type
        if building_type == 'house':
            self._generate_house_interior(building)
        elif building_type == 'tavern':
            self._generate_tavern_interior(building)
        elif building_type == 'forge':
            self._generate_forge_interior(building)
        elif building_type == 'tower':
            self._generate_tower_interior(building)
        elif building_type == 'castle':
            self._generate_castle_interior(building)
        else:
            # Default simple interior
            self._generate_simple_interior(building)
        
        return building
    
    def _generate_house_interior(self, building):
        """Generate a house interior layout."""
        # Interior is typically larger than exterior
        exterior_w, exterior_h = building['exterior_size']
        interior_w = exterior_w + 2  # 5x5 interior for 3x3 exterior
        interior_h = exterior_h + 2
        
        building['interior_size'] = (interior_w, interior_h)
        
        # Create interior map
        interior = [['wall' for _ in range(interior_w)] for _ in range(interior_h)]
        
        # Create floor area
        for x in range(1, interior_w - 1):
            for y in range(1, interior_h - 1):
                interior[y][x] = 'floor'
        
        # Add door
        door_x = interior_w // 2
        door_y = interior_h - 1
        interior[door_y][door_x] = 'door'
        building['doors'].append((door_x, door_y, 'south'))
        building['entrance_points'].append((door_x, door_y - 1))  # Inside position
        
        # Add furniture
        # Bed in corner
        interior[1][interior_w - 2] = 'bed'
        
        # Table in center
        interior[interior_h // 2][interior_w // 2] = 'table'
        
        # Chair near table
        interior[interior_h // 2 + 1][interior_w // 2] = 'chair'
        
        # Add windows
        if interior_w >= 4:
            interior[1][1] = 'window'  # North window
            building['windows'].append((1, 1))
        
        building['interior_map'] = interior
    
    def _generate_tavern_interior(self, building):
        """Generate a tavern interior layout."""
        exterior_w, exterior_h = building['exterior_size']
        interior_w = exterior_w + 3  # 7x7 interior for 4x4 exterior
        interior_h = exterior_h + 3
        
        building['interior_size'] = (interior_w, interior_h)
        
        # Create interior map
        interior = [['wall' for _ in range(interior_w)] for _ in range(interior_h)]
        
        # Create floor area
        for x in range(1, interior_w - 1):
            for y in range(1, interior_h - 1):
                interior[y][x] = 'floor'
        
        # Add door
        door_x = interior_w // 2
        door_y = interior_h - 1
        interior[door_y][door_x] = 'door'
        building['doors'].append((door_x, door_y, 'south'))
        building['entrance_points'].append((door_x, door_y - 1))
        
        # Add tavern furniture
        # Counter along one wall
        for x in range(2, interior_w - 2):
            interior[2][x] = 'counter'
        
        # Tables and chairs
        table_positions = [(2, 4), (interior_w - 3, 4), (2, interior_h - 3), (interior_w - 3, interior_h - 3)]
        for tx, ty in table_positions:
            if 1 <= tx < interior_w - 1 and 1 <= ty < interior_h - 1:
                interior[ty][tx] = 'table'
                # Add chairs around tables
                for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
                    cx, cy = tx + dx, ty + dy
                    if (1 <= cx < interior_w - 1 and 1 <= cy < interior_h - 1 and 
                        interior[cy][cx] == 'floor'):
                        interior[cy][cx] = 'chair'
        
        building['interior_map'] = interior
    
    def _generate_forge_interior(self, building):
        """Generate a forge interior layout."""
        exterior_w, exterior_h = building['exterior_size']
        interior_w = exterior_w + 3  # 6x7 interior for 3x4 exterior
        interior_h = exterior_h + 3
        
        building['interior_size'] = (interior_w, interior_h)
        
        # Create interior map
        interior = [['wall' for _ in range(interior_w)] for _ in range(interior_h)]
        
        # Create floor area
        for x in range(1, interior_w - 1):
            for y in range(1, interior_h - 1):
                interior[y][x] = 'floor'
        
        # Add door
        door_x = interior_w // 2
        door_y = interior_h - 1
        interior[door_y][door_x] = 'door'
        building['doors'].append((door_x, door_y, 'south'))
        building['entrance_points'].append((door_x, door_y - 1))
        
        # Add forge equipment
        # Forge/furnace along north wall
        for x in range(2, interior_w - 2):
            interior[1][x] = 'forge'
        
        # Anvils
        interior[3][2] = 'anvil'
        interior[3][interior_w - 3] = 'anvil'
        
        # Storage along walls
        for y in range(interior_h - 3, interior_h - 1):
            interior[y][1] = 'storage'
            interior[y][interior_w - 2] = 'storage'
        
        building['interior_map'] = interior
    
    def _generate_tower_interior(self, building):
        """Generate a tower interior (placeholder - multi-level)."""
        exterior_w, exterior_h = building['exterior_size']
        interior_w = exterior_w + 2
        interior_h = exterior_h + 2
        
        building['interior_size'] = (interior_w, interior_h)
        
        # Create interior map (ground floor for now)
        interior = [['wall' for _ in range(interior_w)] for _ in range(interior_h)]
        
        # Create floor area
        for x in range(1, interior_w - 1):
            for y in range(1, interior_h - 1):
                interior[y][x] = 'floor'
        
        # Add door
        door_x = interior_w // 2
        door_y = interior_h - 1
        interior[door_y][door_x] = 'door'
        building['doors'].append((door_x, door_y, 'south'))
        building['entrance_points'].append((door_x, door_y - 1))
        
        # Add stairs to upper levels (placeholder)
        interior[1][1] = 'stairs_up'
        
        # Add some basic furniture
        interior[interior_h // 2][interior_w // 2] = 'table'
        
        building['interior_map'] = interior
    
    def _generate_castle_interior(self, building):
        """Generate a castle interior (placeholder - complex multi-room)."""
        exterior_w, exterior_h = building['exterior_size']
        interior_w = exterior_w + 4  # Much larger interior
        interior_h = exterior_h + 4
        
        building['interior_size'] = (interior_w, interior_h)
        
        # Create interior map
        interior = [['wall' for _ in range(interior_w)] for _ in range(interior_h)]
        
        # Create main hall
        for x in range(2, interior_w - 2):
            for y in range(2, interior_h - 2):
                interior[y][x] = 'floor'
        
        # Add main entrance
        door_x = interior_w // 2
        door_y = interior_h - 1
        interior[door_y][door_x] = 'door'
        building['doors'].append((door_x, door_y, 'south'))
        building['entrance_points'].append((door_x, door_y - 1))
        
        # Add throne at far end
        interior[2][interior_w // 2] = 'throne'
        
        # Add pillars
        if interior_w >= 8 and interior_h >= 8:
            interior[4][3] = 'pillar'
            interior[4][interior_w - 4] = 'pillar'
            interior[interior_h - 5][3] = 'pillar'
            interior[interior_h - 5][interior_w - 4] = 'pillar'
        
        # Add side rooms (placeholder)
        for x in range(1, 3):
            for y in range(1, 4):
                interior[y][x] = 'floor'
        interior[2][1] = 'door'
        building['doors'].append((1, 2, 'west'))
        
        building['interior_map'] = interior
    
    def _generate_simple_interior(self, building):
        """Generate a simple default interior."""
        exterior_w, exterior_h = building['exterior_size']
        interior_w = exterior_w + 2
        interior_h = exterior_h + 2
        
        building['interior_size'] = (interior_w, interior_h)
        
        # Create interior map
        interior = [['wall' for _ in range(interior_w)] for _ in range(interior_h)]
        
        # Create floor area
        for x in range(1, interior_w - 1):
            for y in range(1, interior_h - 1):
                interior[y][x] = 'floor'
        
        # Add door
        door_x = interior_w // 2
        door_y = interior_h - 1
        interior[door_y][door_x] = 'door'
        building['doors'].append((door_x, door_y, 'south'))
        building['entrance_points'].append((door_x, door_y - 1))
        
        building['interior_map'] = interior