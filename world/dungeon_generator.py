# world/dungeon_generator.py
"""
Enhanced dungeon generation system with Wave Function Collapse and thematic options.
"""
import random
import pygame
from entities.items import create_random_item
from world.wfc_dungeon_generator import WFCDungeonGenerator
from world.wfc_pattern_library import ThematicWFCGenerator

class DungeonGenerator:
    """Enhanced dungeon generator with multiple generation methods and themes."""
    
    def __init__(self):
        self.wfc_generator = WFCDungeonGenerator()
        self.thematic_generator = ThematicWFCGenerator()
        self.use_wfc = True  # Set to True to use WFC, False for classic
        self.use_themes = True  # Set to True for thematic dungeons
        
        # Available dungeon themes
        self.available_themes = [
            'classic_dungeon',
            'natural_caves', 
            'ancient_temple',
            'underground_city',
            'crypts'
        ]
    
    def generate_dungeon(self, width, height, entrance_locations, max_rooms=30, 
                        min_room_size=5, max_room_size=12):
        """Generate a complete dungeon system using the chosen method."""
        
        if self.use_wfc:
            if self.use_themes:
                # Choose a random theme for variety
                theme = random.choice(self.available_themes)
                print(f"Using Thematic WFC generation: {theme}")
                return self.thematic_generator.generate_themed_dungeon(
                    width, height, entrance_locations, theme)
            else:
                print("Using standard Wave Function Collapse dungeon generation")
                return self.wfc_generator.generate_dungeon(width, height, entrance_locations)
        else:
            print("Using classic dungeon generation")
            return self._generate_classic_dungeon(width, height, entrance_locations, 
                                                max_rooms, min_room_size, max_room_size)
    
    def generate_themed_dungeon(self, width, height, entrance_locations, theme):
        """Generate a dungeon with a specific theme."""
        if self.use_wfc and self.use_themes:
            return self.thematic_generator.generate_themed_dungeon(
                width, height, entrance_locations, theme)
        else:
            # Fallback to classic with theme-appropriate descriptions
            result = self._generate_classic_dungeon(width, height, entrance_locations)
            result = self._apply_theme_to_classic(result, theme)
            return result
    
    def _apply_theme_to_classic(self, dungeon_result, theme):
        """Apply thematic descriptions to classic dungeons."""
        theme_descriptions = {
            'natural_caves': [
                "Water drips from limestone formations above.",
                "The cavern walls glisten with mineral deposits.",
                "Strange rock formations create eerie shadows.",
                "You hear the distant sound of flowing water.",
                "Stalactites hang like ancient teeth from the ceiling.",
                "The air is cool and damp with cave moisture."
            ],
            'ancient_temple': [
                "Sacred symbols are carved into every surface.",
                "Ancient murals depict long-forgotten rituals.",
                "The air hums with residual divine energy.",
                "Ceremonial braziers stand cold and empty.",
                "Holy texts in dead languages cover the walls.",
                "This chamber once echoed with sacred chants."
            ],
            'underground_city': [
                "Abandoned market stalls line the thoroughfare.",
                "Street lamps stand dark and forgotten.",
                "The remnants of a once-thriving community.",
                "Building facades show signs of hasty evacuation.",
                "A central plaza opens before you.",
                "The architecture speaks of better times."
            ],
            'crypts': [
                "Burial niches line the walls like silent sentries.",
                "The musty scent of ages-old incense lingers.",
                "Carved epitaphs tell stories of the departed.",
                "Funeral urns rest undisturbed on stone shelves.",
                "The weight of countless souls presses down.",
                "Bone fragments crunch softly underfoot."
            ]
        }
        
        descriptions = theme_descriptions.get(theme, [
            "Dust and decay fill this ancient chamber.",
            "Strange scratching noises echo from the walls.",
            "The air is thick with the scent of ages past."
        ])
        
        # Update room descriptions
        new_room_data = []
        for room, _ in dungeon_result['room_data']:
            new_room_data.append((room, random.choice(descriptions)))
        
        dungeon_result['room_data'] = new_room_data
        return dungeon_result
    
    def _generate_classic_dungeon(self, width, height, entrance_locations, max_rooms, 
                                 min_room_size, max_room_size):
        """Generate a dungeon using the classic room+corridor method."""
        dungeon_map = [['dungeon_wall' for _ in range(width)] for _ in range(height)]
        rooms = []
        room_data = []
        treasure_chests = []
        entrance_stairs = []
        
        # Generate rooms
        for _ in range(max_rooms):
            w = random.randint(min_room_size, max_room_size)
            h = random.randint(min_room_size, max_room_size)
            x = random.randint(1, width - w - 2)
            y = random.randint(1, height - h - 2)
            new_room = pygame.Rect(x, y, w, h)
            
            # Check for room overlap
            if any(new_room.colliderect(other) for other in rooms):
                continue
            
            # Create room floor
            for i in range(new_room.left, new_room.right):
                for j in range(new_room.top, new_room.bottom):
                    dungeon_map[j][i] = 'dungeon_floor'
            
            # Connect to previous room with tunnel
            if rooms:
                self._create_tunnel(dungeon_map, 
                                   rooms[-1].centerx, rooms[-1].centery,
                                   new_room.centerx, new_room.centery)
            
            rooms.append(new_room)
            
            # Add room description
            descriptions = [
                "Dust and decay fill this ancient chamber.",
                "Strange scratching noises echo from the walls.",
                "Phosphorescent moss provides an eerie glow.",
                "Water drips steadily from the cracked ceiling.",
                "Crude symbols are carved into the stone walls.",
                "This chamber feels unnaturally cold.",
                "The air is thick with the smell of rot.",
                "Cobwebs hang like curtains in the corners."
            ]
            room_data.append((new_room, random.choice(descriptions)))
        
        # Add treasure chests to some rooms
        for room in rooms:
            if random.random() < 0.25:  # 25% chance for treasure
                chest_x = random.randint(room.left + 1, room.right - 2)
                chest_y = random.randint(room.top + 1, room.bottom - 2)
                if dungeon_map[chest_y][chest_x] == 'dungeon_floor':
                    dungeon_map[chest_y][chest_x] = 'treasure_chest'
                    treasure_chests.append({
                        'pos': (chest_x, chest_y),
                        'item': create_random_item()
                    })
        
        # Add entrance stairs
        for i, entrance_pos in enumerate(entrance_locations):
            if i < len(rooms):
                # Place stairs in room centers
                stairs_x = rooms[i].centerx
                stairs_y = rooms[i].centery
                dungeon_map[stairs_y][stairs_x] = 'stairs_up'
                entrance_stairs.append({
                    'dungeon_pos': (stairs_x, stairs_y),
                    'overworld_pos': entrance_pos
                })
        
        return {
            'map': dungeon_map,
            'rooms': rooms,
            'room_data': room_data,
            'treasure_chests': treasure_chests,
            'entrance_stairs': entrance_stairs
        }
    
    def _create_tunnel(self, dungeon_map, x1, y1, x2, y2):
        """Create a tunnel between two points."""
        if random.random() < 0.5:
            # Horizontal then vertical
            for x in range(min(x1, x2), max(x1, x2) + 1):
                dungeon_map[y1][x] = 'dungeon_floor'
            for y in range(min(y1, y2), max(y1, y2) + 1):
                dungeon_map[y][x2] = 'dungeon_floor'
        else:
            # Vertical then horizontal
            for y in range(min(y1, y2), max(y1, y2) + 1):
                dungeon_map[y][x1] = 'dungeon_floor'
            for x in range(min(x1, x2), max(x1, x2) + 1):
                dungeon_map[y2][x] = 'dungeon_floor'
    
    def get_theme_info(self):
        """Get information about available themes."""
        from world.wfc_pattern_library import THEME_EXAMPLES
        return THEME_EXAMPLES
    
    def set_generation_options(self, use_wfc=True, use_themes=True):
        """Configure generation options."""
        self.use_wfc = use_wfc
        self.use_themes = use_themes
        print(f"Dungeon generation configured: WFC={use_wfc}, Themes={use_themes}")wall' for _ in range(width)] for _ in range(height)]
        rooms = []
        room_data = []
        treasure_chests = []
        entrance_stairs = []
        
        # Generate rooms
        for _ in range(max_rooms):
            w = random.randint(min_room_size, max_room_size)
            h = random.randint(min_room_size, max_room_size)
            x = random.randint(1, width - w - 2)
            y = random.randint(1, height - h - 2)
            new_room = pygame.Rect(x, y, w, h)
            
            # Check for room overlap
            if any(new_room.colliderect(other) for other in rooms):
                continue
            
            # Create room floor
            for i in range(new_room.left, new_room.right):
                for j in range(new_room.top, new_room.bottom):
                    dungeon_map[j][i] = 'dungeon_floor'
            
            # Connect to previous room with tunnel
            if rooms:
                self._create_tunnel(dungeon_map, 
                                   rooms[-1].centerx, rooms[-1].centery,
                                   new_room.centerx, new_room.centery)
            
            rooms.append(new_room)
            
            # Add room description
            descriptions = [
                "Dust and decay fill this ancient chamber.",
                "Strange scratching noises echo from the walls.",
                "Phosphorescent moss provides an eerie glow.",
                "Water drips steadily from the cracked ceiling.",
                "Crude symbols are carved into the stone walls.",
                "This chamber feels unnaturally cold.",
                "The air is thick with the smell of rot.",
                "Cobwebs hang like curtains in the corners."
            ]
            room_data.append((new_room, random.choice(descriptions)))
        
        # Add treasure chests to some rooms
        for room in rooms:
            if random.random() < 0.25:  # 25% chance for treasure
                chest_x = random.randint(room.left + 1, room.right - 2)
                chest_y = random.randint(room.top + 1, room.bottom - 2)
                if dungeon_map[chest_y][chest_x] == 'dungeon_floor':
                    dungeon_map[chest_y][chest_x] = 'treasure_chest'
                    treasure_chests.append({
                        'pos': (chest_x, chest_y),
                        'item': create_random_item()
                    })
        
        # Add entrance stairs
        for i, entrance_pos in enumerate(entrance_locations):
            if i < len(rooms):
                # Place stairs in room centers
                stairs_x = rooms[i].centerx
                stairs_y = rooms[i].centery
                dungeon_map[stairs_y][stairs_x] = 'stairs_up'
                entrance_stairs.append({
                    'dungeon_pos': (stairs_x, stairs_y),
                    'overworld_pos': entrance_pos
                })
        
        return {
            'map': dungeon_map,
            'rooms': rooms,
            'room_data': room_data,
            'treasure_chests': treasure_chests,
            'entrance_stairs': entrance_stairs
        }
    
    def _create_tunnel(self, dungeon_map, x1, y1, x2, y2):
        """Create a tunnel between two points."""
        if random.random() < 0.5:
            # Horizontal then vertical
            for x in range(min(x1, x2), max(x1, x2) + 1):
                dungeon_map[y1][x] = 'dungeon_floor'
            for y in range(min(y1, y2), max(y1, y2) + 1):
                dungeon_map[y][x2] = 'dungeon_floor'
        else:
            # Vertical then horizontal
            for y in range(min(y1, y2), max(y1, y2) + 1):
                dungeon_map[y][x1] = 'dungeon_floor'
            for x in range(min(x1, x2), max(x1, x2) + 1):
                dungeon_map[y2][x] = 'dungeon_floor'
    
    def get_theme_info(self):
        """Get information about available themes."""
        from world.wfc_pattern_library import THEME_EXAMPLES
        return THEME_EXAMPLES
    
    def set_generation_options(self, use_wfc=True, use_themes=True):
        """Configure generation options."""
        self.use_wfc = use_wfc
        self.use_themes = use_themes
        print(f"Dungeon generation configured: WFC={use_wfc}, Themes={use_themes}")wall' for _ in range(width)] for _ in range(height)]
        rooms = []
        room_data = []
        treasure_chests = []
        entrance_stairs = []
        
        # Generate rooms
        for _ in range(max_rooms):
            w = random.randint(min_room_size, max_room_size)
            h = random.randint(min_room_size, max_room_size)
            x = random.randint(1, width - w - 2)
            y = random.randint(1, height - h - 2)
            new_room = pygame.Rect(x, y, w, h)
            
            # Check for room overlap
            if any(new_room.colliderect(other) for other in rooms):
                continue
            
            # Create room floor
            for i in range(new_room.left, new_room.right):
                for j in range(new_room.top, new_room.bottom):
                    dungeon_map[j][i] = 'dungeon_floor'
            
            # Connect to previous room with tunnel
            if rooms:
                self._create_tunnel(dungeon_map, 
                                   rooms[-1].centerx, rooms[-1].centery,
                                   new_room.centerx, new_room.centery)
            
            rooms.append(new_room)
            
            # Add room description
            descriptions = [
                "Dust and decay fill this ancient chamber.",
                "Strange scratching noises echo from the walls.",
                "Phosphorescent moss provides an eerie glow.",
                "Water drips steadily from the cracked ceiling.",
                "Crude symbols are carved into the stone walls.",
                "This chamber feels unnaturally cold.",
                "The air is thick with the smell of rot.",
                "Cobwebs hang like curtains in the corners."
            ]
            room_data.append((new_room, random.choice(descriptions)))
        
        # Add treasure chests to some rooms
        for room in rooms:
            if random.random() < 0.25:  # 25% chance for treasure
                chest_x = random.randint(room.left + 1, room.right - 2)
                chest_y = random.randint(room.top + 1, room.bottom - 2)
                if dungeon_map[chest_y][chest_x] == 'dungeon_floor':
                    dungeon_map[chest_y][chest_x] = 'treasure_chest'
                    treasure_chests.append({
                        'pos': (chest_x, chest_y),
                        'item': create_random_item()
                    })
        
        # Add entrance stairs
        for i, entrance_pos in enumerate(entrance_locations):
            if i < len(rooms):
                # Place stairs in room centers
                stairs_x = rooms[i].centerx
                stairs_y = rooms[i].centery
                dungeon_map[stairs_y][stairs_x] = 'stairs_up'
                entrance_stairs.append({
                    'dungeon_pos': (stairs_x, stairs_y),
                    'overworld_pos': entrance_pos
                })
        
        return {
            'map': dungeon_map,
            'rooms': rooms,
            'room_data': room_data,
            'treasure_chests': treasure_chests,
            'entrance_stairs': entrance_stairs
        }
    
    def _create_tunnel(self, dungeon_map, x1, y1, x2, y2):
        """Create a tunnel between two points."""
        if random.random() < 0.5:
            # Horizontal then vertical
            for x in range(min(x1, x2), max(x1, x2) + 1):
                dungeon_map[y1][x] = 'dungeon_floor'
            for y in range(min(y1, y2), max(y1, y2) + 1):
                dungeon_map[y][x2] = 'dungeon_floor'
        else:
            # Vertical then horizontal
            for y in range(min(y1, y2), max(y1, y2) + 1):
                dungeon_map[y][x1] = 'dungeon_floor'
            for x in range(min(x1, x2), max(x1, x2) + 1):
                dungeon_map[y2][x] = 'dungeon_floor'