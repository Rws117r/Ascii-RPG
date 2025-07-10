# game/events.py
"""
Event handling for the ASCII RPG game.
"""
import pygame
from config import MOVE_DELAY

class EventHandler:
    def __init__(self):
        self.last_move_time = 0
    
    def handle_looking_mode(self, event, look_cursor_pos, game_state):
        """Handle events while in looking mode."""
        if event.type == pygame.KEYDOWN:
            if event.key in [pygame.K_UP, pygame.K_w]:
                look_cursor_pos[1] -= 1
            elif event.key in [pygame.K_DOWN, pygame.K_s]:
                look_cursor_pos[1] += 1
            elif event.key in [pygame.K_LEFT, pygame.K_a]:
                look_cursor_pos[0] -= 1
            elif event.key in [pygame.K_RIGHT, pygame.K_d]:
                look_cursor_pos[0] += 1
            elif event.key in [pygame.K_l, pygame.K_ESCAPE]:
                return 'playing'
        return game_state
    
    def handle_prompt_mode(self, event, game_state, pending_action):
        """Handle events for prompt modes (equip/unequip/item)."""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_y:
                if pending_action:
                    pending_action()
                return 'playing', None
            else:
                return 'playing', None
        return game_state, pending_action
    
    def handle_item_prompt(self, event, world, player):
        """Handle item pickup prompts."""
        if event.type == pygame.KEYDOWN:
            chest = next((c for c in world.treasure_chests if c['pos'] == (player.x, player.y)), None)
            if event.key == pygame.K_y and chest:
                player.add_to_inventory(chest['item'])
                world.dungeon_tiles[chest['pos'][1]][chest['pos'][0]] = '.'
                world.treasure_chests.remove(chest)
            return 'playing'
        return 'item_prompt'
    
    def handle_panel_navigation(self, event, ui_focus, ui_cursor, player):
        """Handle navigation within UI panels."""
        new_cursor = ui_cursor
        new_focus = ui_focus
        
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                new_cursor = max(0, ui_cursor - 1)
            elif event.key == pygame.K_DOWN:
                if ui_focus == 'inventory':
                    new_cursor = min(len(player.character.inventory) - 1, ui_cursor + 1)
                else:
                    new_cursor = min(len(player.character.equipped) - 1, ui_cursor + 1)
            elif event.key == pygame.K_LEFT or event.key == pygame.K_RIGHT:
                new_focus = 'equipment' if ui_focus == 'inventory' else 'inventory'
                new_cursor = 0
            elif event.key == pygame.K_RETURN:
                return self._handle_panel_action(ui_focus, ui_cursor, player)
        
        return new_focus, new_cursor, None, None
    
    def _handle_panel_action(self, ui_focus, ui_cursor, player):
        """Handle action selection in panels."""
        if ui_focus == 'inventory' and player.character.inventory:
            return 'inventory', ui_cursor, 'equip_prompt', lambda c=ui_cursor: player.equip(c)
        elif ui_focus == 'equipment':
            slot = list(player.character.equipped.keys())[ui_cursor]
            if player.character.equipped[slot]:
                return 'equipment', ui_cursor, 'unequip_prompt', lambda s=slot: player.unequip(s)
        return ui_focus, ui_cursor, None, None
    
    def handle_main_game_input(self, event, player, world, status_panel, inventory_panel):
        """Handle input during main gameplay."""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                return {'quit': True}
            if event.key == pygame.K_l:
                return {'game_state': 'looking', 'look_cursor_pos': [player.x, player.y]}
            if event.key == pygame.K_c:
                status_panel.toggle()
                if status_panel.state == 'OPENING':
                    inventory_panel.state = 'CLOSING'
            if event.key == pygame.K_i:
                inventory_panel.toggle()
                if inventory_panel.state == 'OPENING':
                    status_panel.state = 'CLOSING'
        
        return {}
    
    def handle_movement(self, player, world):
        """Handle player movement input."""
        keys = pygame.key.get_pressed()
        current_time = pygame.time.get_ticks()
        
        if current_time - self.last_move_time > MOVE_DELAY:
            dx, dy = 0, 0
            
            if keys[pygame.K_UP] or keys[pygame.K_w]:
                dy = -1
            elif keys[pygame.K_DOWN] or keys[pygame.K_s]:
                dy = 1
            elif keys[pygame.K_LEFT] or keys[pygame.K_a]:
                dx = -1
            elif keys[pygame.K_RIGHT] or keys[pygame.K_d]:
                dx = 1
            
            if dx != 0 or dy != 0:
                player.move(dx, dy, world)
                self.last_move_time = current_time
                return True
        
        return False