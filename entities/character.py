# entities/character.py
"""
Character class for the ASCII RPG game.
"""

class Character:
    def __init__(self):
        self.name = "Hero"
        self.char_class = "Fighter"
        self.level = 1
        self.xp = 0
        self.hp = 10
        self.max_hp = 10
        self.ability_scores = {
            'str': 13, 'dex': 12, 'con': 11, 
            'int': 9, 'wis': 8, 'cha': 10
        }
        self.thac0 = 19
        self.saving_throws = {
            'death': 12, 'wands': 13, 'paralysis': 14, 
            'breath': 15, 'spells': 16
        }
        self.inventory = []
        self.equipped = {
            'helmet': None, 'cuirass': None, 'greaves': None, 'boots': None,
            'left_glove': None, 'right_glove': None,
            'weapon': None, 'shield': None
        }

    def get_modifier(self, score):
        """Calculate ability score modifier."""
        if score <= 3: return -3
        if score <= 5: return -2
        if score <= 8: return -1
        if score <= 12: return 0
        if score <= 15: return 1
        if score <= 17: return 2
        return 3