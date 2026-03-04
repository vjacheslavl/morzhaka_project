import pygame
import random
from constants import SCREEN_WIDTH, SCREEN_HEIGHT
from sprites import (
    create_enemy_sprite, create_ice_enemy_sprite,
    create_boss_sprite, create_final_boss_sprite, create_player_sprite
)


class MenuEnemy:
    """Simple enemy for menu background animation."""
    def __init__(self, x, y, sprite, speed):
        self.x = x
        self.y = y
        self.sprite = sprite
        self.speed = speed
        self.direction = [1, 0]
        self.change_timer = 0
    
    def update(self):
        self.change_timer += 1
        if self.change_timer > 60:
            self.change_timer = 0
            self.direction = [random.choice([-1, 0, 1]), random.choice([-1, 0, 1])]
        
        self.x += self.direction[0] * self.speed
        self.y += self.direction[1] * self.speed
        
        if self.x < 50:
            self.x = 50
            self.direction[0] = 1
        if self.x > SCREEN_WIDTH - 100:
            self.x = SCREEN_WIDTH - 100
            self.direction[0] = -1
        if self.y < 150:
            self.y = 150
            self.direction[1] = 1
        if self.y > SCREEN_HEIGHT - 100:
            self.y = SCREEN_HEIGHT - 100
            self.direction[1] = -1
    
    def draw(self, screen):
        screen.blit(self.sprite, (self.x, self.y))


def init_menu_background():
    """Initialize menu background with animated characters."""
    menu_enemies = []
    
    for _ in range(3):
        x = random.randint(100, SCREEN_WIDTH - 200)
        y = random.randint(200, SCREEN_HEIGHT - 150)
        menu_enemies.append(MenuEnemy(x, y, create_enemy_sprite(), 1.5))
    
    for _ in range(2):
        x = random.randint(100, SCREEN_WIDTH - 200)
        y = random.randint(200, SCREEN_HEIGHT - 150)
        menu_enemies.append(MenuEnemy(x, y, create_ice_enemy_sprite(), 1.2))
    
    boss_x = SCREEN_WIDTH // 2 - 40
    boss_y = SCREEN_HEIGHT // 2 + 50
    menu_boss = MenuEnemy(boss_x, boss_y, create_boss_sprite(), 0.8)
    
    player_x = 150
    player_y = SCREEN_HEIGHT // 2
    menu_player = MenuEnemy(player_x, player_y, create_player_sprite(), 1.8)
    
    final_boss_x = SCREEN_WIDTH - 250
    final_boss_y = SCREEN_HEIGHT // 2 - 20
    menu_final_boss = MenuEnemy(final_boss_x, final_boss_y, create_final_boss_sprite(), 0.6)
    
    return menu_enemies, menu_boss, menu_player, menu_final_boss
