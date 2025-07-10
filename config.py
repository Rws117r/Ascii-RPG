# config.py
"""
Configuration constants for the ASCII RPG game.
"""
import os

# --- Screen dimensions ---
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

# --- UI Layout ---
STATUS_PANEL_WIDTH = 240
INVENTORY_PANEL_WIDTH = 300
ANIMATION_SPEED = 30

# --- Font settings ---
FONT_NAME = os.path.join(os.path.dirname(__file__), 'DejaVuSansMono.ttf')
FONT_SIZE = 18
TILE_FONT_SIZE = 24

# --- Game world dimensions ---
WORLD_WIDTH = 150
WORLD_HEIGHT = 150

# --- Tile size ---
TILE_SIZE = 20

# --- Movement settings ---
MOVE_DELAY = 100