# world/location_manager.py (Fixed version)
"""
Fixed location management system with proper dungeon entrance handling.
"""

class LocationManager:
    """Manages player location transitions between overworld, buildings, and dungeons."""
    
    def __init__(self):
        self.current_location = 'overworld'
        self.previous_location = None
        self.location_stack = []  # For nested locations (e.g., tower floors)
        
        # Location-specific managers
        self.building_manager = None
        self.dungeon_manager = None
        
        # Transition data
        self.entrance_used = None
        self.saved_positions = {}  # Save positions when transitioning
    
    def set_managers(self, building_manager, dungeon_manager=None):
        """Set the managers for different location types."""
        self.building_manager = building_manager
        self.dungeon_manager = dungeon_manager
    
    def can_transition(self, player, terrain_map):
        """Check if player can transition to a different location."""
        x, y = player.x, player.y
        
        if self.current_location == 'overworld':
            # Check for building entrance
            if self.building_manager and self.building_manager.can_enter_building(x, y, terrain_map):
                return 'building'
            
            # Check for dungeon entrance
            if (terrain_map and 0 <= y < len(terrain_map) and 0 <= x < len(terrain_map[0]) and
                terrain_map[y][x] == 'dungeon_entrance'):
                return 'dungeon'
        
        elif self.current_location == 'building_interior':
            # Check for building exit
            if self.building_manager and self.building_manager.current_building:
                interior_map = self.building_manager.current_building['interior_map']
                if (0 <= y < len(interior_map) and 0 <= x < len(interior_map[0]) and
                    interior_map[y][x] == 'door'):
                    return 'overworld'
        
        elif self.current_location == 'dungeon':
            # Check for dungeon exit
            if (terrain_map and 0 <= y < len(terrain_map) and 0 <= x < len(terrain_map[0]) and
                terrain_map[y][x] == 'stairs_up'):
                return 'overworld'
        
        return None
    
    def transition_to_location(self, transition_type, player, terrain_map=None):
        """Handle transition to a new location."""
        print(f"Transitioning from {self.current_location} to {transition_type}")
        self.previous_location = self.current_location
        
        if transition_type == 'building':
            return self._enter_building(player, terrain_map)
        elif transition_type == 'overworld':
            return self._exit_to_overworld(player)
        elif transition_type == 'dungeon':
            return self._enter_dungeon(player, terrain_map)
        elif transition_type == 'dungeon_exit':
            return self._exit_dungeon(player)
        
        return False
    
    def _enter_building(self, player, terrain_map):
        """Enter a building from overworld."""
        if not self.building_manager:
            print("No building manager available")
            return False
        
        # Save overworld position
        self.saved_positions['overworld'] = (player.x, player.y)
        print(f"Saved overworld position: {self.saved_positions['overworld']}")
        
        # Find and enter building
        building = self.building_manager.get_building_at_position(player.x, player.y)
        if building:
            print(f"Entering building: {building['building_type']}")
            if self.building_manager.enter_building(building, player):
                self.current_location = 'building_interior'
                print(f"Successfully entered building. New location: {self.current_location}")
                return True
        else:
            print("No building found at position")
        
        return False
    
    def _exit_to_overworld(self, player):
        """Exit current location and return to overworld."""
        print(f"Exiting from {self.current_location} to overworld")
        
        if self.current_location == 'building_interior':
            if self.building_manager:
                if self.building_manager.exit_building(player):
                    self.current_location = 'overworld'
                    print(f"Successfully exited building. New location: {self.current_location}")
                    return True
        
        elif self.current_location == 'dungeon':
            # Restore overworld position
            if 'overworld' in self.saved_positions:
                player.x, player.y = self.saved_positions['overworld']
                player.location = 'overworld'
                self.current_location = 'overworld'
                print(f"Restored to overworld position: {player.x}, {player.y}")
                return True
        
        return False
    
    def _enter_dungeon(self, player, terrain_map):
        """Enter a dungeon from overworld with proper positioning."""
        print(f"Entering dungeon from position {player.x}, {player.y}")
        
        # Save overworld position
        self.saved_positions['overworld'] = (player.x, player.y)
        print(f"Saved overworld position: {self.saved_positions['overworld']}")
        
        # Find a safe starting position in the dungeon
        # Look for the first room and place player on a floor tile
        safe_x, safe_y = self._find_safe_dungeon_position(terrain_map)
        
        player.x = safe_x
        player.y = safe_y
        player.location = 'dungeon'
        self.current_location = 'dungeon'
        print(f"Entered dungeon at safe position {player.x}, {player.y}")
        return True
    
    def _find_safe_dungeon_position(self, dungeon_map):
        """Find a safe floor position in the dungeon."""
        # Look for the first floor tile we can find
        for y in range(len(dungeon_map)):
            for x in range(len(dungeon_map[0])):
                if dungeon_map[y][x] == 'dungeon_floor':
                    print(f"Found safe dungeon position at {x}, {y}")
                    return (x, y)
        
        # Fallback: find any non-wall position
        for y in range(len(dungeon_map)):
            for x in range(len(dungeon_map[0])):
                if dungeon_map[y][x] != 'dungeon_wall':
                    print(f"Found fallback dungeon position at {x}, {y}")
                    return (x, y)
        
        # Ultimate fallback
        print("Using ultimate fallback position (50, 50)")
        return (50, 50)
    
    def _exit_dungeon(self, player):
        """Exit dungeon and return to overworld."""
        return self._exit_to_overworld(player)
    
    def get_current_map_info(self, player, overworld_map, dungeon_map):
        """Get current map information for rendering."""
        if self.current_location == 'overworld':
            return {
                'type': 'overworld',
                'map': overworld_map,
                'width': len(overworld_map[0]) if overworld_map else 0,
                'height': len(overworld_map) if overworld_map else 0
            }
        
        elif self.current_location == 'building_interior':
            if self.building_manager:
                return self.building_manager.get_current_map_info(player)
        
        elif self.current_location == 'dungeon':
            return {
                'type': 'dungeon',
                'map': dungeon_map,
                'width': len(dungeon_map[0]) if dungeon_map else 0,
                'height': len(dungeon_map) if dungeon_map else 0
            }
        
        return None
    
    def get_tile_render_info(self, x, y, player, overworld_map, dungeon_map):
        """Get tile rendering info for current location."""
        if self.current_location == 'overworld':
            # Use existing world tile rendering
            return None  # Let world handle this
        
        elif self.current_location == 'building_interior':
            if self.building_manager and self.building_manager.current_building:
                interior_map = self.building_manager.current_building['interior_map']
                if 0 <= y < len(interior_map) and 0 <= x < len(interior_map[0]):
                    tile_type = interior_map[y][x]
                    return self.building_manager.get_tile_render_info(x, y, tile_type)
        
        elif self.current_location == 'dungeon':
            # Use existing dungeon tile rendering
            return None  # Let world handle this
        
        return None
    
    def is_solid(self, x, y, player, overworld_map, dungeon_map):
        """Check if tile is solid in current location."""
        if self.current_location == 'overworld':
            return False  # Let world handle this
        
        elif self.current_location == 'building_interior':
            if self.building_manager and self.building_manager.current_building:
                interior_map = self.building_manager.current_building['interior_map']
                return self.building_manager.is_solid(x, y, interior_map)
        
        elif self.current_location == 'dungeon':
            return False  # Let world handle this
        
        return True
    
    def get_action_prompt(self, x, y, player, overworld_map, dungeon_map):
        """Get action prompt for current location."""
        if self.current_location == 'overworld':
            return ""  # Let world handle this
        
        elif self.current_location == 'building_interior':
            if self.building_manager and self.building_manager.current_building:
                interior_map = self.building_manager.current_building['interior_map']
                return self.building_manager.get_action_prompt(x, y, interior_map)
        
        elif self.current_location == 'dungeon':
            return ""  # Let world handle this
        
        return ""
    
    def get_description(self, x, y, player, overworld_map, dungeon_map):
        """Get tile description for current location."""
        if self.current_location == 'overworld':
            return ""  # Let world handle this
        
        elif self.current_location == 'building_interior':
            if self.building_manager and self.building_manager.current_building:
                interior_map = self.building_manager.current_building['interior_map']
                return self.building_manager.get_description(x, y, interior_map)
        
        elif self.current_location == 'dungeon':
            return ""  # Let world handle this
        
        return "Unknown location"