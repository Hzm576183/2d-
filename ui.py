import pygame
from constants import *
from skills import SkillTree
import os

# --- File Paths ---
# Get the absolute path to the directory where the script is located
script_dir = os.path.dirname(os.path.abspath(__file__))
assets_dir = os.path.join(script_dir, "assets")
FONT_NAME = os.path.join(assets_dir, "SourceHanSansSC-Regular.ttf")

class Button:
    def __init__(self, x, y, w, h, text, cost, callback):
        self.rect = pygame.Rect(x, y, w, h)
        self.text = text
        self.cost = cost
        self.callback = callback
        self.font = None

    def draw(self, screen, points, offset_y=0):
        if not self.font:
            self.font = pygame.font.Font(FONT_NAME, 32) if FONT_NAME else pygame.font.Font(None, 40)

        drawn_rect = self.rect.move(0, offset_y)
        can_afford = points >= self.cost and self.cost != -1
        color = GREEN if can_afford else GREY
        pygame.draw.rect(screen, color, drawn_rect)
        pygame.draw.rect(screen, BLACK, drawn_rect, 2)
        
        display_text = f"{self.text} ({self.cost}点)" if self.cost > 0 else self.text
        text_surf = self.font.render(display_text, True, BLACK)
        screen.blit(text_surf, text_surf.get_rect(center=drawn_rect.center))

    def handle_event(self, event, game, offset_y=0):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            drawn_rect = self.rect.move(0, offset_y)
            if drawn_rect.collidepoint(event.pos) and game.upgrade_points >= self.cost and self.cost != -1:
                if self.cost > 0: game.upgrade_points -= self.cost
                self.callback(game)

class SkillPanel:
    def __init__(self, x, y, w, h, skill_tree):
        self.rect = pygame.Rect(x, y, w, h)
        self.skill_tree = skill_tree
        self.scroll_y = 0
        self.max_scroll_y = 0

    def draw(self, screen, player_points):
        pygame.draw.rect(screen, GREY, self.rect)
        y_offset = self.rect.y + 20
        for skill_def in self.skill_tree.skills.values():
            text = f"{skill_def.name} - {'已学习' if skill_def.is_learned else f'{skill_def.cost}点'}"
            # ... (drawing logic for each skill)

    def handle_event(self, event, game):
        if event.type == pygame.MOUSEWHEEL:
            self.scroll_y += event.y * 30
            self.scroll_y = max(-self.max_scroll_y, min(0, self.scroll_y))
        elif event.type == pygame.MOUSEBUTTONDOWN:
            # ... (logic to handle clicks on skills)
            pass

class SkillTreePopup:
    def __init__(self, w, h, skill_tree):
        self.rect = pygame.Rect(WIDTH/2 - w/2, HEIGHT/2 - h/2, w, h)
        self.skill_tree = skill_tree
        self.active_skill = None
        self.scroll_y = 0
        self.max_scroll_y = 0

    def draw(self, screen, player_points):
        if not self.active_skill:
            return
        
        pygame.draw.rect(screen, BLACK, self.rect)
        pygame.draw.rect(screen, WHITE, self.rect, 2)
        # ... (drawing logic for the skill tree nodes)
