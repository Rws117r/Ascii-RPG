# systems/encounters.py
"""
Encounter system for the ASCII RPG game based on Old-School Essentials rules.
"""
import random
import sys
import os

# Add the parent directory to Python path so we can import our modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from systems.monster_factory import MonsterFactory

class EncounterManager:
    """Manages wilderness encounters and reactions."""
    
    def __init__(self):
        self.last_check_time = 0
        self.check_interval = 10000  # Check every 10 seconds of real time for demo
        self.encounter_chance = 2  # 2-in-6 chance in wilderness
        self.monster_factory = MonsterFactory()
        
    def should_check_for_encounter(self, current_time, player_location):
        """Determine if we should check for a random encounter."""
        if player_location != 'overworld':
            return False
            
        return current_time - self.last_check_time >= self.check_interval
    
    def check_for_encounter(self, terrain='forest'):
        """Check for a random encounter."""
        import pygame  # Import here to avoid circular imports
        self.last_check_time = pygame.time.get_ticks()
        
        roll = random.randint(1, 6)
        if roll <= self.encounter_chance:
            monsters = self.monster_factory.generate_encounter_by_terrain(terrain)
            if monsters:
                return self.create_encounter(monsters)
        
        return None
    
    def create_encounter(self, monsters):
        """Create an encounter with the given monsters."""
        # Determine encounter distance (4d6 x 10 yards normally)
        distance = sum(random.randint(1, 6) for _ in range(4)) * 10
        
        encounter = {
            'monsters': monsters,
            'distance': distance,
            'surprise_checked': False,
            'player_surprised': False,
            'monsters_surprised': False,
            'reaction_rolled': False,
            'reaction': None,
            'combat_started': False,
            'phase': 'detection'  # detection, surprise, reaction, combat
        }
        
        return encounter
    
    def check_surprise(self, encounter, player):
        """Check for surprise on both sides."""
        if encounter['surprise_checked']:
            return encounter
        
        # Roll surprise for both sides (1d6, surprised on 1-2)
        player_roll = random.randint(1, 6)
        monster_roll = random.randint(1, 6)
        
        encounter['player_surprised'] = player_roll <= 2
        encounter['monsters_surprised'] = monster_roll <= 2
        encounter['surprise_checked'] = True
        
        # Adjust distance if surprise occurs
        if encounter['player_surprised'] or encounter['monsters_surprised']:
            encounter['distance'] = random.randint(1, 4) * 10
        
        # Determine next phase
        if encounter['player_surprised'] and not encounter['monsters_surprised']:
            encounter['phase'] = 'monster_surprise_round'
        elif encounter['monsters_surprised'] and not encounter['player_surprised']:
            encounter['phase'] = 'player_surprise_round'
        else:
            encounter['phase'] = 'reaction'
        
        return encounter
    
    def roll_monster_reaction(self, encounter, player_charisma_mod=0):
        """Roll for monster reaction (2d6)."""
        if encounter['reaction_rolled']:
            return encounter
        
        roll = random.randint(1, 6) + random.randint(1, 6) + player_charisma_mod
        
        if roll <= 2:
            reaction = 'hostile'
        elif roll <= 5:
            reaction = 'unfriendly'
        elif roll <= 8:
            reaction = 'neutral'
        elif roll <= 11:
            reaction = 'indifferent'
        else:
            reaction = 'friendly'
        
        encounter['reaction'] = reaction
        encounter['reaction_rolled'] = True
        
        # Set reaction on monsters
        for monster in encounter['monsters']:
            monster.reaction = reaction
        
        # Determine if combat starts
        if reaction == 'hostile':
            encounter['combat_started'] = True
            encounter['phase'] = 'combat'
        else:
            encounter['phase'] = 'interaction'
        
        return encounter
    
    def get_reaction_description(self, reaction):
        """Get a description of the monster reaction."""
        descriptions = {
            'hostile': "The monsters bare their teeth and prepare to attack!",
            'unfriendly': "The monsters eye you suspiciously and seem ready for trouble.",
            'neutral': "The monsters notice you but seem uncertain what to do.",
            'indifferent': "The monsters acknowledge your presence but continue their business.",
            'friendly': "The monsters seem curious and approach cautiously."
        }
        return descriptions.get(reaction, "The monsters react strangely.")
    
    def can_attempt_evasion(self, encounter):
        """Check if the party can attempt to evade before combat."""
        return (encounter['phase'] in ['reaction', 'interaction'] and 
                encounter['reaction'] != 'hostile')
    
    def attempt_evasion(self, encounter):
        """Attempt to evade the encounter."""
        # Simple evasion for now - could be expanded with movement rates, terrain, etc.
        evasion_chance = 50  # Base 50% chance
        
        # Modify based on reaction
        if encounter['reaction'] == 'friendly':
            evasion_chance = 90
        elif encounter['reaction'] == 'indifferent':
            evasion_chance = 70
        elif encounter['reaction'] == 'neutral':
            evasion_chance = 60
        elif encounter['reaction'] == 'unfriendly':
            evasion_chance = 40
        
        roll = random.randint(1, 100)
        return roll <= evasion_chance

class EncounterDisplay:
    """Handles displaying encounter information to the player."""
    
    @staticmethod
    def get_encounter_description(encounter):
        """Get a description of the current encounter state."""
        monsters = encounter['monsters']
        distance = encounter['distance']
        
        if len(monsters) == 1:
            monster_desc = f"a {monsters[0].name}"
        else:
            # Group similar monsters
            monster_types = {}
            for monster in monsters:
                if monster.name in monster_types:
                    monster_types[monster.name] += 1
                else:
                    monster_types[monster.name] = 1
            
            if len(monster_types) == 1:
                name, count = list(monster_types.items())[0]
                if count == 2:
                    monster_desc = f"two {name}s"
                elif count <= 10:
                    numbers = ['', 'one', 'two', 'three', 'four', 'five', 
                              'six', 'seven', 'eight', 'nine', 'ten']
                    monster_desc = f"{numbers[count]} {name}s"
                else:
                    monster_desc = f"many {name}s"
            else:
                monster_desc = "a group of monsters"
        
        base_desc = f"You encounter {monster_desc} about {distance} yards away."
        
        # Add phase-specific information
        if encounter['phase'] == 'detection':
            return base_desc + " What do you do?"
        elif encounter['phase'] == 'reaction':
            return base_desc + " They notice you as well."
        elif encounter['phase'] == 'interaction':
            reaction_desc = EncounterManager().get_reaction_description(encounter['reaction'])
            return base_desc + " " + reaction_desc
        elif encounter['phase'] == 'combat':
            return base_desc + " Combat begins!"
        elif encounter['phase'] in ['player_surprise_round', 'monster_surprise_round']:
            if encounter['player_surprised']:
                return base_desc + " You are caught off guard!"
            else:
                return base_desc + " You catch them by surprise!"
        
        return base_desc
    
    @staticmethod
    def get_encounter_options(encounter):
        """Get available options for the current encounter phase."""
        if encounter['phase'] == 'detection':
            return [
                "Approach the monsters",
                "Try to avoid them", 
                "Wait and observe"
            ]
        elif encounter['phase'] == 'reaction':
            return [
                "Try to communicate",
                "Prepare for combat",
                "Attempt to flee"
            ]
        elif encounter['phase'] == 'interaction':
            options = ["Try to communicate", "Prepare for combat"]
            if EncounterManager().can_attempt_evasion(encounter):
                options.append("Attempt to flee")
            return options
        elif encounter['phase'] in ['player_surprise_round', 'monster_surprise_round']:
            if encounter['player_surprised']:
                return ["You cannot act this round!"]
            else:
                return ["Attack", "Cast spell", "Move", "Other action"]
        elif encounter['phase'] == 'combat':
            return ["Fight!", "Attempt to flee from combat"]
        
        return []# systems/encounters.py
"""
Encounter system for the ASCII RPG game based on Old-School Essentials rules.
"""
import random
import sys
import os

# Add the parent directory to Python path so we can import our modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from entities.monsters import generate_random_encounter

class EncounterManager:
    """Manages wilderness encounters and reactions."""
    
    def __init__(self):
        self.last_check_time = 0
        self.check_interval = 10000  # Check every 10 seconds of real time for demo
        self.encounter_chance = 2  # 2-in-6 chance in wilderness
        
    def should_check_for_encounter(self, current_time, player_location):
        """Determine if we should check for a random encounter."""
        if player_location != 'overworld':
            return False
            
        return current_time - self.last_check_time >= self.check_interval
    
    def check_for_encounter(self, terrain='forest'):
        """Check for a random encounter."""
        self.last_check_time = pygame.time.get_ticks()
        
        roll = random.randint(1, 6)
        if roll <= self.encounter_chance:
            monsters = generate_random_encounter(terrain)
            if monsters:
                return self.create_encounter(monsters)
        
        return None
    
    def create_encounter(self, monsters):
        """Create an encounter with the given monsters."""
        # Determine encounter distance (4d6 x 10 yards normally)
        distance = sum(random.randint(1, 6) for _ in range(4)) * 10
        
        encounter = {
            'monsters': monsters,
            'distance': distance,
            'surprise_checked': False,
            'player_surprised': False,
            'monsters_surprised': False,
            'reaction_rolled': False,
            'reaction': None,
            'combat_started': False,
            'phase': 'detection'  # detection, surprise, reaction, combat
        }
        
        return encounter
    
    def check_surprise(self, encounter, player):
        """Check for surprise on both sides."""
        if encounter['surprise_checked']:
            return encounter
        
        # Roll surprise for both sides (1d6, surprised on 1-2)
        player_roll = random.randint(1, 6)
        monster_roll = random.randint(1, 6)
        
        encounter['player_surprised'] = player_roll <= 2
        encounter['monsters_surprised'] = monster_roll <= 2
        encounter['surprise_checked'] = True
        
        # Adjust distance if surprise occurs
        if encounter['player_surprised'] or encounter['monsters_surprised']:
            encounter['distance'] = random.randint(1, 4) * 10
        
        # Determine next phase
        if encounter['player_surprised'] and not encounter['monsters_surprised']:
            encounter['phase'] = 'monster_surprise_round'
        elif encounter['monsters_surprised'] and not encounter['player_surprised']:
            encounter['phase'] = 'player_surprise_round'
        else:
            encounter['phase'] = 'reaction'
        
        return encounter
    
    def roll_monster_reaction(self, encounter, player_charisma_mod=0):
        """Roll for monster reaction (2d6)."""
        if encounter['reaction_rolled']:
            return encounter
        
        roll = random.randint(1, 6) + random.randint(1, 6) + player_charisma_mod
        
        if roll <= 2:
            reaction = 'hostile'
        elif roll <= 5:
            reaction = 'unfriendly'
        elif roll <= 8:
            reaction = 'neutral'
        elif roll <= 11:
            reaction = 'indifferent'
        else:
            reaction = 'friendly'
        
        encounter['reaction'] = reaction
        encounter['reaction_rolled'] = True
        
        # Set reaction on monsters
        for monster in encounter['monsters']:
            monster.reaction = reaction
        
        # Determine if combat starts
        if reaction == 'hostile':
            encounter['combat_started'] = True
            encounter['phase'] = 'combat'
        else:
            encounter['phase'] = 'interaction'
        
        return encounter
    
    def get_reaction_description(self, reaction):
        """Get a description of the monster reaction."""
        descriptions = {
            'hostile': "The monsters bare their teeth and prepare to attack!",
            'unfriendly': "The monsters eye you suspiciously and seem ready for trouble.",
            'neutral': "The monsters notice you but seem uncertain what to do.",
            'indifferent': "The monsters acknowledge your presence but continue their business.",
            'friendly': "The monsters seem curious and approach cautiously."
        }
        return descriptions.get(reaction, "The monsters react strangely.")
    
    def can_attempt_evasion(self, encounter):
        """Check if the party can attempt to evade before combat."""
        return (encounter['phase'] in ['reaction', 'interaction'] and 
                encounter['reaction'] != 'hostile')
    
    def attempt_evasion(self, encounter):
        """Attempt to evade the encounter."""
        # Simple evasion for now - could be expanded with movement rates, terrain, etc.
        evasion_chance = 50  # Base 50% chance
        
        # Modify based on reaction
        if encounter['reaction'] == 'friendly':
            evasion_chance = 90
        elif encounter['reaction'] == 'indifferent':
            evasion_chance = 70
        elif encounter['reaction'] == 'neutral':
            evasion_chance = 60
        elif encounter['reaction'] == 'unfriendly':
            evasion_chance = 40
        
        roll = random.randint(1, 100)
        return roll <= evasion_chance

import pygame  # Need this for time tracking

class EncounterDisplay:
    """Handles displaying encounter information to the player."""
    
    @staticmethod
    def get_encounter_description(encounter):
        """Get a description of the current encounter state."""
        monsters = encounter['monsters']
        distance = encounter['distance']
        
        if len(monsters) == 1:
            monster_desc = f"a {monsters[0].name}"
        else:
            # Group similar monsters
            monster_types = {}
            for monster in monsters:
                if monster.name in monster_types:
                    monster_types[monster.name] += 1
                else:
                    monster_types[monster.name] = 1
            
            if len(monster_types) == 1:
                name, count = list(monster_types.items())[0]
                if count == 2:
                    monster_desc = f"two {name}s"
                elif count <= 10:
                    numbers = ['', 'one', 'two', 'three', 'four', 'five', 
                              'six', 'seven', 'eight', 'nine', 'ten']
                    monster_desc = f"{numbers[count]} {name}s"
                else:
                    monster_desc = f"many {name}s"
            else:
                monster_desc = "a group of monsters"
        
        base_desc = f"You encounter {monster_desc} about {distance} yards away."
        
        # Add phase-specific information
        if encounter['phase'] == 'detection':
            return base_desc + " What do you do?"
        elif encounter['phase'] == 'reaction':
            return base_desc + " They notice you as well."
        elif encounter['phase'] == 'interaction':
            reaction_desc = EncounterManager().get_reaction_description(encounter['reaction'])
            return base_desc + " " + reaction_desc
        elif encounter['phase'] == 'combat':
            return base_desc + " Combat begins!"
        elif encounter['phase'] in ['player_surprise_round', 'monster_surprise_round']:
            if encounter['player_surprised']:
                return base_desc + " You are caught off guard!"
            else:
                return base_desc + " You catch them by surprise!"
        
        return base_desc
    
    @staticmethod
    def get_encounter_options(encounter):
        """Get available options for the current encounter phase."""
        if encounter['phase'] == 'detection':
            return [
                "Approach the monsters",
                "Try to avoid them", 
                "Wait and observe"
            ]
        elif encounter['phase'] == 'reaction':
            return [
                "Try to communicate",
                "Prepare for combat",
                "Attempt to flee"
            ]
        elif encounter['phase'] == 'interaction':
            options = ["Try to communicate", "Prepare for combat"]
            if EncounterManager().can_attempt_evasion(encounter):
                options.append("Attempt to flee")
            return options
        elif encounter['phase'] in ['player_surprise_round', 'monster_surprise_round']:
            if encounter['player_surprised']:
                return ["You cannot act this round!"]
            else:
                return ["Attack", "Cast spell", "Move", "Other action"]
        elif encounter['phase'] == 'combat':
            return ["Fight!", "Attempt to flee from combat"]
        
        return []