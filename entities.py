import pygame
from constants import *
import random



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

        # Skill: Dash
        self.dash_unlocked = True  # Player starts with dash
        self.dash_cooldown = 5 * 1000  # 5 seconds
        self.dash_max_charges = 3
        self.dash_current_charges = 1
        self.dash_cooldown_timer = 0
        self.dash_key = pygame.K_SPACE

    def update(self):
        self.get_keys()
        if self.game.enemy_group:
            self.shoot()
        
        self.update_skills()
            
        self.rect.center = self.pos

    def update_skills(self):
        # Dash Cooldown
        if self.dash_unlocked and self.dash_current_charges < self.dash_max_charges:
            now = pygame.time.get_ticks()
            if now - self.dash_cooldown_timer > self.dash_cooldown:
                self.add_dash_charge()
                self.dash_cooldown_timer = now

    def activate_dash(self):
        if self.dash_unlocked and self.dash_current_charges > 0:
            self.dash_current_charges -= 1
            if self.dash_current_charges < self.dash_max_charges:
                self.dash_cooldown_timer = pygame.time.get_ticks()
            
            direction = pygame.math.Vector2(
                (pygame.key.get_pressed()[pygame.K_RIGHT] or pygame.key.get_pressed()[pygame.K_d]) - 
                (pygame.key.get_pressed()[pygame.K_LEFT] or pygame.key.get_pressed()[pygame.K_a]),
                (pygame.key.get_pressed()[pygame.K_DOWN] or pygame.key.get_pressed()[pygame.K_s]) - 
                (pygame.key.get_pressed()[pygame.K_UP] or pygame.key.get_pressed()[pygame.K_w])
            )
            if direction.length() > 0:
                self.pos += direction.normalize() * 150
            return True
        return False

    def add_dash_charge(self, amount=1):
        self.dash_current_charges = min(self.dash_max_charges, self.dash_current_charges + amount)

    def get_dash_cooldown_progress(self):
        if not self.dash_unlocked or self.dash_current_charges >= self.dash_max_charges:
            return 1.0
        return (pygame.time.get_ticks() - self.dash_cooldown_timer) / self.dash_cooldown

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

        if keys[self.dash_key]:
            self.activate_dash()

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
            if self.game.current_mode == "endless" and self.game.level > self.game.highscore:
                self.game.highscore = self.game.level
                self.game.save_highscore()

    def heal(self, amount):
        self.health = min(self.max_health, self.health + amount)


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
        self.health = ENEMY_HEALTH * (2 ** ((self.game.level - 1) // 5)) # Double health every 5 levels
        self.damage = ENEMY_DAMAGE

        if self.game.current_mode == "endless":
            self.speed *= 1 + (self.game.level - 1) * 0.05 # Increase speed by 5% each level in endless mode

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
