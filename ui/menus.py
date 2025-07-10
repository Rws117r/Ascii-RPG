# ui/menus.py
"""
Menu systems for the ASCII RPG game.
"""
import pygame
import os
import json
from config import SCREEN_WIDTH, SCREEN_HEIGHT
from ui.colors import *

class Menu:
    """Base menu class."""
    def __init__(self, title, options):
        self.title = title
        self.options = options
        self.selected = 0
        self.active = True

    def handle_input(self, event):
        """Handle input for menu navigation."""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                self.selected = (self.selected - 1) % len(self.options)
            elif event.key == pygame.K_DOWN:
                self.selected = (self.selected + 1) % len(self.options)
            elif event.key == pygame.K_RETURN:
                return self.options[self.selected]['action']
        return None

    def draw(self, screen, font):
        """Draw the menu."""
        screen.fill(C_BACKGROUND)
        
        # Draw title
        title_surf = font.render(self.title, True, C_TEXT)
        title_rect = title_surf.get_rect(centerx=SCREEN_WIDTH // 2, y=150)
        screen.blit(title_surf, title_rect)
        
        # Draw options
        start_y = 250
        for i, option in enumerate(self.options):
            color = C_CURSOR if i == self.selected else C_TEXT
            prefix = "> " if i == self.selected else "  "
            option_text = f"{prefix}{option['text']}"
            option_surf = font.render(option_text, True, color)
            option_rect = option_surf.get_rect(centerx=SCREEN_WIDTH // 2, y=start_y + i * 40)
            screen.blit(option_surf, option_rect)

class TitleScreen:
    """Main title screen menu."""
    def __init__(self, font):
        self.font = font
        self.menu = Menu("ASCII RPG", [
            {'text': 'New Game', 'action': 'new_game'},
            {'text': 'Load Game', 'action': 'load_game'},
            {'text': 'Options', 'action': 'options'},
            {'text': 'Quit', 'action': 'quit'}
        ])

    def handle_input(self, event):
        return self.menu.handle_input(event)

    def draw(self, screen):
        self.menu.draw(screen, self.font)
        
        # Draw ASCII art or game logo
        logo_lines = [
            "    ___   _____ _____ _____ _____   _____  _____  _____ ",
            "   / _ \\ /  ___/  __ \\_   _|_   _| |  _  ||  _  ||  __ \\",
            "  / /_\\ \\\\ `--.| /  \\/ | |   | |   | |/' || |_| || |  \\/",
            "  |  _  | `--. \\ |     | |   | |   |  /| ||  _  || | __ ",
            "  | | | |/\\__/ / \\__/\\_| |_ _| |_  \\ |_/ /| | | || |_\\ \\",
            "  \\_| |_/\\____/ \\____/\\___/ \\___/   \\___/ \\_| |_/ \\____/"
        ]
        
        start_y = 50
        for i, line in enumerate(logo_lines):
            text_surf = self.font.render(line, True, C_GOLD)
            text_rect = text_surf.get_rect(centerx=SCREEN_WIDTH // 2, y=start_y + i * 20)
            screen.blit(text_surf, text_rect)

class LoadGameMenu:
    """Load game menu with save slots."""
    def __init__(self, font):
        self.font = font
        self.save_slots = self._load_save_info()
        self._build_menu()

    def _load_save_info(self):
        """Load information about save files."""
        slots = []
        for i in range(3):
            save_file = f"save_slot_{i+1}.json"
            if os.path.exists(save_file):
                try:
                    with open(save_file, 'r') as f:
                        data = json.load(f)
                        slots.append({
                            'exists': True,
                            'name': data.get('character_name', 'Unknown'),
                            'level': data.get('level', 1),
                            'location': data.get('location', 'Unknown'),
                            'file': save_file
                        })
                except:
                    slots.append({'exists': False, 'file': save_file})
            else:
                slots.append({'exists': False, 'file': save_file})
        return slots

    def _build_menu(self):
        """Build the menu options based on save slots."""
        options = []
        for i, slot in enumerate(self.save_slots):
            if slot['exists']:
                text = f"Slot {i+1}: {slot['name']} (Level {slot['level']})"
                action = f"load_slot_{i}"
            else:
                text = f"Slot {i+1}: Empty"
                action = f"empty_slot_{i}"
            options.append({'text': text, 'action': action})
        
        options.append({'text': 'Back', 'action': 'back'})
        self.menu = Menu("Load Game", options)

    def handle_input(self, event):
        return self.menu.handle_input(event)

    def draw(self, screen):
        self.menu.draw(screen, self.font)

class OptionsMenu:
    """Options/settings menu."""
    def __init__(self, font):
        self.font = font
        self.menu = Menu("Options", [
            {'text': 'Sound: ON', 'action': 'toggle_sound'},
            {'text': 'Fullscreen: OFF', 'action': 'toggle_fullscreen'},
            {'text': 'Controls', 'action': 'controls'},
            {'text': 'Back', 'action': 'back'}
        ])

    def handle_input(self, event):
        return self.menu.handle_input(event)

    def draw(self, screen):
        self.menu.draw(screen, self.font)

class ControlsMenu:
    """Controls information screen."""
    def __init__(self, font):
        self.font = font
        self.controls = [
            "MOVEMENT:",
            "  Arrow Keys / WASD - Move character",
            "",
            "INTERFACE:",
            "  C - Toggle character status panel",
            "  I - Toggle inventory panel",
            "  L - Look mode (examine tiles)",
            "  Enter - Confirm / Interact",
            "  Y/N - Yes/No prompts",
            "",
            "PANELS:",
            "  Arrow Keys - Navigate",
            "  Left/Right - Switch between equipment/inventory",
            "  Enter - Equip/Unequip items",
            "",
            "Press ESC to return to previous menu"
        ]

    def handle_input(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                return 'back'
        return None

    def draw(self, screen):
        screen.fill(C_BACKGROUND)
        
        # Title
        title_surf = self.font.render("CONTROLS", True, C_TEXT)
        title_rect = title_surf.get_rect(centerx=SCREEN_WIDTH // 2, y=50)
        screen.blit(title_surf, title_rect)
        
        # Controls list
        start_y = 120
        for i, line in enumerate(self.controls):
            if line.endswith(":"):
                color = C_GOLD
            elif line.startswith("  "):
                color = C_TEXT_DIM
            else:
                color = C_TEXT
            
            text_surf = self.font.render(line, True, color)
            text_rect = text_surf.get_rect(centerx=SCREEN_WIDTH // 2, y=start_y + i * 25)
            screen.blit(text_surf, text_rect)

class MenuManager:
    """Manages all menu states and transitions."""
    def __init__(self, font):
        self.font = font
        self.current_menu = 'title'
        self.menu_stack = []
        
        # Initialize all menus
        self.title_screen = TitleScreen(font)
        self.load_game_menu = LoadGameMenu(font)
        self.options_menu = OptionsMenu(font)
        self.controls_menu = ControlsMenu(font)

    def get_current_menu(self):
        """Get the current active menu."""
        if self.current_menu == 'title':
            return self.title_screen
        elif self.current_menu == 'load_game':
            return self.load_game_menu
        elif self.current_menu == 'options':
            return self.options_menu
        elif self.current_menu == 'controls':
            return self.controls_menu
        return None

    def handle_input(self, event):
        """Handle input for the current menu."""
        current = self.get_current_menu()
        if current:
            action = current.handle_input(event)
            return self._process_action(action)
        return None

    def _process_action(self, action):
        """Process menu actions and handle transitions."""
        if not action:
            return None

        if action == 'new_game':
            return {'action': 'start_character_creation'}
        elif action == 'quit':
            return {'action': 'quit'}
        elif action == 'load_game':
            self._push_menu('load_game')
        elif action == 'options':
            self._push_menu('options')
        elif action == 'controls':
            self._push_menu('controls')
        elif action == 'back':
            self._pop_menu()
        elif action.startswith('load_slot_'):
            slot_num = int(action.split('_')[-1])
            return {'action': 'load_game', 'slot': slot_num}
        elif action.startswith('empty_slot_'):
            # Could show a message or do nothing for empty slots
            pass
        elif action == 'toggle_sound':
            # TODO: Implement sound toggle
            pass
        elif action == 'toggle_fullscreen':
            # TODO: Implement fullscreen toggle
            pass

        return None

    def _push_menu(self, menu_name):
        """Push current menu to stack and switch to new menu."""
        self.menu_stack.append(self.current_menu)
        self.current_menu = menu_name

    def _pop_menu(self):
        """Pop menu from stack and return to previous menu."""
        if self.menu_stack:
            self.current_menu = self.menu_stack.pop()
        else:
            self.current_menu = 'title'

    def draw(self, screen):
        """Draw the current menu."""
        current = self.get_current_menu()
        if current:
            current.draw(screen)