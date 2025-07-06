import pygame
import sys
import random
import math
import os

# --- Constants ---
WIDTH = 1280
HEIGHT = 720
FPS = 60

# --- File Paths ---
# Get the absolute path to the directory where the script is located
script_dir = os.path.dirname(os.path.abspath(__file__))
assets_dir = os.path.join(script_dir, "assets")
FONT_NAME = os.path.join(assets_dir, "SourceHanSansSC-Regular.ttf")

# --- Colors ---
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
GREY = (128, 128, 128)

# --- Game States ---
PLAYING = 'playing'
UPGRADING = 'upgrading'
GAME_OVER = 'game_over'
PAUSED = 'paused'

# --- Game Settings ---
PLAYER_SIZE = 30
PLAYER_SPEED = 250
PLAYER_HEALTH = 100
PLAYER_ATTACK_SPEED = 500  # ms

ENEMY_SIZE = 25
ENEMY_SPEED = 120
ENEMY_HEALTH = 10
ENEMY_DAMAGE = 10

PROJECTILE_SIZE = 10
PROJECTILE_SPEED = 600


class Player(pygame.sprite.Sprite):
    def __init__(self, game):
        super().__init__()
        self.game = game
        self.image = pygame.Surface((PLAYER_SIZE, PLAYER_SIZE))
        self.image.fill(BLUE)
        self.rect = self.image.get_rect(center=(WIDTH / 2, HEIGHT / 2))
        self.pos = pygame.math.Vector2(self.rect.center)
        
        self.speed = PLAYER_SPEED
        self.max_health = PLAYER_HEALTH
        self.health = self.max_health
        self.attack_speed = PLAYER_ATTACK_SPEED
        self.projectile_count = 1
        
        self.last_shot_time = 0
        self.kill_count = 0

        self.skills = [
            Skill(self, "冲刺", 5, 3, pygame.K_SPACE)
        ]

    def update(self):
        self.get_keys()
        if self.game.enemy_group:
            self.shoot()
        
        for skill in self.skills:
            skill.update()
            
        self.rect.center = self.pos

    def shoot(self):
        now = pygame.time.get_ticks()
        if now - self.last_shot_time > self.attack_speed:
            self.last_shot_time = now
            
            closest_enemy = self.find_closest_enemy()
            if closest_enemy:
                direction = (closest_enemy.pos - self.pos).normalize()
                self.create_projectiles(direction)

    def find_closest_enemy(self):
        return min(self.game.enemy_group, key=lambda enemy: self.pos.distance_to(enemy.pos), default=None)

    def create_projectiles(self, base_direction):
        self.spawn_projectile(base_direction)
        if self.projectile_count > 1:
            spread_angle = 15
            num_side_projectiles = (self.projectile_count - 1) // 2
            for i in range(num_side_projectiles):
                angle = spread_angle * (i + 1)
                self.spawn_projectile(base_direction.rotate(angle))
                self.spawn_projectile(base_direction.rotate(-angle))

    def spawn_projectile(self, direction):
        projectile = Projectile(self.game, self.pos, direction)
        self.game.all_sprites.add(projectile)
        self.game.projectile_group.add(projectile)

    def get_keys(self):
        keys = pygame.key.get_pressed()
        vel = pygame.math.Vector2(0, 0)
        if keys[pygame.K_LEFT] or keys[pygame.K_a]: vel.x = -1
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]: vel.x = 1
        if keys[pygame.K_UP] or keys[pygame.K_w]: vel.y = -1
        if keys[pygame.K_DOWN] or keys[pygame.K_s]: vel.y = 1
        
        if vel.length() > 0:
            self.pos += vel.normalize() * self.speed * self.game.dt
        self.keep_on_screen()

    def keep_on_screen(self):
        self.pos.x = max(PLAYER_SIZE / 2, min(self.pos.x, WIDTH - PLAYER_SIZE / 2))
        self.pos.y = max(PLAYER_SIZE / 2, min(self.pos.y, HEIGHT - PLAYER_SIZE / 2))
        self.rect.center = self.pos

    def is_alive(self):
        return self.health > 0

    def take_damage(self, amount):
        self.health -= amount
        if self.health <= 0:
            self.health = 0
            self.game.game_state = GAME_OVER

    def heal(self, amount):
        self.health = min(self.max_health, self.health + amount)


class Projectile(pygame.sprite.Sprite):
    def __init__(self, game, pos, direction):
        super().__init__()
        self.game = game
        self.image = pygame.Surface((PROJECTILE_SIZE, PROJECTILE_SIZE))
        self.image.fill(YELLOW)
        self.rect = self.image.get_rect(center=pos)
        self.pos = pygame.math.Vector2(pos)
        self.direction = direction
        self.speed = PROJECTILE_SPEED

    def update(self):
        self.pos += self.direction * self.speed * self.game.dt
        self.rect.center = self.pos
        if not self.game.screen.get_rect().colliderect(self.rect):
            self.kill()


class Enemy(pygame.sprite.Sprite):
    def __init__(self, game, player):
        super().__init__()
        self.game = game
        self.player = player
        self.image = pygame.Surface((ENEMY_SIZE, ENEMY_SIZE))
        self.image.fill(RED)
        self.pos = self.get_spawn_pos()
        self.rect = self.image.get_rect(center=self.pos)
        self.speed = ENEMY_SPEED
        self.health = ENEMY_HEALTH
        self.damage = ENEMY_DAMAGE

    def get_spawn_pos(self):
        margin = 50
        side = random.choice(['top', 'bottom', 'left', 'right'])
        if side == 'top': return pygame.math.Vector2(random.randint(-margin, WIDTH + margin), -margin)
        if side == 'bottom': return pygame.math.Vector2(random.randint(-margin, WIDTH + margin), HEIGHT + margin)
        if side == 'left': return pygame.math.Vector2(-margin, random.randint(-margin, HEIGHT + margin))
        if side == 'right': return pygame.math.Vector2(WIDTH + margin, random.randint(-margin, HEIGHT + margin))

    def update(self):
        if self.player.is_alive():
            direction = (self.player.pos - self.pos).normalize()
            self.pos += direction * self.speed * self.game.dt
            self.rect.center = self.pos


class UI:
    def __init__(self, game):
        self.game = game
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
        if self.game.game_state == GAME_OVER:
            self.draw_game_over_screen(screen)
        else:
            self.draw_player_hud(screen)
            self.draw_skill_slots(screen)

            if self.game.game_state == UPGRADING:
                self.draw_upgrade_screen(screen)
            elif self.game.game_state == PAUSED:
                self.draw_pause_screen(screen)

    def draw_pause_screen(self, screen):
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        screen.blit(overlay, (0, 0))
        title_text = self.title_font.render("游戏暂停", True, WHITE)
        screen.blit(title_text, title_text.get_rect(center=(WIDTH / 2, HEIGHT / 2)))

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
            button.draw(screen, self.game.upgrade_points)

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


class Button:
    def __init__(self, x, y, w, h, text, cost, callback):
        self.rect = pygame.Rect(x, y, w, h)
        self.text = text
        self.cost = cost
        self.callback = callback
        self.font = None # Will be set in Game class

    def draw(self, screen, points):
        if not self.font:
            self.font = pygame.font.Font(FONT_NAME, 32) if FONT_NAME else pygame.font.Font(None, 40)

        can_afford = points >= self.cost
        color = GREEN if can_afford else GREY
        pygame.draw.rect(screen, color, self.rect)
        pygame.draw.rect(screen, BLACK, self.rect, 2)
        
        display_text = f"{self.text} ({self.cost}点)" if self.cost > 0 else self.text
        text_surf = self.font.render(display_text, True, BLACK)
        screen.blit(text_surf, text_surf.get_rect(center=self.rect.center))

    def handle_event(self, event, game):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos) and game.upgrade_points >= self.cost:
                if self.cost > 0: game.upgrade_points -= self.cost
                self.callback(game)


class Skill:
    def __init__(self, player, name, cooldown, max_charges, key):
        self.player = player
        self.name = name
        self.cooldown = cooldown * 1000
        self.max_charges = max_charges
        self.key = key
        self.current_charges = 1
        self.cooldown_timer = 0

    def activate(self):
        if self.current_charges > 0:
            self.current_charges -= 1
            if self.current_charges < self.max_charges:
                self.cooldown_timer = pygame.time.get_ticks()
            
            if self.name == "冲刺":
                direction = pygame.math.Vector2(
                    (pygame.key.get_pressed()[pygame.K_RIGHT] or pygame.key.get_pressed()[pygame.K_d]) - 
                    (pygame.key.get_pressed()[pygame.K_LEFT] or pygame.key.get_pressed()[pygame.K_a]),
                    (pygame.key.get_pressed()[pygame.K_DOWN] or pygame.key.get_pressed()[pygame.K_s]) - 
                    (pygame.key.get_pressed()[pygame.K_UP] or pygame.key.get_pressed()[pygame.K_w])
                )
                if direction.length() > 0:
                    self.player.pos += direction.normalize() * 150
            return True
        return False

    def update(self):
        if self.current_charges < self.max_charges:
            now = pygame.time.get_ticks()
            if now - self.cooldown_timer > self.cooldown:
                self.add_charge()
                self.cooldown_timer = now

    def add_charge(self, amount=1):
        self.current_charges = min(self.max_charges, self.current_charges + amount)

    def get_cooldown_progress(self):
        if self.current_charges >= self.max_charges:
            return 1.0
        return (pygame.time.get_ticks() - self.cooldown_timer) / self.cooldown


class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("肉鸽射击小游戏")
        self.clock = pygame.time.Clock()
        self.is_running = True
        self.dt = 0
        self.reset_game()

    def reset_game(self):
        self.game_state = PLAYING
        self.level = 1
        self.upgrade_points = 0
        
        self.all_sprites = pygame.sprite.Group()
        self.enemy_group = pygame.sprite.Group()
        self.projectile_group = pygame.sprite.Group()
        
        self.player = Player(self)
        self.all_sprites.add(self.player)
        
        self.ui = UI(self)
        self.setup_upgrade_buttons()
        self.start_new_level()

    def start_new_level(self):
        self.game_state = PLAYING
        num_enemies = 5 + self.level * 2
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

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if self.game_state == PLAYING:
                        self.game_state = PAUSED
                    elif self.game_state == PAUSED:
                        self.game_state = PLAYING
                
                if self.game_state == GAME_OVER and event.key == pygame.K_r:
                    self.reset_game()
                
                if self.game_state == PLAYING:
                    for skill in self.player.skills:
                        if event.key == skill.key:
                            skill.activate()

            if self.game_state == UPGRADING:
                for button in self.upgrade_buttons:
                    button.handle_event(event, self)

    def update(self):
        if self.game_state == PLAYING:
            self.all_sprites.update()
            self.check_collisions()
            if not self.enemy_group:
                self.level += 1
                self.game_state = UPGRADING

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
        self.all_sprites.draw(self.screen)
        self.ui.draw(self.screen)
        pygame.display.flip()

    def quit(self):
        pygame.quit()
        sys.exit()

if __name__ == '__main__':
    Game().run()