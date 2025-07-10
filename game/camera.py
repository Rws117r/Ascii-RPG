# game/camera.py
"""
Camera class for the ASCII RPG game.
"""
from config import TILE_SIZE, WORLD_WIDTH, WORLD_HEIGHT

class Camera:
    def __init__(self, view_width, view_height):
        self.x = 0
        self.y = 0
        self.view_width = view_width
        self.view_height = view_height

    def update(self, target):
        """Update camera position to follow the target."""
        self.x = target.x - (self.view_width / TILE_SIZE / 2)
        self.y = target.y - (self.view_height / TILE_SIZE / 2)
        
        # Keep camera within world bounds
        self.x = max(0, min(self.x, WORLD_WIDTH - self.view_width / TILE_SIZE))
        self.y = max(0, min(self.y, WORLD_HEIGHT - self.view_height / TILE_SIZE))