# ui/encounter_ui.py
"""
UI components for encounters and combat.
"""
import pygame
import textwrap

# Import from the correct locations
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import SCREEN_WIDTH, SCREEN_HEIGHT
from ui.colors import *
from systems.encounters import EncounterManager

def draw_encounter_screen(screen, font, encounter, encounter_display):
    """Draw the encounter screen."""
    screen.fill(C_BACKGROUND)
    
    # Title
    title = "ENCOUNTER!"
    title_surf = font.render(title, True, C_GOLD)
    title_rect = title_surf.get_rect(centerx=SCREEN_WIDTH // 2, y=30)
    screen.blit(title_surf, title_rect)
    
    # Encounter description
    description = encounter_display.get_encounter_description(encounter)
    wrapped_desc = textwrap.wrap(description, width=60)
    
    y = 100
    for line in wrapped_desc:
        desc_surf = font.render(line, True, C_TEXT)
        desc_rect = desc_surf.get_rect(centerx=SCREEN_WIDTH // 2, y=y)
        screen.blit(desc_surf, desc_rect)
        y += 30
    
    # Monster list
    y += 20
    monsters_title = "Monsters encountered:"
    monsters_surf = font.render(monsters_title, True, C_TEXT_DIM)
    monsters_rect = monsters_surf.get_rect(centerx=SCREEN_WIDTH // 2, y=y)
    screen.blit(monsters_surf, monsters_rect)
    
    y += 30
    monster_counts = {}
    for monster in encounter['monsters']:
        if monster.name in monster_counts:
            monster_counts[monster.name] += 1
        else:
            monster_counts[monster.name] = 1
    
    for monster_name, count in monster_counts.items():
        if count == 1:
            monster_text = f"  {monster_name}"
        else:
            monster_text = f"  {count} {monster_name}s"
        
        monster_surf = font.render(monster_text, True, C_TEXT)
        monster_rect = monster_surf.get_rect(centerx=SCREEN_WIDTH // 2, y=y)
        screen.blit(monster_surf, monster_rect)
        y += 25
    
    # Show distance
    y += 20
    distance_text = f"Distance: {encounter['distance']} yards"
    distance_surf = font.render(distance_text, True, C_TEXT_DIM)
    distance_rect = distance_surf.get_rect(centerx=SCREEN_WIDTH // 2, y=y)
    screen.blit(distance_surf, distance_rect)
    
    # Show surprise status if checked
    if encounter['surprise_checked']:
        y += 30
        if encounter['player_surprised'] and encounter['monsters_surprised']:
            surprise_text = "Both sides are surprised!"
        elif encounter['player_surprised']:
            surprise_text = "You are surprised!"
        elif encounter['monsters_surprised']:
            surprise_text = "The monsters are surprised!"
        else:
            surprise_text = "No surprise."
        
        surprise_surf = font.render(surprise_text, True, C_CURSOR)
        surprise_rect = surprise_surf.get_rect(centerx=SCREEN_WIDTH // 2, y=y)
        screen.blit(surprise_surf, surprise_rect)
    
    # Show reaction if rolled
    if encounter['reaction_rolled']:
        y += 30
        reaction_desc = EncounterManager().get_reaction_description(encounter['reaction'])
        wrapped_reaction = textwrap.wrap(reaction_desc, width=50)
        
        for line in wrapped_reaction:
            reaction_surf = font.render(line, True, C_GOLD)
            reaction_rect = reaction_surf.get_rect(centerx=SCREEN_WIDTH // 2, y=y)
            screen.blit(reaction_surf, reaction_rect)
            y += 25

def draw_encounter_options(screen, font, options, selected_index):
    """Draw encounter options menu."""
    y = SCREEN_HEIGHT - 200
    
    options_title = "Choose your action:"
    title_surf = font.render(options_title, True, C_TEXT)
    title_rect = title_surf.get_rect(centerx=SCREEN_WIDTH // 2, y=y)
    screen.blit(title_surf, title_rect)
    
    y += 40
    for i, option in enumerate(options):
        color = C_CURSOR if i == selected_index else C_TEXT
        prefix = "> " if i == selected_index else "  "
        option_text = f"{prefix}{option}"
        
        option_surf = font.render(option_text, True, color)
        option_rect = option_surf.get_rect(centerx=SCREEN_WIDTH // 2, y=y)
        screen.blit(option_surf, option_rect)
        y += 30

def draw_combat_screen(screen, font, player, monsters, combat_manager, selected_action=0):
    """Draw the combat screen."""
    screen.fill(C_BACKGROUND)
    
    # Title
    title = f"COMBAT - Round {combat_manager.current_round}"
    title_surf = font.render(title, True, C_GOLD)
    title_rect = title_surf.get_rect(centerx=SCREEN_WIDTH // 2, y=20)
    screen.blit(title_surf, title_rect)
    
    # Player status
    y = 70
    player_title = f"{player.character.name} (Level {player.character.level} {player.character.char_class})"
    player_surf = font.render(player_title, True, C_PLAYER)
    player_rect = player_surf.get_rect(x=50, y=y)
    screen.blit(player_surf, player_rect)
    
    y += 30
    hp_text = f"HP: {player.character.hp}/{player.character.max_hp}"
    hp_color = C_TEXT if player.character.hp > player.character.max_hp // 2 else C_GOLD
    if player.character.hp <= player.character.max_hp // 4:
        hp_color = C_CURSOR  # Red-ish for critical health
    
    hp_surf = font.render(hp_text, True, hp_color)
    screen.blit(hp_surf, (50, y))
    
    ac_text = f"AC: {combat_manager.calculate_player_ac(player)}"
    ac_surf = font.render(ac_text, True, C_TEXT)
    screen.blit(ac_surf, (200, y))
    
    # Monster status
    y += 50
    monsters_title = "Monsters:"
    monsters_surf = font.render(monsters_title, True, C_TEXT)
    screen.blit(monsters_surf, (50, y))
    
    y += 30
    alive_monsters = [m for m in monsters if m.is_alive]
    for i, monster in enumerate(alive_monsters[:6]):  # Show up to 6 monsters
        status_text = f"{monster.name}: {monster.hp}/{monster.max_hp} HP"
        color = C_TEXT if monster.hp > monster.max_hp // 2 else C_TEXT_DIM
        
        monster_surf = font.render(status_text, True, color)
        screen.blit(monster_surf, (70, y))
        y += 25
    
    if len(alive_monsters) > 6:
        more_text = f"... and {len(alive_monsters) - 6} more"
        more_surf = font.render(more_text, True, C_TEXT_DIM)
        screen.blit(more_surf, (70, y))
    
    # Combat log (last 8 entries)
    log_y = 350
    log_title = "Combat Log:"
    log_surf = font.render(log_title, True, C_TEXT)
    screen.blit(log_surf, (50, log_y))
    
    log_y += 30
    recent_log = combat_manager.combat_log[-8:] if len(combat_manager.combat_log) > 8 else combat_manager.combat_log
    
    for entry in recent_log:
        if len(entry) > 70:  # Wrap long entries
            wrapped = textwrap.wrap(entry, width=70)
            for line in wrapped:
                log_entry_surf = font.render(line, True, C_TEXT_DIM)
                screen.blit(log_entry_surf, (70, log_y))
                log_y += 20
        else:
            log_entry_surf = font.render(entry, True, C_TEXT_DIM)
            screen.blit(log_entry_surf, (70, log_y))
            log_y += 20

def draw_combat_actions(screen, font, actions, selected_index):
    """Draw available combat actions."""
    # Draw in bottom right corner
    x = SCREEN_WIDTH - 300
    y = SCREEN_HEIGHT - 200
    
    actions_title = "Actions:"
    title_surf = font.render(actions_title, True, C_TEXT)
    screen.blit(title_surf, (x, y))
    
    y += 30
    for i, action in enumerate(actions):
        color = C_CURSOR if i == selected_index else C_TEXT
        prefix = "> " if i == selected_index else "  "
        action_text = f"{prefix}{action}"
        
        action_surf = font.render(action_text, True, color)
        screen.blit(action_surf, (x, y))
        y += 25

def draw_combat_help(screen, font):
    """Draw combat help text."""
    help_text = [
        "ENTER - Confirm action",
        "UP/DOWN - Select action",
        "ESC - Cancel (if possible)"
    ]
    
    x = SCREEN_WIDTH - 300
    y = 50
    
    help_title = "Controls:"
    title_surf = font.render(help_title, True, C_TEXT_DIM)
    screen.blit(title_surf, (x, y))
    
    y += 25
    for line in help_text:
        help_surf = font.render(line, True, C_TEXT_DIM)
        screen.blit(help_surf, (x, y))
        y += 20

def draw_encounter_result(screen, font, result_text, options=None, selected_option=0):
    """Draw encounter result screen."""
    screen.fill(C_BACKGROUND)
    
    # Title
    title = "Encounter Result"
    title_surf = font.render(title, True, C_GOLD)
    title_rect = title_surf.get_rect(centerx=SCREEN_WIDTH // 2, y=100)
    screen.blit(title_surf, title_rect)
    
    # Result text
    y = 200
    wrapped_result = textwrap.wrap(result_text, width=60)
    
    for line in wrapped_result:
        result_surf = font.render(line, True, C_TEXT)
        result_rect = result_surf.get_rect(centerx=SCREEN_WIDTH // 2, y=y)
        screen.blit(result_surf, result_rect)
        y += 30
    
    # Options if provided
    if options:
        y += 50
        for i, option in enumerate(options):
            color = C_CURSOR if i == selected_option else C_TEXT
            prefix = "> " if i == selected_option else "  "
            option_text = f"{prefix}{option}"
            
            option_surf = font.render(option_text, True, color)
            option_rect = option_surf.get_rect(centerx=SCREEN_WIDTH // 2, y=y)
            screen.blit(option_surf, option_rect)
            y += 30

def draw_monster_info_panel(screen, font, monster):
    """Draw a small info panel for a monster."""
    panel_width = 250
    panel_height = 150
    x = SCREEN_WIDTH - panel_width - 20
    y = 20
    
    # Background
    panel_rect = pygame.Rect(x, y, panel_width, panel_height)
    pygame.draw.rect(screen, C_PANEL_BG, panel_rect)
    pygame.draw.rect(screen, C_BORDER, panel_rect, 2)
    
    # Monster name
    name_surf = font.render(monster.name, True, C_GOLD)
    screen.blit(name_surf, (x + 10, y + 10))
    
    # Stats
    info_y = y + 40
    stats = [
        f"AC: {monster.ac}",
        f"HP: {monster.hp}/{monster.max_hp}",
        f"THAC0: {monster.thac0}",
        f"Morale: {monster.morale}"
    ]
    
    for stat in stats:
        stat_surf = font.render(stat, True, C_TEXT)
        screen.blit(stat_surf, (x + 10, info_y))
        info_y += 20