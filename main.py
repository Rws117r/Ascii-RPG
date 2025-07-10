# main.py
"""
ASCII RPG with complete encounter and combat system using centralized ASCII definitions.
"""
import pygame
import sys
import os

# Add the current directory to the Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

# Import configuration constants
from config import (
    SCREEN_WIDTH, SCREEN_HEIGHT, STATUS_PANEL_WIDTH, INVENTORY_PANEL_WIDTH,
    FONT_NAME, FONT_SIZE, TILE_FONT_SIZE, WORLD_WIDTH, WORLD_HEIGHT, TILE_SIZE
)

# Import colors
from ui.colors import (
    C_BACKGROUND, C_PANEL_BG, C_TEXT, C_TEXT_DIM, C_BORDER, C_PLAYER,
    C_GOLD, C_WATER, C_GRASS, C_FOREST, C_MOUNTAIN, C_CURSOR
)

# Import ASCII definitions
from ui.ascii_definitions import ASCII_DEFS

# Import other modules
from ui.panels import (
    SlidingPanel, draw_status_panel, draw_inventory_panel,
    draw_action_prompt, draw_confirmation_box
)
from ui.menus import MenuManager
from entities.player import Player
from world.world import World
from game.camera import Camera
from game.events import EventHandler
from systems.character_creation import CharacterCreation
from systems.save_system import SaveSystem

# Import encounter system
from game.encounter_events import EncounterEventHandler
from systems.encounters import EncounterDisplay
from ui.encounter_ui import draw_encounter_screen, draw_encounter_options, draw_combat_screen, draw_combat_actions, draw_combat_help

class Game:
    """Main game class that manages all game states with visual effects."""
    
    def __init__(self):
        pygame.init()
        
        # Initialize fonts
        try:
            if FONT_NAME:
                self.ui_font = pygame.font.Font(FONT_NAME, FONT_SIZE)
                self.tile_font = pygame.font.Font(FONT_NAME, TILE_FONT_SIZE)
            else:
                raise FileNotFoundError
        except FileNotFoundError:
            self.ui_font = pygame.font.SysFont('monospace', FONT_SIZE, bold=True)
            self.tile_font = pygame.font.SysFont('monospace', TILE_FONT_SIZE, bold=True)
        
        # Initialize display
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.world_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("ASCII RPG")
        self.clock = pygame.time.Clock()
        
        # Game state
        self.state = 'menu'  # menu, character_creation, playing, encounter, combat
        self.running = True
        
        # Initialize systems
        self.menu_manager = MenuManager(self.ui_font)
        self.character_creation = None
        self.event_handler = EventHandler()
        self.encounter_handler = EncounterEventHandler()
        
        # Encounter and combat state
        self.current_encounter = None
        self.combat_phase = None
        
        # Game objects (initialized when starting new game)
        self.world = None
        self.player = None
        self.camera = None
        self.status_panel = None
        self.inventory_panel = None
        
        # Game state variables
        self.game_state = 'playing'
        self.ui_focus = 'world'
        self.ui_cursor = 0
        self.pending_action = None
        self.look_cursor_pos = [0, 0]
        
        # Visual effects
        self.spell_effects = []  # List of active spell effects

    def run(self):
        """Main game loop."""
        while self.running:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(60)
        
        pygame.quit()

    def add_spell_effect(self, x, y, effect_type, duration=1000):
        """Add a spell effect at the given coordinates."""
        if self.world and self.player:
            # Add effect to world tile
            self.world.add_spell_effect(x, y, self.player.location, effect_type)
            
            # Add to our tracking list
            self.spell_effects.append({
                'x': x, 'y': y, 'type': effect_type,
                'start_time': pygame.time.get_ticks(),
                'duration': duration
            })

    def add_entity_effect(self, entity, effect_type):
        """Add a visual effect to an entity (player or monster)."""
        if hasattr(entity, 'add_visual_effect'):
            entity.add_visual_effect(effect_type)

    def cast_spell(self, spell_type, target_x, target_y):
        """Cast a spell with visual effects."""
        if spell_type == 'fireball':
            # Add fire effect to target area
            for dx in range(-1, 2):
                for dy in range(-1, 2):
                    fx, fy = target_x + dx, target_y + dy
                    if 0 <= fx < self.world.width and 0 <= fy < self.world.height:
                        self.add_spell_effect(fx, fy, 'fire', 2000)
        
        elif spell_type == 'magic_missile':
            # Add magic missile effect
            self.add_spell_effect(target_x, target_y, 'magic_missile', 500)
        
        elif spell_type == 'heal':
            # Add healing effect to player
            self.add_spell_effect(self.player.x, self.player.y, 'healing', 1000)
            self.add_entity_effect(self.player, 'blessed')

    def handle_events(self):
        """Handle all events based on current state."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                continue
            
            if self.state == 'menu':
                self.handle_menu_events(event)
            elif self.state == 'character_creation':
                self.handle_character_creation_events(event)
            elif self.state == 'playing':
                self.handle_playing_events(event)
            elif self.state == 'encounter':
                self.handle_encounter_events(event)
            elif self.state == 'combat':
                self.handle_combat_events(event)

    def handle_encounter_events(self, event):
        """Handle encounter events."""
        try:
            result = self.encounter_handler.handle_encounter_input(
                event, self.current_encounter, self.player)
            
            if result:
                if result['action'] == 'continue_encounter':
                    self.current_encounter = result['encounter']
                elif result['action'] == 'start_combat':
                    self.start_combat()
                elif result['action'] == 'evasion_success':
                    self.state = 'playing'
                    self.current_encounter = None
                elif result['action'] == 'evasion_failed':
                    self.current_encounter = result['encounter']
                    self.start_combat()
        except Exception as e:
            # Fallback to playing state on error
            self.state = 'playing'
            self.current_encounter = None

    def handle_combat_events(self, event):
        """Handle combat events."""
        try:
            alive_monsters = [m for m in self.current_encounter['monsters'] if m.is_alive]
            
            result = self.encounter_handler.handle_combat_input(
                event, self.player, alive_monsters, self.combat_phase)
            
            if result:
                if result['action'] == 'spells_declared':
                    self.combat_phase = 'player_turn'
                elif result['action'] == 'player_attack':
                    self.process_player_attack(result)
                elif result['action'] == 'monster_turn':
                    self.process_monster_turn()
                elif result['action'] == 'player_move':
                    self.combat_phase = 'monster_turn'
                elif result['action'] == 'player_wait':
                    self.combat_phase = 'monster_turn'
                elif result['action'] == 'attempt_retreat':
                    self.attempt_combat_retreat()
        except Exception as e:
            # Fallback to playing state on error
            self.state = 'playing'
            self.current_encounter = None
            self.combat_phase = None

    def start_combat(self):
        """Start combat with current encounter monsters."""
        try:
            self.state = 'combat'
            alive_monsters = [m for m in self.current_encounter['monsters'] if m.is_alive]
            combat_info = self.encounter_handler.combat_manager.start_combat(self.player, alive_monsters)
            self.combat_phase = 'declare_spells'
        except Exception as e:
            self.state = 'playing'
            self.current_encounter = None

    def process_player_attack(self, attack_result):
        """Process the result of a player attack."""
        try:
            # Check if combat should end
            alive_monsters = [m for m in self.current_encounter['monsters'] if m.is_alive]
            combat_check = self.encounter_handler.combat_manager.check_combat_end(self.player, alive_monsters)
            
            if combat_check['ended']:
                self.end_combat(combat_check['result'])
            else:
                self.combat_phase = 'monster_turn'
        except Exception as e:
            self.state = 'playing'
            self.current_encounter = None

    def process_monster_turn(self):
        """Process monster turn in combat."""
        try:
            alive_monsters = [m for m in self.current_encounter['monsters'] if m.is_alive]
            monster_results = self.encounter_handler.combat_manager.execute_monster_turn(
                alive_monsters, self.player)
            
            # Check if combat should end
            combat_check = self.encounter_handler.combat_manager.check_combat_end(self.player, alive_monsters)
            
            if combat_check['ended']:
                self.end_combat(combat_check['result'])
            else:
                # Start new round
                combat_info = self.encounter_handler.combat_manager.start_new_round(
                    self.player, alive_monsters)
                self.combat_phase = 'declare_spells'
        except Exception as e:
            self.state = 'playing'
            self.current_encounter = None

    def end_combat(self, result):
        """End combat and return to playing state."""
        try:
            if result == 'player_victory':
                # Award XP
                defeated_monsters = [m for m in self.current_encounter['monsters'] if not m.is_alive]
                xp_gained = self.encounter_handler.combat_manager.award_experience(
                    self.player, defeated_monsters)
            
            self.state = 'playing'
            self.current_encounter = None
            self.combat_phase = None
        except Exception as e:
            self.state = 'playing'
            self.current_encounter = None
            self.combat_phase = None

    def attempt_combat_retreat(self):
        """Attempt to retreat from combat."""
        try:
            retreat_result = self.encounter_handler.attempt_combat_evasion(self.current_encounter)
            
            if retreat_result['action'] == 'combat_evasion_success':
                self.state = 'playing'
                self.current_encounter = None
                self.combat_phase = None
        except Exception as e:
            self.state = 'playing'
            self.current_encounter = None

    def handle_menu_events(self, event):
        """Handle menu events."""
        result = self.menu_manager.handle_input(event)
        if result:
            action = result['action']
            if action == 'quit':
                self.running = False
            elif action == 'start_character_creation':
                self.start_character_creation()
            elif action == 'load_game':
                self.load_game(result['slot'])

    def handle_character_creation_events(self, event):
        """Handle character creation events."""
        try:
            result = self.character_creation.handle_input(event)
            
            if result:
                if result == 'back_to_menu':
                    self.state = 'menu'
                    self.character_creation = None
                elif isinstance(result, dict) and result.get('action') == 'character_created':
                    self.character_creation = None
                    self.start_new_game(result['character'])
        except Exception as e:
            self.state = 'menu'
            self.character_creation = None

    def handle_playing_events(self, event):
        """Handle in-game events with spell casting support."""
        # Check if any panels are open
        is_panel_open = (self.status_panel.state != 'CLOSED' or 
                        self.inventory_panel.state != 'CLOSED')
        
        # Handle different game states
        if self.game_state == 'looking':
            self.game_state = self.event_handler.handle_looking_mode(
                event, self.look_cursor_pos, self.game_state)
        
        elif self.game_state in ['equip_prompt', 'unequip_prompt']:
            self.game_state, self.pending_action = self.event_handler.handle_prompt_mode(
                event, self.game_state, self.pending_action)
        
        elif self.game_state == 'item_prompt':
            self.game_state = self.event_handler.handle_item_prompt(
                event, self.world, self.player)
        
        else:  # Main game state
            # Handle spell casting (demo keys)
            if event.type == pygame.KEYDOWN and not is_panel_open:
                if event.key == pygame.K_1:  # Fireball
                    self.cast_spell('fireball', self.player.x, self.player.y)
                elif event.key == pygame.K_2:  # Magic Missile
                    self.cast_spell('magic_missile', self.player.x + 1, self.player.y)
                elif event.key == pygame.K_3:  # Heal
                    self.cast_spell('heal', self.player.x, self.player.y)
                elif event.key == pygame.K_4:  # Smoke (demo)
                    self.add_spell_effect(self.player.x, self.player.y, 'smoke', 3000)
            
            # Handle main game input
            result = self.event_handler.handle_main_game_input(
                event, self.player, self.world, self.status_panel, self.inventory_panel)
            
            if result.get('quit'):
                self.state = 'menu'
                return
            
            if result.get('game_state'):
                self.game_state = result['game_state']
                if 'look_cursor_pos' in result:
                    self.look_cursor_pos = result['look_cursor_pos']
            
            # Handle save game (S key)
            if event.type == pygame.KEYDOWN and event.key == pygame.K_s and not is_panel_open:
                self.quick_save()
            
            # Handle panel navigation
            if is_panel_open:
                self.ui_focus, self.ui_cursor, new_game_state, new_pending_action = \
                    self.event_handler.handle_panel_navigation(
                        event, self.ui_focus, self.ui_cursor, self.player)
                
                if new_game_state:
                    self.game_state = new_game_state
                    self.pending_action = new_pending_action

    def update(self):
        """Update game logic based on current state."""
        if self.state == 'playing':
            self.update_playing()
        
        # Update world tile effects
        if self.world:
            self.world.update_tile_effects()
        
        # Clean up expired spell effects
        current_time = pygame.time.get_ticks()
        self.spell_effects = [
            effect for effect in self.spell_effects
            if current_time - effect['start_time'] < effect['duration']
        ]

    def update_playing(self):
        """Update playing state."""
        # Check if any panels are open
        is_panel_open = (self.status_panel.state != 'CLOSED' or 
                        self.inventory_panel.state != 'CLOSED')
        
        if self.game_state == 'playing' and not is_panel_open:
            # Handle movement
            moved = self.event_handler.handle_movement(self.player, self.world)
            
            # Check for random encounters when moving
            if moved and self.encounter_handler:
                try:
                    current_time = pygame.time.get_ticks()
                    encounter = self.encounter_handler.check_for_encounter(
                        self.player, self.world, current_time)
                    
                    if encounter:
                        self.current_encounter = encounter
                        self.state = 'encounter'
                        return
                        
                except Exception as e:
                    pass
            
            # Check for treasure chest interaction
            for chest in self.world.treasure_chests:
                if (self.player.x, self.player.y) == chest['pos']:
                    self.game_state = 'item_prompt'
                    break

        # Update UI Focus
        if self.status_panel.state != 'CLOSED':
            if self.status_panel.state == 'OPEN' and self.ui_focus != 'status':
                self.ui_focus = 'status'
        
        if self.inventory_panel.state != 'CLOSED':
            if self.inventory_panel.state == 'OPEN':
                if self.ui_focus not in ['equipment', 'inventory']:
                    self.ui_focus = 'inventory'
        
        if not is_panel_open:
            self.ui_focus = 'world'

    def draw(self):
        """Draw everything based on current state."""
        try:
            if self.state == 'menu':
                self.menu_manager.draw(self.screen)
            elif self.state == 'character_creation':
                if self.character_creation:
                    self.character_creation.draw(self.screen)
                else:
                    self.state = 'menu'
            elif self.state == 'playing':
                self.draw_playing()
            elif self.state == 'encounter':
                self.draw_encounter()
            elif self.state == 'combat':
                self.draw_combat()
            
            pygame.display.flip()
        except Exception as e:
            pygame.display.flip()

    def draw_encounter(self):
        """Draw encounter screen."""
        try:
            draw_encounter_screen(self.screen, self.ui_font, self.current_encounter, 
                                 EncounterDisplay())
            
            options = EncounterDisplay.get_encounter_options(self.current_encounter)
            draw_encounter_options(self.screen, self.ui_font, options, 
                                 self.encounter_handler.selected_option)
        except Exception as e:
            # Fallback to simple encounter display
            self.screen.fill(C_BACKGROUND)
            text = "ENCOUNTER! Press ESC to flee."
            text_surf = self.ui_font.render(text, True, C_TEXT)
            text_rect = text_surf.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2))
            self.screen.blit(text_surf, text_rect)

    def draw_combat(self):
        """Draw combat screen."""
        try:
            alive_monsters = [m for m in self.current_encounter['monsters'] if m.is_alive]
            draw_combat_screen(self.screen, self.ui_font, self.player, alive_monsters,
                             self.encounter_handler.combat_manager, 
                             self.encounter_handler.selected_action)
            
            if self.combat_phase == 'player_turn':
                actions = self.encounter_handler.combat_manager.get_available_actions(
                    self.player, alive_monsters, 'player_turn')
                draw_combat_actions(self.screen, self.ui_font, actions,
                                  self.encounter_handler.selected_action)
            
            draw_combat_help(self.screen, self.ui_font)
        except Exception as e:
            # Fallback to simple combat display
            self.screen.fill(C_BACKGROUND)
            text = "COMBAT! Press ESC to attempt retreat."
            text_surf = self.ui_font.render(text, True, C_TEXT)
            text_rect = text_surf.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2))
            self.screen.blit(text_surf, text_rect)

    def draw_playing(self):
        """Draw the playing state with enhanced visuals."""
        self.screen.fill(C_BACKGROUND)
        
        # Update camera
        self.camera.update(self.player)
        
        # Draw world (now with enhanced ASCII and effects)
        self.world_surface.fill(C_BACKGROUND)
        self.world.draw(self.world_surface, self.tile_font, self.camera, self.player.location)
        
        # Draw player with effects
        player_screen_x = (self.player.x - self.camera.x) * TILE_SIZE
        player_screen_y = (self.player.y - self.camera.y) * TILE_SIZE
        
        player_render = self.player.get_render_info()
        player_surface = self.tile_font.render(player_render['char'], True, player_render['color'])
        self.world_surface.blit(player_surface, (player_screen_x, player_screen_y))
        
        # Draw look cursor
        if self.game_state == 'looking':
            cursor_screen_x = (self.look_cursor_pos[0] - self.camera.x) * TILE_SIZE
            cursor_screen_y = (self.look_cursor_pos[1] - self.camera.y) * TILE_SIZE
            if (pygame.time.get_ticks() // 400) % 2 == 0:
                cursor_surf = self.tile_font.render('X', True, C_CURSOR)
                self.world_surface.blit(cursor_surf, (cursor_screen_x, cursor_screen_y))

        self.screen.blit(self.world_surface, (0, 0))

        # Update and draw panels
        self.status_panel.update()
        self.inventory_panel.update()

        if self.status_panel.state != 'CLOSED':
            draw_status_panel(self.status_panel.surface, self.player, self.ui_font)
            self.status_panel.draw(self.screen)
        
        if self.inventory_panel.state != 'CLOSED':
            draw_inventory_panel(self.inventory_panel.surface, self.player, 
                               self.ui_font, self.ui_focus, self.ui_cursor)
            self.inventory_panel.draw(self.screen)

        # Draw prompts and dialogs
        action_prompt_text = self.world.get_action_prompt(
            self.player.x, self.player.y, self.player.location)
        if self.game_state == 'item_prompt' and action_prompt_text:
            draw_action_prompt(self.screen, action_prompt_text, self.ui_font)
        elif self.game_state == 'looking':
            look_desc = self.world.get_description(
                self.look_cursor_pos[0], self.look_cursor_pos[1], self.player.location)
            draw_action_prompt(self.screen, look_desc, self.ui_font)
        
        # Draw spell casting help
        if self.game_state == 'playing':
            help_text = "Spells: 1-Fireball 2-Magic Missile 3-Heal 4-Smoke"
            help_surf = self.ui_font.render(help_text, True, C_TEXT_DIM)
            self.screen.blit(help_surf, (10, SCREEN_HEIGHT - 30))
        
        if self.game_state == 'equip_prompt':
            if self.player.character.inventory:
                item_name = self.player.character.inventory[self.ui_cursor].name
                draw_confirmation_box(self.screen, f"Equip {item_name}? (Y/N)", self.ui_font)
        elif self.game_state == 'unequip_prompt':
            slot = list(self.player.character.equipped.keys())[self.ui_cursor]
            if self.player.character.equipped[slot]:
                item_name = self.player.character.equipped[slot].name
                draw_confirmation_box(self.screen, f"Unequip {item_name}? (Y/N)", self.ui_font)

    def start_character_creation(self):
        """Start the character creation process."""
        self.character_creation = CharacterCreation(self.ui_font)
        self.state = 'character_creation'

    def start_new_game(self, character):
        """Start a new game with the created character."""
        try:
            # Initialize game objects
            self.world = World(WORLD_WIDTH, WORLD_HEIGHT)
            self.player = Player(self.world.start_pos[0], self.world.start_pos[1])
            self.player.character = character
            self.camera = Camera(SCREEN_WIDTH, SCREEN_HEIGHT)
            
            # Initialize UI panels
            self.status_panel = SlidingPanel(STATUS_PANEL_WIDTH, SCREEN_HEIGHT, 'left')
            self.inventory_panel = SlidingPanel(INVENTORY_PANEL_WIDTH, SCREEN_HEIGHT, 'right')

            # Reset game state variables
            self.game_state = 'playing'
            self.ui_focus = 'world'
            self.ui_cursor = 0
            self.pending_action = None
            self.look_cursor_pos = [0, 0]

            self.state = 'playing'
            
        except Exception as e:
            self.state = 'menu'
            self.character_creation = None

    def load_game(self, slot):
        """Load a game from the specified slot."""
        save_data = SaveSystem.load_game(slot)
        if save_data:
            try:
                # Initialize world
                self.world = World(WORLD_WIDTH, WORLD_HEIGHT)
                
                # Restore treasure chests
                if 'treasure_chests' in save_data['world_data']:
                    self.world.treasure_chests = []
                    for chest_data in save_data['world_data']['treasure_chests']:
                        self.world.treasure_chests.append({
                            'pos': tuple(chest_data['pos']),
                            'item': SaveSystem._deserialize_item(chest_data['item'])
                        })
                
                # Set player
                self.player = save_data['player']
                self.camera = Camera(SCREEN_WIDTH, SCREEN_HEIGHT)
                
                # Initialize UI panels
                self.status_panel = SlidingPanel(STATUS_PANEL_WIDTH, SCREEN_HEIGHT, 'left')
                self.inventory_panel = SlidingPanel(INVENTORY_PANEL_WIDTH, SCREEN_HEIGHT, 'right')

                # Reset game state variables
                self.game_state = 'playing'
                self.ui_focus = 'world'
                self.ui_cursor = 0
                self.pending_action = None
                self.look_cursor_pos = [0, 0]

                self.state = 'playing'
            except Exception as e:
                pass  # Return to menu on error

    def quick_save(self):
        """Quick save to slot 1."""
        if self.player and self.world:
            SaveSystem.save_game(self.player, self.world, slot=1)

def main():
    game = Game()
    game.run()

if __name__ == '__main__':
    main()