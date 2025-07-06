import pygame
from entities import Enemy
from constants import ENEMY_SIZE, ENEMY_HEALTH, ENEMY_SPEED, GREEN

class Boss(Enemy):
    def __init__(self, game, player):
        super().__init__(game, player)
        self.image = pygame.Surface((ENEMY_SIZE * 2, ENEMY_SIZE * 2))
        self.image.fill(GREEN)
        self.health = (ENEMY_HEALTH * (2 ** ((self.game.level - 1) // 5))) * 20 # 20x health of a normal enemy
        self.speed = ENEMY_SPEED * 0.8 # Slightly slower

class TutorialBoss(Boss):
    def __init__(self, game, player):
        super().__init__(game, player)
        self.health = 50 # Weak boss for tutorial
