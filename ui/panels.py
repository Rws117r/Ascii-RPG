# ui/panels.py
"""
UI panel classes and drawing functions for the ASCII RPG game.
"""
import pygame
import textwrap
from config import SCREEN_WIDTH, ANIMATION_SPEED
from ui.colors import *

class SlidingPanel:
    """Manages a panel that slides in and out from the side of the screen."""
    def __init__(self, width, height, side):
        self.rect = pygame.Rect(0, 0, width, height)
        self.surface = pygame.Surface((width, height))
        self.side = side
        self.state = 'CLOSED'  # CLOSED, OPENING, OPEN, CLOSING
        self.animation_progress = 0.0

        if side == 'left':
            self.rect.topleft = (-width, 0)
            self.open_pos = 0
            self.closed_pos = -width
        else:  # right
            self.rect.topleft = (SCREEN_WIDTH, 0)
            self.open_pos = SCREEN_WIDTH - width
            self.closed_pos = SCREEN_WIDTH

    def toggle(self):
        if self.state in ['CLOSED', 'CLOSING']:
            self.state = 'OPENING'
        elif self.state in ['OPEN', 'OPENING']:
            self.state = 'CLOSING'

    def update(self):
        if self.state == 'OPENING':
            if self.side == 'left':
                self.rect.x = min(self.open_pos, self.rect.x + ANIMATION_SPEED)
                if self.rect.x == self.open_pos:
                    self.state = 'OPEN'
            else:  # right
                self.rect.x = max(self.open_pos, self.rect.x - ANIMATION_SPEED)
                if self.rect.x == self.open_pos:
                    self.state = 'OPEN'
        elif self.state == 'CLOSING':
            if self.side == 'left':
                self.rect.x = max(self.closed_pos, self.rect.x - ANIMATION_SPEED)
                if self.rect.x == self.closed_pos:
                    self.state = 'CLOSED'
            else:  # right
                self.rect.x = min(self.closed_pos, self.rect.x + ANIMATION_SPEED)
                if self.rect.x == self.closed_pos:
                    self.state = 'CLOSED'

    def draw(self, screen):
        if self.state != 'CLOSED':
            screen.blit(self.surface, self.rect)

def draw_panel_title(surface, text, rect, font):
    """Draw a panel title with decorative brackets."""
    title_text = f"[--- {text.upper()} ---]"
    text_surf = font.render(title_text, True, C_TEXT)
    surface.blit(text_surf, (rect.x, rect.y))

def draw_stat_bar(surface, rect, value, max_value, color):
    """Draw a stat bar with fill ratio."""
    bar_width = rect.width
    fill_ratio = value / max_value if max_value > 0 else 0
    fill_width = int(bar_width * fill_ratio)
    
    pygame.draw.rect(surface, C_TEXT_DIM, rect)
    pygame.draw.rect(surface, color, (rect.x, rect.y, fill_width, rect.height))
    pygame.draw.rect(surface, C_BORDER, rect, 1)

def draw_status_panel(surface, player, font):
    """Draw the character status panel."""
    surface.fill(C_PANEL_BG)
    pygame.draw.rect(surface, C_BORDER, surface.get_rect(), 1)
    
    # Title
    draw_panel_title(surface, "Status", pygame.Rect(10, 10, 0, 0), font)
    
    # Health
    y = 40
    hp_text = f"HP: {player.character.hp} / {player.character.max_hp}"
    surface.blit(font.render(hp_text, True, C_TEXT), (10, y))
    draw_stat_bar(surface, pygame.Rect(10, y + 25, 200, 10), 
                  player.character.hp, player.character.max_hp, C_TEXT)
    
    # Ability Scores
    y += 50
    draw_panel_title(surface, "Ability Scores", pygame.Rect(10, y, 0, 0), font)
    y += 30
    for score, value in player.character.ability_scores.items():
        mod = player.character.get_modifier(value)
        mod_str = f"({'+' if mod >= 0 else ''}{mod})"
        stat_text = f"{score.upper()}: {value} {mod_str}"
        surface.blit(font.render(stat_text, True, C_TEXT), (10, y))
        y += 25

    # Combat Stats
    y += 15
    draw_panel_title(surface, "Combat", pygame.Rect(10, y, 0, 0), font)
    y += 30
    surface.blit(font.render(f"THACO: {player.character.thac0}", True, C_TEXT), (10, y))
    
    # Saving Throws
    y += 40
    draw_panel_title(surface, "Saving Throws", pygame.Rect(10, y, 0, 0), font)
    y += 30
    for save, value in player.character.saving_throws.items():
        save_text = f"{save.title()}: {value}"
        surface.blit(font.render(save_text, True, C_TEXT), (10, y))
        y += 25

def get_short_slot_name(slot):
    """Converts a slot name to a shorter version for the UI."""
    words = slot.replace('_', ' ').split()
    if len(words) > 1:
        return f"{words[0][0].upper()}. {words[1].title()}:"
    else:
        return f"{words[0].title()}:"

def draw_inventory_panel(surface, player, font, focus, cursor_pos):
    """Draw the inventory and equipment panel."""
    surface.fill(C_PANEL_BG)
    pygame.draw.rect(surface, C_BORDER, surface.get_rect(), 1)

    # Equipment section
    equip_rect = pygame.Rect(10, 10, surface.get_width() - 20, 320)
    draw_panel_title(surface, "Equipment", equip_rect, font)
    y = 40
    equipment_slots = list(player.character.equipped.keys())
    
    col1_x = 10
    col2_x = 150  # Start of item name column
    
    for i, slot in enumerate(equipment_slots):
        item = player.character.equipped[slot]
        item_name = item.name if item else "---"
        
        prefix = "> " if focus == 'equipment' and i == cursor_pos else "  "
        slot_text = get_short_slot_name(slot)
        full_slot_text = f"{prefix}{slot_text}"
        
        color = C_CURSOR if focus == 'equipment' and i == cursor_pos else C_TEXT
        
        # Draw slot name
        slot_surf = font.render(full_slot_text, True, color)
        surface.blit(slot_surf, (col1_x, y))

        # Draw item name with text wrapping
        available_width = (equip_rect.x + equip_rect.width) - col2_x
        char_width = font.size('A')[0]
        max_chars = available_width // char_width if char_width > 0 else 1
        
        wrapped_lines = textwrap.wrap(item_name, width=max_chars) if max_chars > 0 else [item_name]
        
        line_y = y
        total_item_height = 0
        if not wrapped_lines:
            total_item_height = font.get_height()
        else:
            for line_idx, line in enumerate(wrapped_lines):
                item_surf = font.render(line, True, color)
                surface.blit(item_surf, (col2_x, line_y))
                line_y += font.get_height()
                total_item_height += font.get_height()
        
        y += max(slot_surf.get_height(), total_item_height)

    # Inventory section
    inv_rect = pygame.Rect(10, y + 10, surface.get_width() - 20, 200)
    draw_panel_title(surface, "Inventory", inv_rect, font)
    y += 40
    
    if not player.character.inventory:
        surface.blit(font.render("--- Empty ---", True, C_TEXT_DIM), (10, y))
    else:
        for i, item in enumerate(player.character.inventory):
            text = item.name
            color = C_CURSOR if focus == 'inventory' and i == cursor_pos else C_TEXT
            if focus == 'inventory' and i == cursor_pos:
                text = "> " + text
            surface.blit(font.render(text, True, color), (10, y))
            y += 25

def draw_action_prompt(screen, text, font):
    """Draws a small action prompt at the bottom of the screen."""
    from config import SCREEN_WIDTH, SCREEN_HEIGHT
    prompt_surf = font.render(text, True, C_TEXT, C_PANEL_BG)
    prompt_rect = prompt_surf.get_rect(centerx=SCREEN_WIDTH / 2, bottom=SCREEN_HEIGHT - 20)
    padding_rect = prompt_rect.inflate(20, 10)
    pygame.draw.rect(screen, C_PANEL_BG, padding_rect)
    pygame.draw.rect(screen, C_BORDER, padding_rect, 1)
    screen.blit(prompt_surf, prompt_rect)

def draw_confirmation_box(screen, text, font):
    """Draws a confirmation prompt in the center of the screen."""
    from config import SCREEN_WIDTH, SCREEN_HEIGHT
    width, height = 400, 100
    rect = pygame.Rect((SCREEN_WIDTH - width) / 2, (SCREEN_HEIGHT - height) / 2, width, height)
    pygame.draw.rect(screen, C_PANEL_BG, rect)
    pygame.draw.rect(screen, C_BORDER, rect, 1)
    draw_panel_title(screen, "Confirm", pygame.Rect(rect.x + 10, rect.y + 5, 0, 0), font)
    text_surf = font.render(text, True, C_TEXT)
    text_rect = text_surf.get_rect(center=rect.center)
    screen.blit(text_surf, text_rect)