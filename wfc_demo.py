# wfc_demo.py
"""
Demo script to test and visualize different WFC dungeon themes.
"""

def demo_wfc_dungeons():
    """Generate and display sample dungeons for each theme."""
    import sys
    import os
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    
    from world.dungeon_generator import DungeonGenerator
    
    print("=== Wave Function Collapse Dungeon Generation Demo ===\n")
    
    # Initialize generator
    dungeon_gen = DungeonGenerator()
    dungeon_gen.set_generation_options(use_wfc=True, use_themes=True)
    
    # Test parameters
    width, height = 40, 30
    entrance_locations = [(5, 5), (35, 25)]
    
    # Available themes
    themes = [
        'classic_dungeon',
        'natural_caves', 
        'ancient_temple',
        'underground_city',
        'crypts'
    ]
    
    # Get theme descriptions
    theme_info = dungeon_gen.get_theme_info()
    
    print("Available Themes:")
    for theme in themes:
        description = theme_info.get(theme, "No description available")
        print(f"  {theme}: {description}")
    print()
    
    # Generate a sample dungeon for each theme
    for theme in themes:
        print(f"=== Generating {theme.upper().replace('_', ' ')} ===")
        
        try:
            result = dungeon_gen.generate_themed_dungeon(
                width, height, entrance_locations, theme)
            
            dungeon_map = result['map']
            rooms = result['rooms']
            treasure_chests = result['treasure_chests']
            entrance_stairs = result['entrance_stairs']
            
            print(f"Generated:")
            print(f"  - {len(rooms)} rooms")
            print(f"  - {len(treasure_chests)} treasure chests") 
            print(f"  - {len(entrance_stairs)} entrance stairs")
            
            # Show a small sample of the map
            print(f"\nSample map section (top-left 20x15):")
            sample_map = visualize_dungeon_sample(dungeon_map, 20, 15)
            print(sample_map)
            
            # Show room descriptions
            if result['room_data']:
                sample_room = result['room_data'][0]
                print(f"Sample room description: \"{sample_room[1]}\"")
            
        except Exception as e:
            print(f"Error generating {theme}: {e}")
        
        print("-" * 50)
        print()

def visualize_dungeon_sample(dungeon_map, max_width, max_height):
    """Create a visual representation of a dungeon map sample."""
    
    # Character mapping for different tile types
    char_map = {
        'dungeon_wall': '#',
        'dungeon_floor': '.',
        'treasure_chest': '$',
        'stairs_up': '<',
        'stairs_down': '>',
        'water': '~',
        'altar': '♱',
        'sacred_pillar': '⌂',
        'temple_floor': '▒',
        'temple_door': '┼',
        'shrine': '☩',
        'mural': '▓',
        'building': '█',
        'street': '▓',
        'plaza': '░',
        'city_door': '╬',
        'stall': '⌐',
        'fountain': '◊',
        'crypt_floor': '░',
        'sarcophagus': '▬',
        'tomb_wall': '▓',
        'bones': '☠',
        'crypt_door': '†',
        'memorial': '♰',
        'cave_floor': '.',
        'stalactite': 'i',
        'pillar': 'O',
        'secret': '?',
    }
    
    lines = []
    height = min(max_height, len(dungeon_map))
    
    for y in range(height):
        line = ""
        width = min(max_width, len(dungeon_map[y]))
        for x in range(width):
            tile_type = dungeon_map[y][x]
            char = char_map.get(tile_type, '?')
            line += char
        lines.append(f"  {line}")
    
    return "\n".join(lines)

def compare_generation_methods():
    """Compare classic vs WFC generation."""
    import sys
    import os
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    
    from world.dungeon_generator import DungeonGenerator
    
    print("=== Generation Method Comparison ===\n")
    
    dungeon_gen = DungeonGenerator()
    width, height = 30, 20
    entrance_locations = [(5, 5)]
    
    # Test classic generation
    print("CLASSIC GENERATION:")
    dungeon_gen.set_generation_options(use_wfc=False, use_themes=False)
    classic_result = dungeon_gen.generate_dungeon(width, height, entrance_locations)
    
    print(f"  Rooms: {len(classic_result['rooms'])}")
    print(f"  Treasures: {len(classic_result['treasure_chests'])}")
    print("  Sample:")
    print(visualize_dungeon_sample(classic_result['map'], 25, 15))
    print()
    
    # Test WFC generation
    print("WAVE FUNCTION COLLAPSE:")
    dungeon_gen.set_generation_options(use_wfc=True, use_themes=False)
    wfc_result = dungeon_gen.generate_dungeon(width, height, entrance_locations)
    
    print(f"  Rooms: {len(wfc_result['rooms'])}")
    print(f"  Treasures: {len(wfc_result['treasure_chests'])}")
    print("  Sample:")
    print(visualize_dungeon_sample(wfc_result['map'], 25, 15))
    print()
    
    # Test themed WFC
    print("THEMED WFC (Ancient Temple):")
    dungeon_gen.set_generation_options(use_wfc=True, use_themes=True)
    themed_result = dungeon_gen.generate_themed_dungeon(
        width, height, entrance_locations, 'ancient_temple')
    
    print(f"  Rooms: {len(themed_result['rooms'])}")
    print(f"  Treasures: {len(themed_result['treasure_chests'])}")
    print("  Sample:")
    print(visualize_dungeon_sample(themed_result['map'], 25, 15))

if __name__ == '__main__':
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == 'compare':
        compare_generation_methods()
    else:
        demo_wfc_dungeons()
        
    print("\n=== Demo Complete ===")
    print("Run 'python wfc_demo.py compare' to see generation method comparison")