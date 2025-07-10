# entities/items.py
"""
Item classes using centralized ASCII definitions.
"""
import random
from ui.colors import C_TEXT_DIM, C_TEXT, C_BROWN
from ui.ascii_definitions import ASCII_DEFS

class Item:
    def __init__(self, name, item_id, slot, item_type, hands=1, damage='1d6', defense=0):
        self.name = name
        self.item_id = item_id
        self.slot = slot
        self.item_type = item_type
        self.hands = hands
        self.damage = damage
        self.defense = defense
        
        # Get character and color from ASCII definitions
        item_def = ASCII_DEFS.get_item(item_id)
        self.char = item_def['char']
        self.color = item_def['color']

def create_random_item():
    """Creates a random item using ASCII definitions."""
    items_data = [
        ("Rusty Sword", 'sword', 'weapon', 'weapon', 1, '1d8', 0),
        ("Iron Axe", 'axe', 'weapon', 'weapon', 1, '1d8', 0),
        ("Greatsword", 'greatsword', 'weapon', 'weapon', 2, '1d10', 0),
        ("Leather Helm", 'helmet', 'helmet', 'armor', 1, '1d6', 1),
        ("Steel Cuirass", 'armor_piece', 'cuirass', 'armor', 1, '1d6', 3),
        ("Chain Glove", 'armor_piece', 'left_glove', 'armor', 1, '1d6', 1),
        ("Plated Greaves", 'armor_piece', 'greaves', 'armor', 1, '1d6', 2),
        ("Worn Boots", 'armor_piece', 'boots', 'armor', 1, '1d6', 1),
        ("Wooden Shield", 'shield', 'shield', 'armor', 1, '1d6', 2)
    ]
    
    name, item_id, slot, item_type, hands, damage, defense = random.choice(items_data)
    return Item(name, item_id, slot, item_type, hands, damage, defense)