# systems/character_creation.py
"""
Character creation system for the ASCII RPG game.
"""
import pygame
import random
from config import SCREEN_WIDTH, SCREEN_HEIGHT
from ui.colors import *
from entities.character import Character

class CharacterCreation:
    """Character creation screen and logic."""
    
    def __init__(self, font):
        self.font = font
        self.step = 'name'  # name, class, stats, confirm
        self.character_name = ""
        self.character_class = "Fighter"
        self.ability_scores = {}
        self.available_classes = [
            "Fighter", "Cleric", "Magic-User", "Thief", 
            "Ranger", "Paladin", "Druid"
        ]
        self.class_descriptions = {
            "Fighter": "Masters of combat and weapons. High HP and THAC0.",
            "Cleric": "Divine spellcasters and healers. Moderate combat ability.",
            "Magic-User": "Arcane spellcasters with powerful magic but weak in combat.",
            "Thief": "Stealthy rogues with special abilities. Moderate combat.",
            "Ranger": "Wilderness warriors with tracking and nature skills.",
            "Paladin": "Holy warriors combining combat with divine magic.",
            "Druid": "Nature priests with animal and elemental magic."
        }
        self.selected_class_index = 0
        self.input_active = True
        self.reroll_count = 0
        self.max_rerolls = 3
        self._generate_stats()

    def _generate_stats(self):
        """Generate random ability scores using 3d6."""
        self.ability_scores = {
            'str': self._roll_stat(),
            'dex': self._roll_stat(),
            'con': self._roll_stat(),
            'int': self._roll_stat(),
            'wis': self._roll_stat(),
            'cha': self._roll_stat()
        }

    def _roll_stat(self):
        """Roll 3d6 for an ability score."""
        return sum(random.randint(1, 6) for _ in range(3))

    def _get_stat_modifier(self, score):
        """Calculate ability score modifier."""
        if score <= 3: return -3
        if score <= 5: return -2
        if score <= 8: return -1
        if score <= 12: return 0
        if score <= 15: return 1
        if score <= 17: return 2
        return 3

    def _get_class_bonuses(self, char_class):
        """Get class-specific bonuses and requirements."""
        bonuses = {
            "Fighter": {"hp_bonus": 2, "thac0_bonus": -1, "primary": "str", "min_primary": 9},
            "Cleric": {"hp_bonus": 0, "thac0_bonus": 0, "primary": "wis", "min_primary": 9},
            "Magic-User": {"hp_bonus": -2, "thac0_bonus": 1, "primary": "int", "min_primary": 9},
            "Thief": {"hp_bonus": -1, "thac0_bonus": 0, "primary": "dex", "min_primary": 9},
            "Ranger": {"hp_bonus": 1, "thac0_bonus": -1, "primary": "str", "min_primary": 13, "secondary": "dex", "min_secondary": 13},
            "Paladin": {"hp_bonus": 1, "thac0_bonus": -1, "primary": "str", "min_primary": 12, "secondary": "cha", "min_secondary": 17},
            "Druid": {"hp_bonus": 0, "thac0_bonus": 0, "primary": "wis", "min_primary": 12, "secondary": "cha", "min_secondary": 15}
        }
        return bonuses.get(char_class, {"hp_bonus": 0, "thac0_bonus": 0, "primary": "str", "min_primary": 3})

    def _can_be_class(self, char_class):
        """Check if current stats meet class requirements."""
        bonuses = self._get_class_bonuses(char_class)
        primary_ok = self.ability_scores[bonuses["primary"]] >= bonuses["min_primary"]
        
        if "secondary" in bonuses:
            secondary_ok = self.ability_scores[bonuses["secondary"]] >= bonuses["min_secondary"]
            return primary_ok and secondary_ok
        
        return primary_ok

    def handle_input(self, event):
        """Handle input for character creation."""
        if event.type == pygame.KEYDOWN:
            if self.step == 'name':
                return self._handle_name_input(event)
            elif self.step == 'class':
                return self._handle_class_input(event)
            elif self.step == 'stats':
                return self._handle_stats_input(event)
            elif self.step == 'confirm':
                return self._handle_confirm_input(event)
        
        return None

    def _handle_name_input(self, event):
        """Handle name input."""
        if event.key == pygame.K_RETURN and self.character_name.strip():
            self.step = 'class'
        elif event.key == pygame.K_BACKSPACE:
            self.character_name = self.character_name[:-1]
        elif event.key == pygame.K_ESCAPE:
            return 'back_to_menu'
        elif event.unicode.isprintable() and len(self.character_name) < 20:
            self.character_name += event.unicode
        return None

    def _handle_class_input(self, event):
        """Handle class selection."""
        if event.key == pygame.K_UP:
            self.selected_class_index = (self.selected_class_index - 1) % len(self.available_classes)
        elif event.key == pygame.K_DOWN:
            self.selected_class_index = (self.selected_class_index + 1) % len(self.available_classes)
        elif event.key == pygame.K_RETURN:
            selected_class = self.available_classes[self.selected_class_index]
            if self._can_be_class(selected_class):
                self.character_class = selected_class
                self.step = 'stats'
            # If can't be class, stay here (could add error message)
        elif event.key == pygame.K_ESCAPE:
            self.step = 'name'
        return None

    def _handle_stats_input(self, event):
        """Handle stats review and reroll."""
        if event.key == pygame.K_RETURN:
            self.step = 'confirm'
        elif event.key == pygame.K_r and self.reroll_count < self.max_rerolls:
            self._generate_stats()
            self.reroll_count += 1
            # Check if current class is still valid
            if not self._can_be_class(self.character_class):
                self.step = 'class'  # Go back to class selection
        elif event.key == pygame.K_ESCAPE:
            self.step = 'class'
        return None

    def _handle_confirm_input(self, event):
        """Handle final confirmation."""
        if event.key == pygame.K_y:
            return self._create_final_character()
        elif event.key == pygame.K_n or event.key == pygame.K_ESCAPE:
            self.step = 'stats'
        return None

    def _create_final_character(self):
        """Create the final character and return it."""
        try:
            character = Character()
            character.name = self.character_name.strip()
            character.char_class = self.character_class
            character.ability_scores = self.ability_scores.copy()
            
            # Apply class bonuses
            bonuses = self._get_class_bonuses(self.character_class)
            base_hp = 8 + bonuses["hp_bonus"] + self._get_stat_modifier(character.ability_scores['con'])
            character.hp = max(1, base_hp)  # Minimum 1 HP
            character.max_hp = character.hp
            character.thac0 = 20 + bonuses["thac0_bonus"]  # Base THAC0 for level 1
            
            return {'action': 'character_created', 'character': character}
        except Exception as e:
            print(f"Error creating character: {e}")
            # Return to stats step if there's an error
            self.step = 'stats'
            return None

    def draw(self, screen):
        """Draw the character creation screen."""
        screen.fill(C_BACKGROUND)
        
        # Draw title
        title = "Character Creation"
        title_surf = self.font.render(title, True, C_GOLD)
        title_rect = title_surf.get_rect(centerx=SCREEN_WIDTH // 2, y=30)
        screen.blit(title_surf, title_rect)
        
        if self.step == 'name':
            self._draw_name_step(screen)
        elif self.step == 'class':
            self._draw_class_step(screen)
        elif self.step == 'stats':
            self._draw_stats_step(screen)
        elif self.step == 'confirm':
            self._draw_confirm_step(screen)

    def _draw_name_step(self, screen):
        """Draw the name input step."""
        y = 120
        
        prompt = "Enter your character's name:"
        prompt_surf = self.font.render(prompt, True, C_TEXT)
        prompt_rect = prompt_surf.get_rect(centerx=SCREEN_WIDTH // 2, y=y)
        screen.blit(prompt_surf, prompt_rect)
        
        # Name input box
        y += 60
        name_display = self.character_name + ("_" if pygame.time.get_ticks() % 1000 < 500 else "")
        name_surf = self.font.render(name_display, True, C_CURSOR)
        name_rect = name_surf.get_rect(centerx=SCREEN_WIDTH // 2, y=y)
        
        # Draw input box
        box_rect = name_rect.inflate(40, 20)
        pygame.draw.rect(screen, C_PANEL_BG, box_rect)
        pygame.draw.rect(screen, C_BORDER, box_rect, 2)
        screen.blit(name_surf, name_rect)
        
        # Instructions
        y += 80
        instructions = [
            "Type your character's name and press ENTER",
            "ESC - Return to main menu"
        ]
        for instruction in instructions:
            inst_surf = self.font.render(instruction, True, C_TEXT_DIM)
            inst_rect = inst_surf.get_rect(centerx=SCREEN_WIDTH // 2, y=y)
            screen.blit(inst_surf, inst_rect)
            y += 30

    def _draw_class_step(self, screen):
        """Draw the class selection step."""
        y = 100
        
        prompt = f"Choose a class for {self.character_name}:"
        prompt_surf = self.font.render(prompt, True, C_TEXT)
        prompt_rect = prompt_surf.get_rect(centerx=SCREEN_WIDTH // 2, y=y)
        screen.blit(prompt_surf, prompt_rect)
        
        y += 60
        
        # Draw class list
        for i, char_class in enumerate(self.available_classes):
            color = C_CURSOR if i == self.selected_class_index else C_TEXT
            can_be = self._can_be_class(char_class)
            
            if not can_be:
                color = C_TEXT_DIM
            
            prefix = "> " if i == self.selected_class_index else "  "
            suffix = " (Requirements not met)" if not can_be else ""
            class_text = f"{prefix}{char_class}{suffix}"
            
            class_surf = self.font.render(class_text, True, color)
            class_rect = class_surf.get_rect(centerx=SCREEN_WIDTH // 2, y=y)
            screen.blit(class_surf, class_rect)
            y += 30
        
        # Draw class description
        y += 20
        selected_class = self.available_classes[self.selected_class_index]
        desc = self.class_descriptions[selected_class]
        desc_surf = self.font.render(desc, True, C_TEXT_DIM)
        desc_rect = desc_surf.get_rect(centerx=SCREEN_WIDTH // 2, y=y)
        screen.blit(desc_surf, desc_rect)
        
        # Instructions
        y += 60
        instructions = [
            "UP/DOWN - Select class",
            "ENTER - Choose class",
            "ESC - Back to name"
        ]
        for instruction in instructions:
            inst_surf = self.font.render(instruction, True, C_TEXT_DIM)
            inst_rect = inst_surf.get_rect(centerx=SCREEN_WIDTH // 2, y=y)
            screen.blit(inst_surf, inst_rect)
            y += 25

    def _draw_stats_step(self, screen):
        """Draw the stats review step."""
        y = 100
        
        prompt = f"Ability Scores for {self.character_name} the {self.character_class}:"
        prompt_surf = self.font.render(prompt, True, C_TEXT)
        prompt_rect = prompt_surf.get_rect(centerx=SCREEN_WIDTH // 2, y=y)
        screen.blit(prompt_surf, prompt_rect)
        
        y += 60
        
        # Draw ability scores
        for score_name, value in self.ability_scores.items():
            modifier = self._get_stat_modifier(value)
            mod_str = f"({'+' if modifier >= 0 else ''}{modifier})"
            score_text = f"{score_name.upper()}: {value:2d} {mod_str}"
            
            score_surf = self.font.render(score_text, True, C_TEXT)
            score_rect = score_surf.get_rect(centerx=SCREEN_WIDTH // 2, y=y)
            screen.blit(score_surf, score_rect)
            y += 30
        
        # Show calculated HP and THAC0
        y += 20
        bonuses = self._get_class_bonuses(self.character_class)
        hp = max(1, 8 + bonuses["hp_bonus"] + self._get_stat_modifier(self.ability_scores['con']))
        thac0 = 20 + bonuses["thac0_bonus"]
        
        hp_surf = self.font.render(f"Starting HP: {hp}", True, C_GOLD)
        hp_rect = hp_surf.get_rect(centerx=SCREEN_WIDTH // 2, y=y)
        screen.blit(hp_surf, hp_rect)
        
        y += 30
        thac0_surf = self.font.render(f"THAC0: {thac0}", True, C_GOLD)
        thac0_rect = thac0_surf.get_rect(centerx=SCREEN_WIDTH // 2, y=y)
        screen.blit(thac0_surf, thac0_rect)
        
        # Instructions
        y += 60
        rerolls_left = self.max_rerolls - self.reroll_count
        instructions = [
            "ENTER - Accept these stats",
            f"R - Reroll stats ({rerolls_left} rerolls left)" if rerolls_left > 0 else "R - No rerolls left",
            "ESC - Back to class selection"
        ]
        
        for i, instruction in enumerate(instructions):
            color = C_TEXT_DIM if i == 1 and rerolls_left == 0 else C_TEXT_DIM
            inst_surf = self.font.render(instruction, True, color)
            inst_rect = inst_surf.get_rect(centerx=SCREEN_WIDTH // 2, y=y)
            screen.blit(inst_surf, inst_rect)
            y += 25

    def _draw_confirm_step(self, screen):
        """Draw the final confirmation step."""
        y = 120
        
        prompt = "Create this character?"
        prompt_surf = self.font.render(prompt, True, C_TEXT)
        prompt_rect = prompt_surf.get_rect(centerx=SCREEN_WIDTH // 2, y=y)
        screen.blit(prompt_surf, prompt_rect)
        
        y += 60
        
        # Character summary
        summary = [
            f"Name: {self.character_name}",
            f"Class: {self.character_class}",
            "",
            "Ability Scores:"
        ]
        
        for line in summary:
            if line:
                color = C_GOLD if line.startswith(("Name:", "Class:")) else C_TEXT
                line_surf = self.font.render(line, True, color)
                line_rect = line_surf.get_rect(centerx=SCREEN_WIDTH // 2, y=y)
                screen.blit(line_surf, line_rect)
            y += 25
        
        # Ability scores summary
        for score_name, value in self.ability_scores.items():
            modifier = self._get_stat_modifier(value)
            mod_str = f"({'+' if modifier >= 0 else ''}{modifier})"
            score_text = f"  {score_name.upper()}: {value} {mod_str}"
            
            score_surf = self.font.render(score_text, True, C_TEXT_DIM)
            score_rect = score_surf.get_rect(centerx=SCREEN_WIDTH // 2, y=y)
            screen.blit(score_surf, score_rect)
            y += 25
        
        # Final prompt
        y += 40
        confirm_text = "Y - Yes, create character    N - No, go back"
        confirm_surf = self.font.render(confirm_text, True, C_CURSOR)
        confirm_rect = confirm_surf.get_rect(centerx=SCREEN_WIDTH // 2, y=y)
        screen.blit(confirm_surf, confirm_rect)