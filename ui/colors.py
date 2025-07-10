# ui/colors.py
"""
Color palette for the ASCII RPG game.
"""

def hex_to_rgb(hex_code):
    """Converts a hex color code to an RGB tuple."""
    hex_code = hex_code.lstrip('#')
    return tuple(int(hex_code[i:i+2], 16) for i in (0, 2, 4))

# AAP-64 Palette
C_BACKGROUND = hex_to_rgb("#060608")
C_PANEL_BG = hex_to_rgb("#141013")
C_TEXT = hex_to_rgb("#d6f264")
C_TEXT_DIM = hex_to_rgb("#9cdb43")
C_BORDER = hex_to_rgb("#59c135")
C_PLAYER = hex_to_rgb("#ffd541")
C_GOLD = hex_to_rgb("#f9a31b")
C_WATER = hex_to_rgb("#285cc4")
C_GRASS = hex_to_rgb("#59c135")
C_FOREST = hex_to_rgb("#1a7a3e")
C_MOUNTAIN = hex_to_rgb("#6d758d")
C_CAVE_FLOOR = hex_to_rgb("#5a4e44")
C_CURSOR = hex_to_rgb("#fffc40")
C_BROWN = hex_to_rgb("#71413b")
C_WHITE = hex_to_rgb("#ffffff")
C_STRUCTURE = hex_to_rgb("#dba463")
C_PATH = hex_to_rgb("#a08662")