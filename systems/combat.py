# systems/combat.py
"""
Combat system for the ASCII RPG game based on Old-School Essentials rules.
"""
import random

class CombatManager:
    """Manages combat encounters and rounds."""
    
    def __init__(self):
        self.current_round = 0
        self.initiative_order = []
        self.player_acted = False
        self.monsters_acted = False
        self.declared_spells = []
        self.combat_log = []
        
    def start_combat(self, player, monsters):
        """Initialize combat with the given participants."""
        self.current_round = 1
        self.player_acted = False
        self.monsters_acted = False
        self.declared_spells = []
        self.combat_log = []
        
        # Reset monster combat state
        for monster in monsters:
            monster.has_acted_this_round = False
        
        return self.start_new_round(player, monsters)
    
    def start_new_round(self, player, monsters):
        """Start a new combat round."""
        self.current_round += 1
        self.player_acted = False
        self.monsters_acted = False
        
        # Reset monster acted state
        for monster in monsters:
            monster.has_acted_this_round = False
        
        # Roll initiative
        player_initiative = random.randint(1, 6)
        monster_initiative = random.randint(1, 6)
        
        self.combat_log.append(f"--- Round {self.current_round} ---")
        self.combat_log.append(f"Initiative: Player {player_initiative}, Monsters {monster_initiative}")
        
        if player_initiative > monster_initiative:
            self.initiative_order = ['player', 'monsters']
            self.combat_log.append("Player acts first!")
        elif monster_initiative > player_initiative:
            self.initiative_order = ['monsters', 'player']
            self.combat_log.append("Monsters act first!")
        else:
            self.initiative_order = ['simultaneous']
            self.combat_log.append("Simultaneous actions!")
        
        return {
            'round': self.current_round,
            'initiative_order': self.initiative_order,
            'player_initiative': player_initiative,
            'monster_initiative': monster_initiative,
            'phase': 'declare_spells'
        }
    
    def get_available_actions(self, player, monsters, phase):
        """Get available actions for the current combat phase."""
        if phase == 'declare_spells':
            return ['Declare Spell', 'No Spell', 'Retreat']
        elif phase == 'player_turn':
            actions = []
            
            # Check if any monsters are in melee range (adjacent)
            in_melee = any(self.calculate_distance(player, monster) <= 5 for monster in monsters if monster.is_alive)
            
            if in_melee:
                actions.extend(['Melee Attack', 'Fighting Withdrawal'])
            else:
                actions.extend(['Move', 'Missile Attack'])
            
            if self.declared_spells:
                actions.append('Cast Declared Spell')
            
            actions.extend(['Wait', 'Retreat'])
            return actions
        elif phase == 'monster_turn':
            return ['Monsters Act']  # Automatic
        
        return []
    
    def calculate_distance(self, entity1, entity2):
        """Calculate distance between two entities (simplified)."""
        # For now, assume all combat happens at close range
        # In a full implementation, you'd track positions
        return 5  # Assume 5 feet (melee range)
    
    def make_attack(self, attacker, target, attack_type='melee'):
        """Execute an attack from attacker to target."""
        # Get target AC
        if hasattr(target, 'character'):
            # Player target
            target_ac = self.calculate_player_ac(target)
            target_name = target.character.name
        else:
            # Monster target
            target_ac = target.ac
            target_name = target.name
        
        # Get attacker's relevant ability modifier
        if hasattr(attacker, 'character'):
            # Player attacker
            if attack_type == 'melee':
                ability_mod = attacker.character.get_modifier(attacker.character.ability_scores['str'])
            else:  # missile
                ability_mod = attacker.character.get_modifier(attacker.character.ability_scores['dex'])
            attacker_name = attacker.character.name
            attacker_thac0 = attacker.character.thac0
        else:
            # Monster attacker
            ability_mod = 0  # Monsters don't have ability scores in this simple system
            attacker_name = attacker.name
            attacker_thac0 = attacker.thac0
        
        # Make attack roll
        attack_result = self.make_attack_roll(attacker_thac0, target_ac, ability_mod)
        
        if attack_result['hit']:
            # Roll damage
            if hasattr(attacker, 'character'):
                # Player damage (simplified - using a basic weapon)
                damage = random.randint(1, 6) + ability_mod if attack_type == 'melee' else random.randint(1, 6)
                damage = max(1, damage)  # Minimum 1 damage
            else:
                # Monster damage
                damage = attacker.roll_damage()
            
            # Apply damage
            if hasattr(target, 'character'):
                # Damage to player
                target.character.hp -= damage
                died = target.character.hp <= 0
            else:
                # Damage to monster
                died = target.take_damage(damage)
            
            self.combat_log.append(f"{attacker_name} hits {target_name} for {damage} damage!")
            
            if died:
                self.combat_log.append(f"{target_name} is slain!")
            
            return {
                'hit': True,
                'damage': damage,
                'target_died': died,
                'roll': attack_result['roll'],
                'total': attack_result['total']
            }
        else:
            self.combat_log.append(f"{attacker_name} attacks {target_name} but misses!")
            return {
                'hit': False,
                'damage': 0,
                'target_died': False,
                'roll': attack_result['roll'],
                'total': attack_result['total']
            }
    
    def make_attack_roll(self, thac0, target_ac, ability_modifier=0, situational_modifier=0):
        """Make an attack roll using THAC0 system."""
        roll = random.randint(1, 20)
        total_roll = roll + ability_modifier + situational_modifier
        
        # Calculate required roll: THAC0 - Target AC
        required_roll = thac0 - target_ac
        hit = total_roll >= required_roll
        
        return {
            'roll': roll,
            'total': total_roll,
            'required': required_roll,
            'hit': hit,
            'critical': roll == 20,
            'fumble': roll == 1
        }
    
    def calculate_player_ac(self, player):
        """Calculate player's effective AC from equipment."""
        base_ac = 10  # Unarmored AC 10
        ac_bonus = 0
        
        # Add armor bonuses (simplified)
        for slot, item in player.character.equipped.items():
            if item and item.item_type == 'armor':
                ac_bonus += item.defense
        
        # Add dexterity modifier
        dex_mod = player.character.get_modifier(player.character.ability_scores['dex'])
        ac_bonus += dex_mod
        
        return base_ac - ac_bonus  # Lower is better in AD&D
    
    def monster_ai_action(self, monster, player, other_monsters):
        """Determine what action a monster should take."""
        if not monster.is_alive:
            return None
        
        # Simple AI: always attack if able
        distance = self.calculate_distance(monster, player)
        
        if distance <= 5:  # In melee range
            return {
                'type': 'melee_attack',
                'target': player
            }
        else:
            return {
                'type': 'move_and_attack',
                'target': player
            }
    
    def execute_monster_turn(self, monsters, player):
        """Execute all monster actions for their turn."""
        results = []
        
        for monster in monsters:
            if not monster.is_alive or monster.has_acted_this_round:
                continue
            
            # Check morale if monster is wounded
            if monster.hp < monster.max_hp // 2:  # Below half health
                if not monster.make_morale_check():
                    self.combat_log.append(f"{monster.name} flees in terror!")
                    monster.is_alive = False  # Remove from combat
                    monster.has_acted_this_round = True
                    continue
            
            action = self.monster_ai_action(monster, player, monsters)
            
            if action:
                if action['type'] in ['melee_attack', 'move_and_attack']:
                    attack_result = self.make_attack(monster, player, 'melee')
                    results.append({
                        'monster': monster,
                        'action': 'attack',
                        'result': attack_result
                    })
                
                monster.has_acted_this_round = True
        
        return results
    
    def check_combat_end(self, player, monsters):
        """Check if combat should end."""
        player_alive = player.character.hp > 0
        monsters_alive = any(monster.is_alive for monster in monsters)
        
        if not player_alive:
            return {'ended': True, 'result': 'player_defeat'}
        elif not monsters_alive:
            return {'ended': True, 'result': 'player_victory'}
        else:
            return {'ended': False, 'result': None}
    
    def award_experience(self, player, defeated_monsters):
        """Award experience points for defeated monsters."""
        total_xp = sum(monster.xp_value for monster in defeated_monsters if not monster.is_alive)
        
        if total_xp > 0:
            player.character.xp += total_xp
            self.combat_log.append(f"You gain {total_xp} experience points!")
        
        return total_xp
    
    def get_combat_summary(self):
        """Get a summary of the current combat state."""
        return {
            'round': self.current_round,
            'log': self.combat_log.copy(),
            'initiative_order': self.initiative_order,
            'player_acted': self.player_acted,
            'monsters_acted': self.monsters_acted
        }