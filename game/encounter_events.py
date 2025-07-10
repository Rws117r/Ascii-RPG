# game/encounter_events.py
"""
Event handling for encounters and combat.
"""
import pygame
import sys
import os

# Add the parent directory to Python path so we can import our modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from systems.encounters import EncounterManager, EncounterDisplay
from systems.combat import CombatManager

class EncounterEventHandler:
    """Handles events during encounters and combat."""
    
    def __init__(self):
        self.encounter_manager = EncounterManager()
        self.combat_manager = CombatManager()
        self.selected_option = 0
        self.selected_action = 0
        
    def handle_encounter_input(self, event, encounter, player):
        """Handle input during encounter phase."""
        if event.type == pygame.KEYDOWN:
            options = EncounterDisplay.get_encounter_options(encounter)
            
            if event.key == pygame.K_UP:
                self.selected_option = (self.selected_option - 1) % len(options)
            elif event.key == pygame.K_DOWN:
                self.selected_option = (self.selected_option + 1) % len(options)
            elif event.key == pygame.K_RETURN:
                return self.process_encounter_action(encounter, player, options[self.selected_option])
            elif event.key == pygame.K_ESCAPE:
                # Try to flee if possible
                if self.encounter_manager.can_attempt_evasion(encounter):
                    return self.attempt_evasion(encounter)
        
        return None
    
    def process_encounter_action(self, encounter, player, action):
        """Process the selected encounter action."""
        if action == "Approach the monsters":
            # Move to reaction phase
            encounter['phase'] = 'reaction'
            encounter = self.encounter_manager.check_surprise(encounter, player)
            if encounter['phase'] == 'reaction':
                encounter = self.encounter_manager.roll_monster_reaction(
                    encounter, player.character.get_modifier(player.character.ability_scores['cha']))
            return {'action': 'continue_encounter', 'encounter': encounter}
        
        elif action == "Try to avoid them":
            return self.attempt_evasion(encounter)
        
        elif action == "Wait and observe":
            # Move to reaction phase (monsters notice you)
            encounter['phase'] = 'reaction'
            encounter = self.encounter_manager.check_surprise(encounter, player)
            if encounter['phase'] == 'reaction':
                encounter = self.encounter_manager.roll_monster_reaction(
                    encounter, player.character.get_modifier(player.character.ability_scores['cha']))
            return {'action': 'continue_encounter', 'encounter': encounter}
        
        elif action == "Try to communicate":
            # Roll reaction with Charisma bonus
            cha_mod = player.character.get_modifier(player.character.ability_scores['cha'])
            encounter = self.encounter_manager.roll_monster_reaction(encounter, cha_mod)
            return {'action': 'continue_encounter', 'encounter': encounter}
        
        elif action == "Prepare for combat":
            encounter['combat_started'] = True
            encounter['phase'] = 'combat'
            return {'action': 'start_combat', 'encounter': encounter}
        
        elif action == "Attempt to flee":
            return self.attempt_evasion(encounter)
        
        elif action == "Fight!":
            return {'action': 'start_combat', 'encounter': encounter}
        
        elif action == "Attempt to flee from combat":
            return self.attempt_combat_evasion(encounter)
        
        elif action in ["Attack", "Cast spell", "Move", "Other action"]:
            # Handle surprise round actions
            encounter['phase'] = 'combat'
            return {'action': 'start_combat', 'encounter': encounter}
        
        elif action == "You cannot act this round!":
            # Skip surprise round, move to normal combat
            encounter['phase'] = 'combat'
            return {'action': 'start_combat', 'encounter': encounter}
        
        return None
    
    def attempt_evasion(self, encounter):
        """Attempt to evade the encounter."""
        if self.encounter_manager.attempt_evasion(encounter):
            return {
                'action': 'evasion_success',
                'message': "You successfully avoid the encounter and slip away unnoticed."
            }
        else:
            # Failed evasion usually leads to combat
            encounter['combat_started'] = True
            encounter['phase'] = 'combat'
            return {
                'action': 'evasion_failed',
                'message': "Your attempt to flee fails! The monsters give chase and combat begins!",
                'encounter': encounter
            }
    
    def attempt_combat_evasion(self, encounter):
        """Attempt to flee from active combat."""
        # In OSE, fleeing from combat is more difficult
        # This is a simplified version
        evasion_chance = 30  # Base 30% in combat
        
        import random
        if random.randint(1, 100) <= evasion_chance:
            return {
                'action': 'combat_evasion_success',
                'message': "You successfully flee from combat!"
            }
        else:
            return {
                'action': 'combat_evasion_failed',
                'message': "You fail to escape! Combat continues.",
                'encounter': encounter
            }
    
    def handle_combat_input(self, event, player, monsters, combat_phase):
        """Handle input during combat phase."""
        if event.type == pygame.KEYDOWN:
            if combat_phase == 'declare_spells':
                return self.handle_spell_declaration(event)
            elif combat_phase == 'player_turn':
                return self.handle_player_combat_turn(event, player, monsters)
            elif combat_phase == 'monster_turn':
                # Monster turn is automatic
                return {'action': 'monster_turn'}
        
        return None
    
    def handle_spell_declaration(self, event):
        """Handle spell declaration phase."""
        if event.key == pygame.K_RETURN:
            # For now, assume no spells (can be expanded later)
            return {'action': 'spells_declared', 'spells': []}
        elif event.key == pygame.K_ESCAPE:
            return {'action': 'attempt_retreat'}
        
        return None
    
    def handle_player_combat_turn(self, event, player, monsters):
        """Handle player's combat turn input."""
        available_actions = self.combat_manager.get_available_actions(
            player, monsters, 'player_turn')
        
        if event.key == pygame.K_UP:
            self.selected_action = (self.selected_action - 1) % len(available_actions)
        elif event.key == pygame.K_DOWN:
            self.selected_action = (self.selected_action + 1) % len(available_actions)
        elif event.key == pygame.K_RETURN:
            action = available_actions[self.selected_action]
            return self.process_combat_action(action, player, monsters)
        elif event.key == pygame.K_ESCAPE:
            return {'action': 'attempt_retreat'}
        
        return None
    
    def process_combat_action(self, action, player, monsters):
        """Process the selected combat action."""
        if action == 'Melee Attack':
            # Find the first alive monster to attack
            target = next((m for m in monsters if m.is_alive), None)
            if target:
                attack_result = self.combat_manager.make_attack(player, target, 'melee')
                return {
                    'action': 'player_attack',
                    'target': target,
                    'result': attack_result
                }
        
        elif action == 'Missile Attack':
            # Find the first alive monster to attack
            target = next((m for m in monsters if m.is_alive), None)
            if target:
                attack_result = self.combat_manager.make_attack(player, target, 'missile')
                return {
                    'action': 'player_attack',
                    'target': target,
                    'result': attack_result
                }
        
        elif action == 'Move':
            return {'action': 'player_move'}
        
        elif action == 'Wait':
            return {'action': 'player_wait'}
        
        elif action == 'Retreat':
            return {'action': 'attempt_retreat'}
        
        elif action == 'Fighting Withdrawal':
            return {'action': 'fighting_withdrawal'}
        
        elif action == 'Cast Declared Spell':
            return {'action': 'cast_spell'}
        
        return None
    
    def check_for_encounter(self, player, world, current_time):
        """Check if a random encounter should occur."""
        if not self.encounter_manager.should_check_for_encounter(current_time, player.location):
            return None
        
        # Determine terrain type from player's current position
        if player.location == 'overworld':
            current_tile = world.overworld_tiles[player.y][player.x]
            terrain_map = {
                '"': 'forest',    # Forest
                '#': 'mountains', # Mountains
                ',': 'plains',    # Grass/plains
                '~': 'water'      # Water (no encounters)
            }
            terrain = terrain_map.get(current_tile, 'plains')
            
            if terrain == 'water':
                return None  # No encounters on water
            
            encounter = self.encounter_manager.check_for_encounter(terrain)
            if encounter:
                self.selected_option = 0  # Reset selection
                return encounter
        
        return None