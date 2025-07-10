# entities/monsters.py
"""
Monster classes using centralized ASCII definitions.
"""
import random
from ui.colors import C_TEXT_DIM, C_BROWN
from ui.ascii_definitions import ASCII_DEFS

class Monster:
    """Base monster class using ASCII definitions."""
    def __init__(self, name, entity_id, ac, hd, hp, attacks, thac0, movement, 
                 saves, morale, alignment, xp_value, special_abilities=None):
        self.name = name
        self.entity_id = entity_id
        
        # Get character and color from ASCII definitions
        entity_def = ASCII_DEFS.get_entity(entity_id)
        self.char = entity_def['char']
        self.color = entity_def['color']
        
        # Monster stats
        self.ac = ac
        self.hd = hd
        self.hp = hp
        self.max_hp = hp
        self.attacks = attacks
        self.thac0 = thac0
        self.movement = movement
        self.saves = saves
        self.morale = morale
        self.alignment = alignment
        self.xp_value = xp_value
        self.special_abilities = special_abilities or []
        
        # Combat state
        self.is_alive = True
        self.reaction = None
        self.has_acted_this_round = False
        
        # Visual effects
        self.color_effect = None
        self.char_effect = None

    def add_visual_effect(self, effect_type):
        """Add a visual effect to the monster."""
        if effect_type == 'burning':
            # Add fire effect
            from ui.ascii_definitions import ColorPulse
            self.color_effect = ColorPulse(self.color, (255, 100, 0), duration=1000, repeat=True)
            self.color_effect.start()
        elif effect_type == 'poisoned':
            # Add poison effect
            from ui.ascii_definitions import ColorPulse
            self.color_effect = ColorPulse(self.color, (100, 255, 100), duration=1500, repeat=True)
            self.color_effect.start()
        elif effect_type == 'frozen':
            # Add ice effect
            from ui.ascii_definitions import ColorPulse
            self.color_effect = ColorPulse(self.color, (150, 200, 255), duration=2000, repeat=True)
            self.color_effect.start()

    def get_render_info(self):
        """Get current rendering information with effects."""
        char = self.char
        color = self.color
        
        # Apply color effects
        if self.color_effect and self.color_effect.active:
            self.color_effect.update()
            color = self.color_effect.get_current_color()
        
        # Apply character effects
        if self.char_effect and self.char_effect.active:
            self.char_effect.update()
            char = self.char_effect.get_current_char()
        
        return {'char': char, 'color': color}

    def take_damage(self, damage):
        """Apply damage to the monster."""
        self.hp -= damage
        if self.hp <= 0:
            self.hp = 0
            self.is_alive = False
        return self.hp <= 0

    def heal(self, amount):
        """Heal the monster."""
        self.hp = min(self.hp + amount, self.max_hp)

    def make_attack_roll(self, target_ac, ability_modifier=0, situational_modifier=0):
        """Make an attack roll against a target AC."""
        roll = random.randint(1, 20)
        total_roll = roll + ability_modifier + situational_modifier
        
        required_roll = self.thac0 - target_ac
        hit = total_roll >= required_roll
        
        return {
            'roll': roll,
            'total': total_roll,
            'required': required_roll,
            'hit': hit,
            'critical': roll == 20,
            'fumble': roll == 1
        }

    def roll_damage(self, attack_index=0):
        """Roll damage for an attack."""
        if attack_index >= len(self.attacks):
            return 0
        
        attack = self.attacks[attack_index]
        damage_dice = attack.get('damage', '1d4')
        
        if 'd' in damage_dice:
            if damage_dice.startswith('1d'):
                die_size = int(damage_dice[2:])
                return random.randint(1, die_size)
            else:
                parts = damage_dice.split('d')
                num_dice = int(parts[0])
                die_size = int(parts[1])
                return sum(random.randint(1, die_size) for _ in range(num_dice))
        else:
            return int(damage_dice)

    def make_morale_check(self, modifier=0):
        """Make a morale check. Returns True if passes (continues fighting)."""
        roll = random.randint(2, 12)
        return roll + modifier <= self.morale

class Kobold(Monster):
    """Kobold monster implementation."""
    def __init__(self, is_chieftain=False, is_bodyguard=False):
        if is_chieftain:
            name = "Kobold Chieftain"
            entity_id = 'kobold_chieftain'
            hd = 2
            hp = random.randint(1, 8) + random.randint(1, 8)
            morale = 8
            xp_value = 20
        elif is_bodyguard:
            name = "Kobold Bodyguard"
            entity_id = 'kobold'  # Use regular kobold appearance
            hd = 1.5
            hp = random.randint(1, 8) + 1
            morale = 8
            xp_value = 15
        else:
            name = "Kobold"
            entity_id = 'kobold'
            hd = 0.5
            hp = 2
            morale = 6
            xp_value = 5

        attacks = [{'name': 'weapon', 'damage': '1d4-1', 'type': 'melee'}]
        saves = {'death': 14, 'wands': 15, 'paralysis': 16, 'breath': 17, 'spells': 18}
        special_abilities = ['ambush', 'infravision_90', 'hate_gnomes']

        super().__init__(
            name=name,
            entity_id=entity_id,
            ac=7,
            hd=hd,
            hp=hp,
            attacks=attacks,
            thac0=19,
            movement=60,
            saves=saves,
            morale=morale,
            alignment='Chaotic',
            xp_value=xp_value,
            special_abilities=special_abilities
        )

        self.is_chieftain = is_chieftain
        self.is_bodyguard = is_bodyguard

    def roll_damage(self, attack_index=0):
        """Override damage rolling for kobold weapon attacks."""
        base_damage = random.randint(1, 4)
        return max(1, base_damage - 1)

def create_kobold_group(location='wilderness'):
    """Create a group of kobolds based on location."""
    kobolds = []
    
    if location == 'wilderness' or location == 'lair':
        # 6d10 kobolds in wilderness/lair
        num_kobolds = sum(random.randint(1, 10) for _ in range(6))
        
        # Add chieftain and bodyguards for large groups
        if num_kobolds >= 10:
            kobolds.append(Kobold(is_chieftain=True))
            num_bodyguards = random.randint(1, 6)
            for _ in range(num_bodyguards):
                kobolds.append(Kobold(is_bodyguard=True))
            num_kobolds -= (1 + num_bodyguards)  # Subtract leader types
    else:
        # 4d4 kobolds in dungeons
        num_kobolds = sum(random.randint(1, 4) for _ in range(4))
    
    # Add regular kobolds
    for _ in range(num_kobolds):
        kobolds.append(Kobold())
    
    return kobolds

def get_monster_by_name(name):
    """Factory function to create monsters by name."""
    if name.lower() == 'kobold':
        return Kobold()
    elif name.lower() == 'kobold_chieftain':
        return Kobold(is_chieftain=True)
    elif name.lower() == 'kobold_bodyguard':
        return Kobold(is_bodyguard=True)
    else:
        # Default to kobold if unknown
        return Kobold()

# Monster encounter tables
WILDERNESS_MONSTERS = {
    'forest': [
        {'name': 'kobold', 'chance': 30, 'group_func': lambda: create_kobold_group('wilderness')},
        # Add more monsters here later
    ],
    'mountains': [
        {'name': 'kobold', 'chance': 40, 'group_func': lambda: create_kobold_group('wilderness')},
    ],
    'plains': [
        {'name': 'kobold', 'chance': 20, 'group_func': lambda: create_kobold_group('wilderness')},
    ]
}

def generate_random_encounter(terrain='forest'):
    """Generate a random encounter based on terrain."""
    monster_table = WILDERNESS_MONSTERS.get(terrain, WILDERNESS_MONSTERS['forest'])
    
    # Simple random selection for now
    if monster_table:
        encounter = random.choice(monster_table)
        return encounter['group_func']()
    
    return []