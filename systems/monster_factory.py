# systems/monster_factory.py
"""
Data-driven monster factory for creating encounters from JSON data.
"""
import json
import random
import os
import sys

# Add the parent directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from entities.monsters import Monster

class MonsterFactory:
    """Factory for creating monsters from JSON data."""
    
    def __init__(self):
        self.monster_data = {}
        self.encounter_tables = {}
        self.subtables = {}
        self.load_monster_data()
    
    def load_monster_data(self):
        """Load monster data from JSON file."""
        try:
            # Try to load from data directory
            data_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'monsters.json')
            if not os.path.exists(data_path):
                # Fallback: create basic data if file doesn't exist
                self.create_default_data()
                return
                
            with open(data_path, 'r') as f:
                data = json.load(f)
                
            self.monster_data = data.get('monsters', {})
            self.encounter_tables = data.get('encounter_tables', {})
            self.subtables = data.get('subtables', {})
            
        except Exception as e:
            print(f"Error loading monster data: {e}")
            self.create_default_data()
    
    def create_default_data(self):
        """Create default monster data if JSON file is missing."""
        self.monster_data = {
            'kobold': {
                'name': 'Kobold',
                'char': 'k',
                'color': [113, 65, 59],
                'ac': 7,
                'hd': 0.5,
                'hp_roll': '1d4+1',
                'attacks': [{'name': 'weapon', 'damage': '1d4-1', 'type': 'melee'}],
                'thac0': 19,
                'movement': 60,
                'saves': {'death': 14, 'wands': 15, 'paralysis': 16, 'breath': 17, 'spells': 18},
                'morale': 6,
                'alignment': 'Chaotic',
                'xp_value': 5,
                'special_abilities': ['ambush', 'infravision_90', 'hate_gnomes'],
                'encounter_size': '4d4'
            },
            'goblin': {
                'name': 'Goblin',
                'char': 'g',
                'color': [139, 69, 19],
                'ac': 6,
                'hd': 1,
                'hp_roll': '1d8',
                'attacks': [{'name': 'weapon', 'damage': '1d6', 'type': 'melee'}],
                'thac0': 19,
                'movement': 60,
                'saves': {'death': 14, 'wands': 15, 'paralysis': 16, 'breath': 17, 'spells': 18},
                'morale': 7,
                'alignment': 'Chaotic',
                'xp_value': 10,
                'special_abilities': ['infravision_60'],
                'encounter_size': '2d4'
            },
            'wolf': {
                'name': 'Wolf',
                'char': 'w',
                'color': [105, 105, 105],
                'ac': 7,
                'hd': 2,
                'hp_roll': '2d8',
                'attacks': [{'name': 'bite', 'damage': '1d6', 'type': 'melee'}],
                'thac0': 18,
                'movement': 180,
                'saves': {'death': 14, 'wands': 15, 'paralysis': 16, 'breath': 17, 'spells': 18},
                'morale': 8,
                'alignment': 'Neutral',
                'xp_value': 20,
                'special_abilities': ['pack_tactics'],
                'encounter_size': '2d6'
            }
        }
        
        self.encounter_tables = {
            'forest': {
                '1-2': {'category': 'animal', 'result': 'wolf'},
                '3-4': {'category': 'humanoid', 'result': 'goblin'},
                '5-6': {'category': 'humanoid', 'result': 'kobold'},
                '7-8': {'category': 'animal', 'result': 'wolf'}
            }
        }
    
    def create_monster(self, monster_id, custom_hp=None):
        """Create a monster instance from its ID."""
        if monster_id not in self.monster_data:
            # Fallback to kobold if monster not found
            monster_id = 'kobold'
            
        data = self.monster_data[monster_id]
        
        # Calculate HP
        if custom_hp:
            hp = custom_hp
        else:
            hp = self.roll_hp(data['hp_roll'])
        
        # Create the monster
        monster = Monster(
            name=data['name'],
            char=data['char'],
            color=tuple(data['color']),
            ac=data['ac'],
            hd=data['hd'],
            hp=hp,
            attacks=data['attacks'],
            thac0=data['thac0'],
            movement=data['movement'],
            saves=data['saves'],
            morale=data['morale'],
            alignment=data['alignment'],
            xp_value=data['xp_value'],
            special_abilities=data.get('special_abilities', [])
        )
        
        return monster
    
    def roll_hp(self, hp_roll_string):
        """Roll HP based on dice notation (e.g., '2d8', '1d4+1')."""
        try:
            # Handle simple cases like '2d8', '1d4+1', '1d4-1'
            if '+' in hp_roll_string:
                dice_part, bonus = hp_roll_string.split('+')
                bonus = int(bonus)
            elif '-' in hp_roll_string:
                dice_part, penalty = hp_roll_string.split('-')
                bonus = -int(penalty)
            else:
                dice_part = hp_roll_string
                bonus = 0
            
            # Parse dice notation
            if 'd' in dice_part:
                num_dice, die_size = dice_part.split('d')
                num_dice = int(num_dice)
                die_size = int(die_size)
                
                total = sum(random.randint(1, die_size) for _ in range(num_dice))
                return max(1, total + bonus)
            else:
                return max(1, int(dice_part) + bonus)
                
        except Exception:
            return 1  # Fallback to 1 HP
    
    def roll_encounter_size(self, size_string):
        """Roll the number of monsters in an encounter."""
        try:
            if 'd' in size_string:
                if '+' in size_string:
                    dice_part, bonus = size_string.split('+')
                    bonus = int(bonus)
                elif '-' in size_string:
                    dice_part, penalty = size_string.split('-')
                    bonus = -int(penalty)
                else:
                    dice_part = size_string
                    bonus = 0
                
                num_dice, die_size = dice_part.split('d')
                num_dice = int(num_dice)
                die_size = int(die_size)
                
                total = sum(random.randint(1, die_size) for _ in range(num_dice))
                return max(1, total + bonus)
            else:
                return max(1, int(size_string))
        except Exception:
            return 1
    
    def generate_encounter_by_terrain(self, terrain):
        """Generate an encounter for a specific terrain."""
        # Fallback to forest if terrain not found
        if terrain not in self.encounter_tables:
            terrain = 'forest'
        
        table = self.encounter_tables[terrain]
        
        # Roll d8 for main encounter type
        roll = random.randint(1, 8)
        
        # Find the appropriate entry
        for range_key, encounter_data in table.items():
            if self.roll_in_range(roll, range_key):
                return self.resolve_encounter(encounter_data)
        
        # Fallback
        return self.create_monster_group('kobold')
    
    def roll_in_range(self, roll, range_string):
        """Check if a roll falls within a range (e.g., '1-3', '4', '5-6')."""
        if '-' in range_string:
            start, end = map(int, range_string.split('-'))
            return start <= roll <= end
        else:
            return roll == int(range_string)
    
    def resolve_encounter(self, encounter_data):
        """Resolve an encounter from encounter data."""
        if 'result' in encounter_data:
            # Direct monster reference
            return self.create_monster_group(encounter_data['result'])
        elif 'subtable' in encounter_data:
            # Roll on a subtable
            subtable_name = encounter_data['subtable']
            category = encounter_data.get('category', '')
            return self.roll_on_subtable(subtable_name, category)
        else:
            # Fallback
            return self.create_monster_group('kobold')
    
    def roll_on_subtable(self, subtable_name, category=''):
        """Roll on a subtable to determine the encounter."""
        if subtable_name not in self.subtables:
            return self.create_monster_group('kobold')
        
        subtable = self.subtables[subtable_name]
        
        # Handle special subtables like dragon_flyer_insect
        if category and category in subtable:
            category_table = subtable[category]
            roll = random.randint(1, 20)
            
            for range_key, monster_id in category_table.items():
                if self.roll_in_range(roll, range_key):
                    return self.create_monster_group(monster_id)
        else:
            # Regular subtable
            roll = random.randint(1, 20)
            
            for range_key, monster_id in subtable.items():
                if self.roll_in_range(roll, range_key):
                    return self.create_monster_group(monster_id)
        
        # Fallback
        return self.create_monster_group('kobold')
    
    def create_monster_group(self, monster_id):
        """Create a group of monsters of the specified type."""
        if monster_id not in self.monster_data:
            monster_id = 'kobold'  # Fallback
        
        data = self.monster_data[monster_id]
        group_size = self.roll_encounter_size(data['encounter_size'])
        
        monsters = []
        for _ in range(group_size):
            monster = self.create_monster(monster_id)
            monsters.append(monster)
        
        return monsters
    
    def get_available_monsters(self):
        """Get a list of all available monster IDs."""
        return list(self.monster_data.keys())
    
    def get_monster_info(self, monster_id):
        """Get the raw data for a monster."""
        return self.monster_data.get(monster_id, None)