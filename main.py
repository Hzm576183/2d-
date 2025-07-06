import pygame
import sys
import random
import math
import os
import json

from constants import *
from entities import Player, Enemy, Skill, Projectile
from endless_mode import Boss
from account_manager import account_manager

# --- File Paths ---
# Get the absolute path to the directory where the script is located
script_dir = os.path.dirname(os.path.abspath(__file__))
assets_dir = os.path.join(script_dir, "assets")
FONT_NAME = os.path.join(assets_dir, "SourceHanSansSC-Regular.ttf")

class UI:
    def __init__(self, game):
        self.game = game
        self.scroll_y = 0
        try:
            self.font = pygame.font.Font(FONT_NAME, 30)
            self.title_font = pygame.font.Font(FONT_NAME, 60)
            self.score_font = pygame.font.Font(FONT_NAME, 45)
            self.key_font = pygame.font.Font(FONT_NAME, 20)
            self.charge_font = pygame.font.Font(FONT_NAME, 26)
        except FileNotFoundError:
            print(f"字体文件 '{FONT_NAME}' 未找到，将使用默认字体。")
            self.font = pygame.font.Font(None, 36)
            self.title_font = pygame.font.Font(None, 72)
            self.score_font = pygame.font.Font(None, 50)
            self.key_font = pygame.font.Font(None, 24)
            self.charge_font = pygame.font.Font(None, 30)


    def draw(self, screen):
        if self.game.game_state == 'account_selection':
            self.draw_account_selection_screen(screen)
        elif self.game.game_state == START_SCREEN:
            self.draw_start_screen(screen)
        elif self.game.game_state == GAME_OVER:
            self.draw_game_over_screen(screen)
        elif self.game.game_state == GAME_WON:
            self.draw_game_won_screen(screen)
        else:
            self.draw_player_hud(screen)
            self.draw_skill_slots(screen)

            if self.game.game_state == UPGRADING:
                self.draw_upgrade_screen(screen)
            elif self.game.game_state == PAUSED:
                self.draw_pause_screen(screen)

    def draw_account_selection_screen(self, screen):
        screen.fill(BLACK)
        title_text = self.title_font.render("选择或创建账户", True, WHITE)
        screen.blit(title_text, title_text.get_rect(center=(WIDTH / 2, 100)))

        # Draw account list
        y_offset = 200
        for name in account_manager.accounts:
            color = YELLOW if name == self.game.selected_account else WHITE
            text = self.font.render(name, True, color)
            rect = text.get_rect(center=(WIDTH / 2, y_offset))
            screen.blit(text, rect)
            y_offset += 50

        # Draw input box
        input_rect = pygame.Rect(WIDTH / 2 - 150, y_offset, 300, 50)
        pygame.draw.rect(screen, WHITE, input_rect, 2)
        input_text = self.font.render(self.game.account_input_text, True, WHITE)
        screen.blit(input_text, (input_rect.x + 5, input_rect.y + 5))

        # Draw buttons
        create_button = Button(WIDTH / 2 - 150, y_offset + 60, 140, 50, "创建", 0, lambda g: g.create_account())
        enter_button = Button(WIDTH / 2 + 10, y_offset + 60, 140, 50, "进入游戏", 0, lambda g: g.select_account())
        create_button.draw(screen, 1)
        enter_button.draw(screen, 1)


    def draw_start_screen(self, screen):
        screen.fill(BLACK)
        title_text = self.title_font.render("肉鸽射击游戏", True, WHITE)
        screen.blit(title_text, title_text.get_rect(center=(WIDTH / 2, HEIGHT / 4)))
        
        for button in self.game.start_buttons:
            button.draw(screen, 1) # Pass 1 to enable drawing

        highscore_text = self.font.render(f"无尽模式最高纪录: {self.game.highscore}", True, YELLOW)
        screen.blit(highscore_text, highscore_text.get_rect(topright=(WIDTH - 20, 20)))

    def draw_pause_screen(self, screen):
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        screen.blit(overlay, (0, 0))
        title_text = self.title_font.render("游戏暂停", True, WHITE)
        screen.blit(title_text, title_text.get_rect(center=(WIDTH / 2, HEIGHT / 3)))
        
        for button in self.game.pause_buttons:
            button.draw(screen, 1, self.scroll_y)

    def draw_player_hud(self, screen):
        # Health Bar
        health_ratio = self.game.player.health / self.game.player.max_health
        bar_rect = pygame.Rect(10, 10, 200, 20)
        fill_rect = pygame.Rect(10, 10, int(200 * health_ratio), 20)
        pygame.draw.rect(screen, RED, bar_rect)
        pygame.draw.rect(screen, GREEN, fill_rect)
        pygame.draw.rect(screen, BLACK, bar_rect, 2)

        # Stats
        texts = [
            f"击杀: {self.game.player.kill_count}",
            f"关卡: {self.game.level}",
            f"升级点: {self.game.upgrade_points}"
        ]
        for i, text in enumerate(texts):
            color = GREEN if "升级点" in text and self.game.upgrade_points > 0 else BLACK
            text_surf = self.font.render(text, True, color)
            screen.blit(text_surf, (10, 40 + i * 30))

        # Pause Hint
        pause_text = self.key_font.render("ESC 暂停", True, BLACK)
        screen.blit(pause_text, pause_text.get_rect(topright=(WIDTH - 10, 10)))

    def draw_skill_slots(self, screen):
        slot_size = 60
        slot_margin = 10
        start_x = (WIDTH - (4 * slot_size + 3 * slot_margin)) / 2
        start_y = HEIGHT - slot_size - slot_margin

        for i in range(4):
            x = start_x + i * (slot_size + slot_margin)
            slot_rect = pygame.Rect(x, start_y, slot_size, slot_size)
            
            if i < len(self.game.player.skills):
                skill = self.game.player.skills[i]
                
                progress = skill.get_cooldown_progress()
                
                pygame.draw.rect(screen, BLUE, slot_rect)
                if progress < 1.0:
                    overlay_rect = pygame.Rect(x, start_y, slot_size, slot_size * (1-progress))
                    pygame.draw.rect(screen, (0, 0, 50, 200), overlay_rect)

                charge_text = self.charge_font.render(str(skill.current_charges), True, WHITE)
                screen.blit(charge_text, charge_text.get_rect(bottomright=(slot_rect.right - 5, slot_rect.bottom - 5)))

                key_name = pygame.key.name(skill.key).upper()
                if key_name == "SPACE": key_name = "空格"
                key_text = self.key_font.render(key_name, True, WHITE)
                screen.blit(key_text, key_text.get_rect(topleft=(slot_rect.left + 5, slot_rect.top + 5)))
            else:
                pygame.draw.rect(screen, GREY, slot_rect)

            pygame.draw.rect(screen, BLACK, slot_rect, 2)

    def draw_upgrade_screen(self, screen):
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        screen.blit(overlay, (0, 0))
        title_text = self.title_font.render("关卡完成", True, WHITE)
        screen.blit(title_text, title_text.get_rect(center=(WIDTH / 2, 100)))
        for button in self.game.upgrade_buttons:
            button.draw(screen, self.game.upgrade_points, self.scroll_y)

    def draw_game_over_screen(self, screen):
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 220))
        screen.blit(overlay, (0, 0))
        title_text = self.title_font.render("游戏结束", True, RED)
        screen.blit(title_text, title_text.get_rect(center=(WIDTH / 2, HEIGHT / 3)))
        score_text = self.score_font.render(f"你到达了第 {self.game.level} 关", True, WHITE)
        screen.blit(score_text, score_text.get_rect(center=(WIDTH / 2, HEIGHT / 2)))
        restart_text = self.score_font.render("按 R 键重新开始", True, WHITE)
        screen.blit(restart_text, restart_text.get_rect(center=(WIDTH / 2, HEIGHT / 2 + 80)))

    def draw_game_won_screen(self, screen):
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 220))
        screen.blit(overlay, (0, 0))
        title_text = self.title_font.render("恭喜通关！", True, GREEN)
        screen.blit(title_text, title_text.get_rect(center=(WIDTH / 2, HEIGHT / 3)))
        restart_text = self.score_font.render("按 R 键重新开始", True, WHITE)
        screen.blit(restart_text, restart_text.get_rect(center=(WIDTH / 2, HEIGHT / 2 + 80)))


class Button:
    def __init__(self, x, y, w, h, text, cost, callback):
        self.rect = pygame.Rect(x, y, w, h)
        self.text = text
        self.cost = cost
        self.callback = callback
        self.font = None # Will be set in Game class

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


class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("肉鸽射击小游戏")
        self.clock = pygame.time.Clock()
        self.is_running = True
        self.dt = 0
        self.max_scroll_y = 0
        self.game_state = 'account_selection' # Start with account selection
        self.account_input_text = ''
        self.selected_account = None
        self.highscore = 0
        self.reset_game()

    def save_highscore(self):
        account_data = account_manager.get_current_account_data()
        if account_data:
            account_data["highscore"] = self.highscore
            account_manager.save_accounts()

    def reset_game(self):
        self.level = 1
        self.upgrade_points = 0
        self.current_mode = None
        
        self.all_sprites = pygame.sprite.Group()
        self.enemy_group = pygame.sprite.Group()
        self.projectile_group = pygame.sprite.Group()
        
        self.player = Player(self)
        self.all_sprites.add(self.player)
        
        self.ui = UI(self)
        self.setup_upgrade_buttons()
        self.setup_start_buttons()
        self.setup_pause_buttons()

    def load_from_account(self):
        account_data = account_manager.get_current_account_data()
        if not account_data:
            return

        self.highscore = account_data.get("highscore", 0)
        self.game_state = START_SCREEN

    def setup_pause_buttons(self):
        self.pause_buttons = []
        w, h, gap = 380, 60, 75
        cx, sy = WIDTH / 2 - w / 2, HEIGHT / 2 - h

        self.pause_buttons.append(Button(cx, sy, w, h, "继续游戏", 0, lambda g: setattr(g, 'game_state', PLAYING)))
        self.pause_buttons.append(Button(cx, sy + gap, w, h, "保存并退出", 0, lambda g: g.save_game()))
        self.pause_buttons.append(Button(cx, sy + 2 * gap, w, h, "回到主菜单", 0, lambda g: g.go_to_main_menu()))

    def setup_start_buttons(self):
        self.start_buttons = []
        w, h, gap = 380, 60, 75
        cx, sy = WIDTH / 2 - w / 2, HEIGHT / 2 - h - gap * 2

        self.start_buttons.append(Button(cx, sy, w, h, "普通模式", 0, lambda g: g.start_new_game("normal")))
        self.start_buttons.append(Button(cx, sy + gap, w, h, "副本模式", 0, lambda g: g.start_new_game("dungeon")))
        self.start_buttons.append(Button(cx, sy + 2 * gap, w, h, "无尽模式", 0, lambda g: g.start_new_game("endless")))
        
        continue_button = Button(cx, sy + 3 * gap, w, h, "继续游戏", 0, lambda g: g.continue_game())
        save_file = account_manager.get_current_account_data().get("save_file") if account_manager.get_current_account_data() else None
        if not save_file or not os.path.exists(save_file):
            continue_button.cost = -1 # Make it unclickable
        self.start_buttons.append(continue_button)
        self.start_buttons.append(Button(cx, sy + 4 * gap, w, h, "退出游戏", 0, lambda g: g.quit()))

    def start_new_game(self, mode):
        self.current_mode = mode
        self.level = 1
        self.upgrade_points = 0
        self.player.kill_count = 0
        self.player.health = self.player.max_health
        self.game_state = PLAYING
        self.start_new_level()

    def continue_game(self):
        if self.load_game():
            self.game_state = PLAYING
        else:
            # This should not happen if button is disabled
            self.start_new_game("normal")

    def go_to_main_menu(self):
        self.game_state = START_SCREEN

    def start_new_level(self):
        self.game_state = PLAYING

        if self.current_mode == "endless" and self.level % 20 == 0:
            # Spawn a boss
            boss = Boss(self, self.player)
            self.all_sprites.add(boss)
            self.enemy_group.add(boss)
        else:
            # Spawn normal enemies
            num_enemies = 5 + self.level * 3
            for _ in range(num_enemies):
                enemy = Enemy(self, self.player)
                self.all_sprites.add(enemy)
                self.enemy_group.add(enemy)

    def setup_upgrade_buttons(self):
        self.upgrade_buttons = []
        w, h, gap = 380, 60, 75
        cx, sy = WIDTH / 2 - w / 2, 180
        
        upgrades = [
            ("移动速度", 1, lambda g: setattr(g.player, 'speed', g.player.speed + 30)),
            ("攻击速度", 1, lambda g: setattr(g.player, 'attack_speed', g.player.attack_speed * 0.85)),
            ("最大生命", 1, lambda g: (setattr(g.player, 'max_health', g.player.max_health + 20), g.player.heal(20))),
            ("散射", 1, lambda g: setattr(g.player, 'projectile_count', g.player.projectile_count + 2)),
            ("购买冲刺次数", 2, lambda g: g.player.skills[0].add_charge() if g.player.skills else None)
        ]
        for i, (text, cost, action) in enumerate(upgrades):
            self.upgrade_buttons.append(Button(cx, sy + i * gap, w, h, text, cost, action))
        
        self.upgrade_buttons.append(Button(cx, sy + len(upgrades) * gap, w, h, "下一关", 0, lambda g: g.start_new_level()))
        self.upgrade_buttons.append(Button(cx, sy + (len(upgrades) + 1) * gap, w, h, "回到主菜单", 0, lambda g: g.go_to_main_menu()))
        self.upgrade_buttons.append(Button(cx, sy + (len(upgrades) + 2) * gap, w, h, "保存并退出", 0, lambda g: g.save_game()))

    def run(self):
        while self.is_running:
            self.dt = self.clock.tick(FPS) / 1000.0
            self.events()
            self.update()
            self.draw()
        self.quit()

    def events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.is_running = False

            if self.game_state == 'account_selection':
                self.handle_account_selection_events(event)
                continue

            if self.game_state == UPGRADING or self.game_state == PAUSED:
                if event.type == pygame.MOUSEWHEEL:
                    self.ui.scroll_y += event.y * 30
                    self.ui.scroll_y = max(-self.max_scroll_y, min(0, self.ui.scroll_y))

            if self.game_state == START_SCREEN:
                for button in self.start_buttons:
                    button.handle_event(event, self)
                continue

            if self.game_state == PAUSED:
                for button in self.pause_buttons:
                    button.handle_event(event, self, self.ui.scroll_y)

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if self.game_state == PLAYING:
                        self.game_state = PAUSED
                        self.ui.scroll_y = 0
                        
                        # Recalculate max_scroll_y for pause screen
                        h, gap = 60, 75
                        sy = HEIGHT / 2 - h
                        content_height = (len(self.pause_buttons) * (h + gap)) - gap
                        self.max_scroll_y = max(0, content_height - (HEIGHT - sy))
                    elif self.game_state == PAUSED:
                        self.game_state = PLAYING
                
                if (self.game_state == GAME_OVER or self.game_state == GAME_WON) and event.key == pygame.K_r:
                    self.reset_game()
                
                if self.game_state == PLAYING:
                    for skill in self.player.skills:
                        if event.key == skill.key:
                            skill.activate()

            if self.game_state == UPGRADING:
                for button in self.upgrade_buttons:
                    button.handle_event(event, self, self.ui.scroll_y)

    def handle_account_selection_events(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                self.create_account()
            elif event.key == pygame.K_BACKSPACE:
                self.account_input_text = self.account_input_text[:-1]
            else:
                self.account_input_text += event.unicode
        elif event.type == pygame.MOUSEBUTTONDOWN:
            # Check account selection
            y_offset = 200
            for name in account_manager.accounts:
                rect = pygame.Rect(WIDTH / 2 - 150, y_offset - 25, 300, 50)
                if rect.collidepoint(event.pos):
                    self.selected_account = name
                y_offset += 50
            
            # Check button clicks
            create_button = Button(WIDTH / 2 - 150, y_offset + 60, 140, 50, "创建", 0, lambda g: g.create_account())
            enter_button = Button(WIDTH / 2 + 10, y_offset + 60, 140, 50, "进入游戏", 0, lambda g: g.select_account())
            create_button.handle_event(event, self)
            enter_button.handle_event(event, self)

    def create_account(self):
        if self.account_input_text:
            account_manager.create_account(self.account_input_text)
            self.account_input_text = ''

    def select_account(self):
        if self.selected_account:
            account_manager.set_current_account(self.selected_account)
            self.load_from_account()


    def update(self):
        if self.game_state == PLAYING:
            self.all_sprites.update()
            self.check_collisions()
            if not self.enemy_group:
                if self.current_mode == "normal" and self.level == 20:
                    self.game_state = GAME_WON
                else:
                    self.level += 1
                    self.player.max_health += 5
                    self.player.heal(5)
                    self.game_state = UPGRADING
                    self.ui.scroll_y = 0
                    
                    # Recalculate max_scroll_y for upgrade screen
                    h, gap = 60, 75
                    sy = 180
                    content_height = (len(self.upgrade_buttons) * (h + gap)) - gap
                    self.max_scroll_y = max(0, content_height - (HEIGHT - sy))

    def check_collisions(self):
        for _ in pygame.sprite.groupcollide(self.enemy_group, self.projectile_group, True, True):
            self.player.kill_count += 1
            if self.player.kill_count % 10 == 0:
                self.upgrade_points += 1

        if self.player.is_alive():
            for hit in pygame.sprite.spritecollide(self.player, self.enemy_group, True):
                self.player.take_damage(hit.damage)

    def draw(self):
        self.screen.fill(WHITE)
        if self.game_state == 'account_selection':
            self.ui.draw_account_selection_screen(self.screen)
        else:
            self.all_sprites.draw(self.screen)
            self.ui.draw(self.screen)
        pygame.display.flip()

    def quit(self):
        pygame.quit()
        sys.exit()

    def save_game(self):
        account_data = account_manager.get_current_account_data()
        if not account_data:
            return

        data = {
            "level": self.level,
            "upgrade_points": self.upgrade_points,
            "current_mode": self.current_mode,
            "player": {
                "pos": [self.player.pos.x, self.player.pos.y],
                "speed": self.player.speed,
                "max_health": self.player.max_health,
                "health": self.player.health,
                "attack_speed": self.player.attack_speed,
                "projectile_count": self.player.projectile_count,
                "kill_count": self.player.kill_count,
            }
        }
        with open(account_data["save_file"], 'w') as f:
            json.dump(data, f)
        self.quit()

    def load_game(self):
        account_data = account_manager.get_current_account_data()
        if not account_data or not os.path.exists(account_data["save_file"]):
            return False
            
        with open(account_data["save_file"], 'r') as f:
            data = json.load(f)

        self.level = data["level"]
        self.upgrade_points = data["upgrade_points"]
        self.current_mode = data.get("current_mode", "normal")
        
        player_data = data["player"]
        self.player.pos = pygame.math.Vector2(player_data["pos"])
        self.player.speed = player_data["speed"]
        self.player.max_health = player_data["max_health"]
        self.player.health = player_data["health"]
        self.player.attack_speed = player_data["attack_speed"]
        self.player.projectile_count = player_data["projectile_count"]
        self.player.kill_count = player_data["kill_count"]
        
        self.start_new_level()
        return True

if __name__ == '__main__':
    Game().run()
