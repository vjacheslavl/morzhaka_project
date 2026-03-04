import pygame
import random
from constants import (
    TILE_SIZE, ENEMY_SPEED, BOSS_SPEED, BOSS_HEALTH,
    BOSS_PROJECTILE_SIZE, BOSS_SHOOT_INTERVAL,
    FINAL_BOSS_HEALTH, FINAL_BOSS_SPEED,
    SCREEN_WIDTH, SCREEN_HEIGHT, WHITE, RED, DARK_RED, FINAL_BOSS_COLOR
)
from sprites import (
    create_enemy_sprite, create_ice_enemy_sprite,
    create_castle_enemy_fast_sprite, create_castle_enemy_shooter_sprite,
    create_boss_sprite, create_ice_boss_sprite,
    create_final_boss_sprite, create_shadow_boss_sprite
)
from pathfinding import find_path, find_path_for_large_entity
from projectiles import EnemyProjectile, BossProjectile


class Enemy:
    _next_id = 0
    
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.sprite = create_enemy_sprite()
        self.width = self.sprite.get_width()
        self.height = self.sprite.get_height()
        self.speed = ENEMY_SPEED
        self.path = []
        self.path_update_timer = 0
        self.path_update_interval = 30
        self.blink_timer = 0
        self.blink_duration = 6
        self.enemy_id = Enemy._next_id
        Enemy._next_id += 1

    def move_towards_player(self, player, dungeon):
        player_dx = player.x - self.x
        player_dy = player.y - self.y
        player_dist = (player_dx ** 2 + player_dy ** 2) ** 0.5
        
        if player_dist < 60:
            self.circle_around_player(player, dungeon)
            return
        
        self.path_update_timer += 1
        if self.path_update_timer >= self.path_update_interval or not self.path:
            self.path_update_timer = 0
            self.update_path(player, dungeon)
        
        if not self.path:
            self.move_directly_towards(player, dungeon)
            return
        
        target_tile = self.path[0]
        target_x = target_tile[0] * TILE_SIZE + TILE_SIZE // 2 - self.width // 2
        target_y = target_tile[1] * TILE_SIZE + TILE_SIZE // 2 - self.height // 2
        
        dx = target_x - self.x
        dy = target_y - self.y
        distance = (dx ** 2 + dy ** 2) ** 0.5
        
        if distance < self.speed:
            self.x = target_x
            self.y = target_y
            self.path.pop(0)
        else:
            dx = dx / distance
            dy = dy / distance
            new_x = self.x + dx * self.speed
            new_y = self.y + dy * self.speed
            
            if not dungeon.is_wall(new_x, self.y, self.width, self.height):
                self.x = new_x
            if not dungeon.is_wall(self.x, new_y, self.width, self.height):
                self.y = new_y

    def move_directly_towards(self, player, dungeon):
        dx = player.x - self.x
        dy = player.y - self.y
        distance = (dx ** 2 + dy ** 2) ** 0.5
        if distance > 0:
            dx = dx / distance
            dy = dy / distance
            new_x = self.x + dx * self.speed
            new_y = self.y + dy * self.speed
            if not dungeon.is_wall(new_x, self.y, self.width, self.height):
                self.x = new_x
            if not dungeon.is_wall(self.x, new_y, self.width, self.height):
                self.y = new_y

    def would_collide_with_player(self, new_x, new_y, player):
        enemy_rect = pygame.Rect(new_x, new_y, self.width, self.height)
        return enemy_rect.colliderect(player.get_rect())

    def circle_around_player(self, player, dungeon):
        dx = player.x - self.x
        dy = player.y - self.y
        distance = (dx ** 2 + dy ** 2) ** 0.5
        if distance == 0:
            dx, dy = 1.0, 0.0
        else:
            dx = dx / distance
            dy = dy / distance
        
        if (self.enemy_id % 2) == 0:
            perp_x, perp_y = -dy, dx
        else:
            perp_x, perp_y = dy, -dx
        
        close_to_player = distance < 40
        if close_to_player:
            move_x = perp_x
            move_y = perp_y
        else:
            move_x = perp_x * 0.7 + dx * 0.5
            move_y = perp_y * 0.7 + dy * 0.5
        
        new_x = self.x + move_x * self.speed
        new_y = self.y + move_y * self.speed
        
        moved = False
        if not dungeon.is_wall(new_x, self.y, self.width, self.height):
            if not self.would_collide_with_player(new_x, self.y, player):
                self.x = new_x
                moved = True
        if not dungeon.is_wall(self.x, new_y, self.width, self.height):
            if not self.would_collide_with_player(self.x, new_y, player):
                self.y = new_y
                moved = True
        
        if not moved:
            perp_x, perp_y = -perp_x, -perp_y
            if close_to_player:
                move_x = perp_x
                move_y = perp_y
            else:
                move_x = perp_x * 0.7 + dx * 0.5
                move_y = perp_y * 0.7 + dy * 0.5
            new_x = self.x + move_x * self.speed
            new_y = self.y + move_y * self.speed
            if not dungeon.is_wall(new_x, self.y, self.width, self.height):
                if not self.would_collide_with_player(new_x, self.y, player):
                    self.x = new_x
            if not dungeon.is_wall(self.x, new_y, self.width, self.height):
                if not self.would_collide_with_player(self.x, new_y, player):
                    self.y = new_y

    def update_path(self, player, dungeon):
        my_tile = (int((self.x + self.width // 2) // TILE_SIZE),
                   int((self.y + self.height // 2) // TILE_SIZE))
        player_tile = (int((player.x + player.width // 2) // TILE_SIZE),
                       int((player.y + player.height // 2) // TILE_SIZE))

        self.path = find_path(my_tile, player_tile, dungeon.tiles, self.enemy_id)

    def start_blink(self):
        self.blink_timer = self.blink_duration

    def update_blink(self):
        if self.blink_timer > 0:
            self.blink_timer -= 1

    def draw(self, screen):
        if self.blink_timer > 0 and self.blink_timer % 2 == 1:
            return
        screen.blit(self.sprite, (self.x, self.y))

    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)

    def collides_with_player(self, player):
        return self.get_rect().colliderect(player.get_rect())

    def is_touching_player(self, player):
        enemy_rect = self.get_rect().inflate(4, 4)
        return enemy_rect.colliderect(player.get_rect())


class IceEnemy:
    _next_id = 1000
    
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.sprite = create_ice_enemy_sprite()
        self.width = self.sprite.get_width()
        self.height = self.sprite.get_height()
        self.speed = ENEMY_SPEED
        self.path = []
        self.path_update_timer = 0
        self.path_update_interval = 30
        self.shoot_timer = 0
        self.shoot_interval = 420
        self.health = 2
        self.blink_timer = 0
        self.blink_duration = 6
        self.enemy_id = IceEnemy._next_id
        IceEnemy._next_id += 1

    def take_damage(self, amount=1):
        self.health -= amount
        self.start_blink()
        return self.health <= 0

    def start_blink(self):
        self.blink_timer = self.blink_duration

    def update_blink(self):
        if self.blink_timer > 0:
            self.blink_timer -= 1

    def move_towards_player(self, player, dungeon):
        player_dx = player.x - self.x
        player_dy = player.y - self.y
        player_dist = (player_dx ** 2 + player_dy ** 2) ** 0.5
        
        if player_dist < 60:
            self.circle_around_player(player, dungeon)
            return
        
        self.path_update_timer += 1
        if self.path_update_timer >= self.path_update_interval or not self.path:
            self.path_update_timer = 0
            self.update_path(player, dungeon)
        
        if not self.path:
            self.move_directly_towards(player, dungeon)
            return
        
        target_tile = self.path[0]
        target_x = target_tile[0] * TILE_SIZE + TILE_SIZE // 2 - self.width // 2
        target_y = target_tile[1] * TILE_SIZE + TILE_SIZE // 2 - self.height // 2
        
        dx = target_x - self.x
        dy = target_y - self.y
        distance = (dx ** 2 + dy ** 2) ** 0.5
        
        if distance < self.speed:
            self.x = target_x
            self.y = target_y
            self.path.pop(0)
        else:
            dx = dx / distance
            dy = dy / distance
            new_x = self.x + dx * self.speed
            new_y = self.y + dy * self.speed
            
            if not dungeon.is_wall(new_x, self.y, self.width, self.height):
                self.x = new_x
            if not dungeon.is_wall(self.x, new_y, self.width, self.height):
                self.y = new_y

    def move_directly_towards(self, player, dungeon):
        dx = player.x - self.x
        dy = player.y - self.y
        distance = (dx ** 2 + dy ** 2) ** 0.5
        if distance > 0:
            dx = dx / distance
            dy = dy / distance
            new_x = self.x + dx * self.speed
            new_y = self.y + dy * self.speed
            if not dungeon.is_wall(new_x, self.y, self.width, self.height):
                self.x = new_x
            if not dungeon.is_wall(self.x, new_y, self.width, self.height):
                self.y = new_y

    def would_collide_with_player(self, new_x, new_y, player):
        enemy_rect = pygame.Rect(new_x, new_y, self.width, self.height)
        return enemy_rect.colliderect(player.get_rect())

    def circle_around_player(self, player, dungeon):
        dx = player.x - self.x
        dy = player.y - self.y
        distance = (dx ** 2 + dy ** 2) ** 0.5
        if distance == 0:
            dx, dy = 1.0, 0.0
        else:
            dx = dx / distance
            dy = dy / distance
        
        if (self.enemy_id % 2) == 0:
            perp_x, perp_y = -dy, dx
        else:
            perp_x, perp_y = dy, -dx
        
        close_to_player = distance < 40
        if close_to_player:
            move_x = perp_x
            move_y = perp_y
        else:
            move_x = perp_x * 0.7 + dx * 0.5
            move_y = perp_y * 0.7 + dy * 0.5
        
        new_x = self.x + move_x * self.speed
        new_y = self.y + move_y * self.speed
        
        moved = False
        if not dungeon.is_wall(new_x, self.y, self.width, self.height):
            if not self.would_collide_with_player(new_x, self.y, player):
                self.x = new_x
                moved = True
        if not dungeon.is_wall(self.x, new_y, self.width, self.height):
            if not self.would_collide_with_player(self.x, new_y, player):
                self.y = new_y
                moved = True
        
        if not moved:
            perp_x, perp_y = -perp_x, -perp_y
            if close_to_player:
                move_x = perp_x
                move_y = perp_y
            else:
                move_x = perp_x * 0.7 + dx * 0.5
                move_y = perp_y * 0.7 + dy * 0.5
            new_x = self.x + move_x * self.speed
            new_y = self.y + move_y * self.speed
            if not dungeon.is_wall(new_x, self.y, self.width, self.height):
                if not self.would_collide_with_player(new_x, self.y, player):
                    self.x = new_x
            if not dungeon.is_wall(self.x, new_y, self.width, self.height):
                if not self.would_collide_with_player(self.x, new_y, player):
                    self.y = new_y

    def update_path(self, player, dungeon):
        my_tile = (int((self.x + self.width // 2) // TILE_SIZE),
                   int((self.y + self.height // 2) // TILE_SIZE))
        player_tile = (int((player.x + player.width // 2) // TILE_SIZE),
                       int((player.y + player.height // 2) // TILE_SIZE))
        
        self.path = find_path(my_tile, player_tile, dungeon.tiles, self.enemy_id)

    def shoot_at_player(self, player):
        self.shoot_timer += 1
        if self.shoot_timer >= self.shoot_interval:
            self.shoot_timer = 0
            
            my_center_x = self.x + self.width // 2
            my_center_y = self.y + self.height // 2
            player_center_x = player.x + player.width // 2
            player_center_y = player.y + player.height // 2
            
            dx = player_center_x - my_center_x
            dy = player_center_y - my_center_y
            distance = (dx ** 2 + dy ** 2) ** 0.5
            
            if distance > 0:
                dx = dx / distance
                dy = dy / distance
                
                proj_x = my_center_x - 4
                proj_y = my_center_y - 4
                return EnemyProjectile(proj_x, proj_y, (dx, dy))
        return None

    def draw(self, screen):
        if self.blink_timer > 0 and self.blink_timer % 2 == 1:
            return
        screen.blit(self.sprite, (self.x, self.y))

    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)

    def collides_with_player(self, player):
        return self.get_rect().colliderect(player.get_rect())

    def is_touching_player(self, player):
        enemy_rect = self.get_rect().inflate(4, 4)
        return enemy_rect.colliderect(player.get_rect())


class CastleEnemyFast:
    """Light gray fast castle enemy with 2 HP."""
    _next_id = 2000
    
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.sprite = create_castle_enemy_fast_sprite()
        self.width = self.sprite.get_width()
        self.height = self.sprite.get_height()
        self.speed = ENEMY_SPEED * 1.15
        self.path = []
        self.path_update_timer = 0
        self.path_update_interval = 25
        self.health = 2
        self.blink_timer = 0
        self.blink_duration = 6
        self.enemy_id = CastleEnemyFast._next_id
        CastleEnemyFast._next_id += 1

    def take_damage(self, amount=1):
        self.health -= amount
        self.start_blink()
        return self.health <= 0

    def start_blink(self):
        self.blink_timer = self.blink_duration

    def update_blink(self):
        if self.blink_timer > 0:
            self.blink_timer -= 1

    def move_towards_player(self, player, dungeon):
        player_dx = player.x - self.x
        player_dy = player.y - self.y
        player_dist = (player_dx ** 2 + player_dy ** 2) ** 0.5
        
        if player_dist < 60:
            self.circle_around_player(player, dungeon)
            return
        
        self.path_update_timer += 1
        if self.path_update_timer >= self.path_update_interval or not self.path:
            self.path_update_timer = 0
            self.update_path(player, dungeon)
        
        if not self.path:
            self.move_directly_towards(player, dungeon)
            return
        
        target_tile = self.path[0]
        target_x = target_tile[0] * TILE_SIZE + TILE_SIZE // 2 - self.width // 2
        target_y = target_tile[1] * TILE_SIZE + TILE_SIZE // 2 - self.height // 2
        
        dx = target_x - self.x
        dy = target_y - self.y
        distance = (dx ** 2 + dy ** 2) ** 0.5
        
        if distance < self.speed:
            self.x = target_x
            self.y = target_y
            self.path.pop(0)
        else:
            dx = dx / distance
            dy = dy / distance
            new_x = self.x + dx * self.speed
            new_y = self.y + dy * self.speed
            
            if not dungeon.is_wall(new_x, self.y, self.width, self.height):
                self.x = new_x
            if not dungeon.is_wall(self.x, new_y, self.width, self.height):
                self.y = new_y

    def move_directly_towards(self, player, dungeon):
        dx = player.x - self.x
        dy = player.y - self.y
        distance = (dx ** 2 + dy ** 2) ** 0.5
        if distance > 0:
            dx = dx / distance
            dy = dy / distance
            new_x = self.x + dx * self.speed
            new_y = self.y + dy * self.speed
            if not dungeon.is_wall(new_x, self.y, self.width, self.height):
                self.x = new_x
            if not dungeon.is_wall(self.x, new_y, self.width, self.height):
                self.y = new_y

    def would_collide_with_player(self, new_x, new_y, player):
        enemy_rect = pygame.Rect(new_x, new_y, self.width, self.height)
        return enemy_rect.colliderect(player.get_rect())

    def circle_around_player(self, player, dungeon):
        dx = player.x - self.x
        dy = player.y - self.y
        distance = (dx ** 2 + dy ** 2) ** 0.5
        if distance == 0:
            dx, dy = 1.0, 0.0
        else:
            dx = dx / distance
            dy = dy / distance
        
        if (self.enemy_id % 2) == 0:
            perp_x, perp_y = -dy, dx
        else:
            perp_x, perp_y = dy, -dx
        
        close_to_player = distance < 40
        if close_to_player:
            move_x = perp_x
            move_y = perp_y
        else:
            move_x = perp_x * 0.7 + dx * 0.5
            move_y = perp_y * 0.7 + dy * 0.5
        
        new_x = self.x + move_x * self.speed
        new_y = self.y + move_y * self.speed
        
        moved = False
        if not dungeon.is_wall(new_x, self.y, self.width, self.height):
            if not self.would_collide_with_player(new_x, self.y, player):
                self.x = new_x
                moved = True
        if not dungeon.is_wall(self.x, new_y, self.width, self.height):
            if not self.would_collide_with_player(self.x, new_y, player):
                self.y = new_y
                moved = True
        
        if not moved:
            perp_x, perp_y = -perp_x, -perp_y
            if close_to_player:
                move_x = perp_x
                move_y = perp_y
            else:
                move_x = perp_x * 0.7 + dx * 0.5
                move_y = perp_y * 0.7 + dy * 0.5
            new_x = self.x + move_x * self.speed
            new_y = self.y + move_y * self.speed
            if not dungeon.is_wall(new_x, self.y, self.width, self.height):
                if not self.would_collide_with_player(new_x, self.y, player):
                    self.x = new_x
            if not dungeon.is_wall(self.x, new_y, self.width, self.height):
                if not self.would_collide_with_player(self.x, new_y, player):
                    self.y = new_y

    def update_path(self, player, dungeon):
        my_tile = (int((self.x + self.width // 2) // TILE_SIZE),
                   int((self.y + self.height // 2) // TILE_SIZE))
        player_tile = (int((player.x + player.width // 2) // TILE_SIZE),
                       int((player.y + player.height // 2) // TILE_SIZE))
        self.path = find_path(my_tile, player_tile, dungeon.tiles, self.enemy_id)

    def draw(self, screen):
        if self.blink_timer > 0 and self.blink_timer % 2 == 1:
            return
        screen.blit(self.sprite, (self.x, self.y))

    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)

    def collides_with_player(self, player):
        return self.get_rect().colliderect(player.get_rect())

    def is_touching_player(self, player):
        enemy_rect = self.get_rect().inflate(4, 4)
        return enemy_rect.colliderect(player.get_rect())


class CastleEnemyShooter:
    """Dark gray shooter castle enemy with 2 HP, shoots every 8 seconds."""
    _next_id = 3000
    
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.sprite = create_castle_enemy_shooter_sprite()
        self.width = self.sprite.get_width()
        self.height = self.sprite.get_height()
        self.speed = ENEMY_SPEED
        self.path = []
        self.path_update_timer = 0
        self.path_update_interval = 30
        self.shoot_timer = 0
        self.shoot_interval = 480
        self.health = 2
        self.blink_timer = 0
        self.blink_duration = 6
        self.enemy_id = CastleEnemyShooter._next_id
        CastleEnemyShooter._next_id += 1

    def take_damage(self, amount=1):
        self.health -= amount
        self.start_blink()
        return self.health <= 0

    def start_blink(self):
        self.blink_timer = self.blink_duration

    def update_blink(self):
        if self.blink_timer > 0:
            self.blink_timer -= 1

    def move_towards_player(self, player, dungeon):
        player_dx = player.x - self.x
        player_dy = player.y - self.y
        player_dist = (player_dx ** 2 + player_dy ** 2) ** 0.5
        
        if player_dist < 60:
            self.circle_around_player(player, dungeon)
            return
        
        self.path_update_timer += 1
        if self.path_update_timer >= self.path_update_interval or not self.path:
            self.path_update_timer = 0
            self.update_path(player, dungeon)
        
        if not self.path:
            self.move_directly_towards(player, dungeon)
            return
        
        target_tile = self.path[0]
        target_x = target_tile[0] * TILE_SIZE + TILE_SIZE // 2 - self.width // 2
        target_y = target_tile[1] * TILE_SIZE + TILE_SIZE // 2 - self.height // 2
        
        dx = target_x - self.x
        dy = target_y - self.y
        distance = (dx ** 2 + dy ** 2) ** 0.5
        
        if distance < self.speed:
            self.x = target_x
            self.y = target_y
            self.path.pop(0)
        else:
            dx = dx / distance
            dy = dy / distance
            new_x = self.x + dx * self.speed
            new_y = self.y + dy * self.speed
            
            if not dungeon.is_wall(new_x, self.y, self.width, self.height):
                self.x = new_x
            if not dungeon.is_wall(self.x, new_y, self.width, self.height):
                self.y = new_y

    def move_directly_towards(self, player, dungeon):
        dx = player.x - self.x
        dy = player.y - self.y
        distance = (dx ** 2 + dy ** 2) ** 0.5
        if distance > 0:
            dx = dx / distance
            dy = dy / distance
            new_x = self.x + dx * self.speed
            new_y = self.y + dy * self.speed
            if not dungeon.is_wall(new_x, self.y, self.width, self.height):
                self.x = new_x
            if not dungeon.is_wall(self.x, new_y, self.width, self.height):
                self.y = new_y

    def would_collide_with_player(self, new_x, new_y, player):
        enemy_rect = pygame.Rect(new_x, new_y, self.width, self.height)
        return enemy_rect.colliderect(player.get_rect())

    def circle_around_player(self, player, dungeon):
        dx = player.x - self.x
        dy = player.y - self.y
        distance = (dx ** 2 + dy ** 2) ** 0.5
        if distance == 0:
            dx, dy = 1.0, 0.0
        else:
            dx = dx / distance
            dy = dy / distance
        
        if (self.enemy_id % 2) == 0:
            perp_x, perp_y = -dy, dx
        else:
            perp_x, perp_y = dy, -dx
        
        close_to_player = distance < 40
        if close_to_player:
            move_x = perp_x
            move_y = perp_y
        else:
            move_x = perp_x * 0.7 + dx * 0.5
            move_y = perp_y * 0.7 + dy * 0.5
        
        new_x = self.x + move_x * self.speed
        new_y = self.y + move_y * self.speed
        
        moved = False
        if not dungeon.is_wall(new_x, self.y, self.width, self.height):
            if not self.would_collide_with_player(new_x, self.y, player):
                self.x = new_x
                moved = True
        if not dungeon.is_wall(self.x, new_y, self.width, self.height):
            if not self.would_collide_with_player(self.x, new_y, player):
                self.y = new_y
                moved = True
        
        if not moved:
            perp_x, perp_y = -perp_x, -perp_y
            if close_to_player:
                move_x = perp_x
                move_y = perp_y
            else:
                move_x = perp_x * 0.7 + dx * 0.5
                move_y = perp_y * 0.7 + dy * 0.5
            new_x = self.x + move_x * self.speed
            new_y = self.y + move_y * self.speed
            if not dungeon.is_wall(new_x, self.y, self.width, self.height):
                if not self.would_collide_with_player(new_x, self.y, player):
                    self.x = new_x
            if not dungeon.is_wall(self.x, new_y, self.width, self.height):
                if not self.would_collide_with_player(self.x, new_y, player):
                    self.y = new_y

    def update_path(self, player, dungeon):
        my_tile = (int((self.x + self.width // 2) // TILE_SIZE),
                   int((self.y + self.height // 2) // TILE_SIZE))
        player_tile = (int((player.x + player.width // 2) // TILE_SIZE),
                       int((player.y + player.height // 2) // TILE_SIZE))
        self.path = find_path(my_tile, player_tile, dungeon.tiles, self.enemy_id)

    def shoot_at_player(self, player):
        self.shoot_timer += 1
        if self.shoot_timer >= self.shoot_interval:
            self.shoot_timer = 0
            
            my_center_x = self.x + self.width // 2
            my_center_y = self.y + self.height // 2
            player_center_x = player.x + player.width // 2
            player_center_y = player.y + player.height // 2
            
            dx = player_center_x - my_center_x
            dy = player_center_y - my_center_y
            distance = (dx ** 2 + dy ** 2) ** 0.5
            
            if distance > 0:
                dx = dx / distance
                dy = dy / distance
                
                proj_x = my_center_x - 4
                proj_y = my_center_y - 4
                return EnemyProjectile(proj_x, proj_y, (dx, dy))
        return None

    def draw(self, screen):
        if self.blink_timer > 0 and self.blink_timer % 2 == 1:
            return
        screen.blit(self.sprite, (self.x, self.y))

    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)

    def collides_with_player(self, player):
        return self.get_rect().colliderect(player.get_rect())

    def is_touching_player(self, player):
        enemy_rect = self.get_rect().inflate(4, 4)
        return enemy_rect.colliderect(player.get_rect())


class Boss:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.sprite = create_boss_sprite()
        self.width = self.sprite.get_width()
        self.height = self.sprite.get_height()
        self.speed = BOSS_SPEED
        self.max_health = BOSS_HEALTH
        self.health = self.max_health
        self.shoot_timer = 0
        self.shoot_interval = BOSS_SHOOT_INTERVAL
        self.teleport_timer = 0
        self.teleport_interval = 300
        self.blink_timer = 0
        self.blink_duration = 8
        self.path = []
        self.path_update_timer = 0
        self.path_update_interval = 15

    def teleport(self, player, dungeon):
        self.teleport_timer += 1
        if self.teleport_timer < self.teleport_interval:
            return
        
        self.teleport_timer = 0
        
        valid_positions = []
        for tile_y in range(len(dungeon.tiles)):
            for tile_x in range(len(dungeon.tiles[0])):
                if dungeon.tiles[tile_y][tile_x] == 0:
                    pos_x = tile_x * TILE_SIZE
                    pos_y = tile_y * TILE_SIZE
                    
                    if not dungeon.is_wall(pos_x, pos_y, self.width, self.height):
                        dist_to_player = ((pos_x - player.x) ** 2 + (pos_y - player.y) ** 2) ** 0.5
                        if dist_to_player > 150:
                            valid_positions.append((pos_x, pos_y))
        
        if valid_positions:
            new_pos = random.choice(valid_positions)
            self.x = new_pos[0]
            self.y = new_pos[1]

    def update_path(self, player, dungeon):
        my_tile = (int((self.x + self.width // 2) // TILE_SIZE),
                   int((self.y + self.height // 2) // TILE_SIZE))
        player_tile = (int((player.x + player.width // 2) // TILE_SIZE),
                       int((player.y + player.height // 2) // TILE_SIZE))
        self.path = find_path_for_large_entity(
            my_tile, player_tile, dungeon.tiles, TILE_SIZE, self.width, self.height
        )

    def move_towards_player(self, player, dungeon):
        dx = player.x - self.x
        dy = player.y - self.y
        distance = (dx ** 2 + dy ** 2) ** 0.5
        
        if distance < 100:
            return
        
        self.path_update_timer += 1
        if self.path_update_timer >= self.path_update_interval or not self.path:
            self.path_update_timer = 0
            self.update_path(player, dungeon)
        
        if not self.path:
            self._move_directly_towards(player, dungeon)
            return
        
        target_tile = self.path[0]
        target_x = target_tile[0] * TILE_SIZE
        target_y = target_tile[1] * TILE_SIZE
        
        dx = target_x - self.x
        dy = target_y - self.y
        dist_to_target = (dx ** 2 + dy ** 2) ** 0.5
        
        if dist_to_target < self.speed * 2:
            self.path.pop(0)
        
        if dist_to_target > 0:
            dx = dx / dist_to_target
            dy = dy / dist_to_target
            new_x = self.x + dx * self.speed
            new_y = self.y + dy * self.speed
            
            moved = False
            if not dungeon.is_wall(new_x, new_y, self.width, self.height):
                self.x = new_x
                self.y = new_y
                moved = True
            else:
                if not dungeon.is_wall(new_x, self.y, self.width, self.height):
                    self.x = new_x
                    moved = True
                if not dungeon.is_wall(self.x, new_y, self.width, self.height):
                    self.y = new_y
                    moved = True
            
            if not moved:
                self.path = []

    def _move_directly_towards(self, player, dungeon):
        dx = player.x - self.x
        dy = player.y - self.y
        distance = (dx ** 2 + dy ** 2) ** 0.5
        if distance > 0:
            dx = dx / distance
            dy = dy / distance
            new_x = self.x + dx * self.speed
            new_y = self.y + dy * self.speed
            if not dungeon.is_wall(new_x, self.y, self.width, self.height):
                self.x = new_x
            if not dungeon.is_wall(self.x, new_y, self.width, self.height):
                self.y = new_y

    def shoot_at_player(self, player):
        self.shoot_timer += 1
        if self.shoot_timer >= self.shoot_interval:
            self.shoot_timer = 0
            
            my_center_x = self.x + self.width // 2
            my_center_y = self.y + self.height // 2
            player_center_x = player.x + player.width // 2
            player_center_y = player.y + player.height // 2
            
            dx = player_center_x - my_center_x
            dy = player_center_y - my_center_y
            distance = (dx ** 2 + dy ** 2) ** 0.5
            
            if distance > 0:
                dx = dx / distance
                dy = dy / distance
                
                proj_x = my_center_x - BOSS_PROJECTILE_SIZE // 2
                proj_y = my_center_y - BOSS_PROJECTILE_SIZE // 2
                return BossProjectile(proj_x, proj_y, (dx, dy))
        return None

    def take_damage(self, amount=1):
        self.health -= amount
        self.start_blink()
        return self.health <= 0

    def start_blink(self):
        self.blink_timer = self.blink_duration

    def update_blink(self):
        if self.blink_timer > 0:
            self.blink_timer -= 1

    def draw(self, screen):
        bar_width = self.width
        bar_height = 8
        bar_x = self.x
        bar_y = self.y - 15
        
        pygame.draw.rect(screen, DARK_RED, (bar_x, bar_y, bar_width, bar_height))
        health_width = int(bar_width * (self.health / self.max_health))
        pygame.draw.rect(screen, RED, (bar_x, bar_y, health_width, bar_height))
        pygame.draw.rect(screen, WHITE, (bar_x, bar_y, bar_width, bar_height), 1)
        
        if self.blink_timer > 0 and self.blink_timer % 2 == 1:
            return
        screen.blit(self.sprite, (self.x, self.y))

    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)

    def collides_with_player(self, player):
        return self.get_rect().colliderect(player.get_rect())

    def is_touching_player(self, player):
        boss_rect = self.get_rect().inflate(4, 4)
        return boss_rect.colliderect(player.get_rect())


class IceBoss:
    """Ice cave boss with 50 HP."""
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.sprite = create_ice_boss_sprite()
        self.width = self.sprite.get_width()
        self.height = self.sprite.get_height()
        self.speed = BOSS_SPEED
        self.max_health = 50
        self.health = self.max_health
        self.shoot_timer = 0
        self.shoot_interval = BOSS_SHOOT_INTERVAL
        self.teleport_timer = 0
        self.teleport_interval = 250
        self.blink_timer = 0
        self.blink_duration = 8
        self.path = []
        self.path_update_timer = 0
        self.path_update_interval = 15

    def teleport(self, player, dungeon):
        self.teleport_timer += 1
        if self.teleport_timer < self.teleport_interval:
            return

        self.teleport_timer = 0

        valid_positions = []
        for tile_y in range(len(dungeon.tiles)):
            for tile_x in range(len(dungeon.tiles[0])):
                if dungeon.tiles[tile_y][tile_x] == 0:
                    pos_x = tile_x * TILE_SIZE
                    pos_y = tile_y * TILE_SIZE
                    
                    if pos_x + self.width <= SCREEN_WIDTH and pos_y + self.height <= SCREEN_HEIGHT:
                        dist_to_player = ((pos_x - player.x)**2 + (pos_y - player.y)**2)**0.5
                        if dist_to_player > 150:
                            valid_positions.append((pos_x, pos_y))

        if valid_positions:
            new_pos = random.choice(valid_positions)
            self.x, self.y = new_pos

    def update_path(self, player, dungeon):
        my_tile = (int((self.x + self.width // 2) // TILE_SIZE),
                   int((self.y + self.height // 2) // TILE_SIZE))
        player_tile = (int((player.x + player.width // 2) // TILE_SIZE),
                       int((player.y + player.height // 2) // TILE_SIZE))
        self.path = find_path_for_large_entity(
            my_tile, player_tile, dungeon.tiles, TILE_SIZE, self.width, self.height
        )

    def move_towards_player(self, player, dungeon):
        dx = player.x - self.x
        dy = player.y - self.y
        distance = (dx ** 2 + dy ** 2) ** 0.5

        if distance < 100:
            return

        self.path_update_timer += 1
        if self.path_update_timer >= self.path_update_interval or not self.path:
            self.path_update_timer = 0
            self.update_path(player, dungeon)

        if not self.path:
            self._move_directly_towards(player, dungeon)
            return

        target_tile = self.path[0]
        target_x = target_tile[0] * TILE_SIZE
        target_y = target_tile[1] * TILE_SIZE

        dx = target_x - self.x
        dy = target_y - self.y
        dist_to_target = (dx ** 2 + dy ** 2) ** 0.5

        if dist_to_target < self.speed * 2:
            self.path.pop(0)

        if dist_to_target > 0:
            dx = dx / dist_to_target
            dy = dy / dist_to_target
            new_x = self.x + dx * self.speed
            new_y = self.y + dy * self.speed

            moved = False
            if not dungeon.is_wall(new_x, new_y, self.width, self.height):
                self.x = new_x
                self.y = new_y
                moved = True
            else:
                if not dungeon.is_wall(new_x, self.y, self.width, self.height):
                    self.x = new_x
                    moved = True
                if not dungeon.is_wall(self.x, new_y, self.width, self.height):
                    self.y = new_y
                    moved = True

            if not moved:
                self.path = []

    def _move_directly_towards(self, player, dungeon):
        dx = player.x - self.x
        dy = player.y - self.y
        distance = (dx ** 2 + dy ** 2) ** 0.5
        if distance > 0:
            dx = dx / distance
            dy = dy / distance
            new_x = self.x + dx * self.speed
            new_y = self.y + dy * self.speed
            if not dungeon.is_wall(new_x, self.y, self.width, self.height):
                self.x = new_x
            if not dungeon.is_wall(self.x, new_y, self.width, self.height):
                self.y = new_y

    def shoot_at_player(self, player):
        self.shoot_timer += 1
        if self.shoot_timer >= self.shoot_interval:
            self.shoot_timer = 0

            my_center_x = self.x + self.width // 2
            my_center_y = self.y + self.height // 2
            player_center_x = player.x + player.width // 2
            player_center_y = player.y + player.height // 2

            dx = player_center_x - my_center_x
            dy = player_center_y - my_center_y
            distance = (dx ** 2 + dy ** 2) ** 0.5

            if distance > 0:
                dx = dx / distance
                dy = dy / distance

                proj_x = my_center_x - BOSS_PROJECTILE_SIZE // 2
                proj_y = my_center_y - BOSS_PROJECTILE_SIZE // 2
                return BossProjectile(proj_x, proj_y, (dx, dy))
        return None

    def take_damage(self, amount=1):
        self.health -= amount
        self.start_blink()
        return self.health <= 0

    def start_blink(self):
        self.blink_timer = self.blink_duration

    def update_blink(self):
        if self.blink_timer > 0:
            self.blink_timer -= 1

    def draw(self, screen):
        if self.blink_timer > 0 and self.blink_timer % 2 == 1:
            return
        screen.blit(self.sprite, (self.x, self.y))

        bar_width = self.width
        bar_height = 8
        bar_x = self.x
        bar_y = self.y - 15

        pygame.draw.rect(screen, (60, 60, 60), (bar_x, bar_y, bar_width, bar_height))

        health_ratio = self.health / self.max_health
        health_width = int(bar_width * health_ratio)
        pygame.draw.rect(screen, (148, 80, 200), (bar_x, bar_y, health_width, bar_height))

        pygame.draw.rect(screen, WHITE, (bar_x, bar_y, bar_width, bar_height), 1)

    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)

    def collides_with_player(self, player):
        return self.get_rect().colliderect(player.get_rect())

    def is_touching_player(self, player):
        boss_rect = self.get_rect().inflate(4, 4)
        return boss_rect.colliderect(player.get_rect())


class FinalBoss:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.sprite = create_final_boss_sprite()
        self.width = self.sprite.get_width()
        self.height = self.sprite.get_height()
        self.speed = FINAL_BOSS_SPEED
        self.max_health = FINAL_BOSS_HEALTH
        self.health = self.max_health
        self.spawn_timer = 0
        self.spawn_interval = 300
        self.teleport_timer = 0
        self.teleport_interval = 180
        self.blink_timer = 0
        self.blink_duration = 8
        self.path = []
        self.path_update_timer = 0
        self.path_update_interval = 15

    def teleport(self, player, dungeon):
        self.teleport_timer += 1
        if self.teleport_timer < self.teleport_interval:
            return
        
        self.teleport_timer = 0
        
        valid_positions = []
        for tile_y in range(len(dungeon.tiles)):
            for tile_x in range(len(dungeon.tiles[0])):
                if dungeon.tiles[tile_y][tile_x] == 0:
                    pos_x = tile_x * TILE_SIZE
                    pos_y = tile_y * TILE_SIZE
                    
                    if not dungeon.is_wall(pos_x, pos_y, self.width, self.height):
                        dist_to_player = ((pos_x - player.x) ** 2 + (pos_y - player.y) ** 2) ** 0.5
                        if dist_to_player > 150:
                            valid_positions.append((pos_x, pos_y))
        
        if valid_positions:
            new_pos = random.choice(valid_positions)
            self.x = new_pos[0]
            self.y = new_pos[1]

    def update_path(self, player, dungeon):
        my_tile = (int((self.x + self.width // 2) // TILE_SIZE),
                   int((self.y + self.height // 2) // TILE_SIZE))
        player_tile = (int((player.x + player.width // 2) // TILE_SIZE),
                       int((player.y + player.height // 2) // TILE_SIZE))
        self.path = find_path_for_large_entity(
            my_tile, player_tile, dungeon.tiles, TILE_SIZE, self.width, self.height
        )

    def move_towards_player(self, player, dungeon):
        dx = player.x - self.x
        dy = player.y - self.y
        distance = (dx ** 2 + dy ** 2) ** 0.5
        
        if distance < 80:
            return
        
        self.path_update_timer += 1
        if self.path_update_timer >= self.path_update_interval or not self.path:
            self.path_update_timer = 0
            self.update_path(player, dungeon)
        
        if not self.path:
            self._move_directly_towards(player, dungeon)
            return
        
        target_tile = self.path[0]
        target_x = target_tile[0] * TILE_SIZE
        target_y = target_tile[1] * TILE_SIZE
        
        dx = target_x - self.x
        dy = target_y - self.y
        dist_to_target = (dx ** 2 + dy ** 2) ** 0.5
        
        if dist_to_target < self.speed * 2:
            self.path.pop(0)
        
        if dist_to_target > 0:
            dx = dx / dist_to_target
            dy = dy / dist_to_target
            new_x = self.x + dx * self.speed
            new_y = self.y + dy * self.speed
            
            moved = False
            if not dungeon.is_wall(new_x, new_y, self.width, self.height):
                self.x = new_x
                self.y = new_y
                moved = True
            else:
                if not dungeon.is_wall(new_x, self.y, self.width, self.height):
                    self.x = new_x
                    moved = True
                if not dungeon.is_wall(self.x, new_y, self.width, self.height):
                    self.y = new_y
                    moved = True
            
            if not moved:
                self.path = []

    def _move_directly_towards(self, player, dungeon):
        dx = player.x - self.x
        dy = player.y - self.y
        distance = (dx ** 2 + dy ** 2) ** 0.5
        if distance > 0:
            dx = dx / distance
            dy = dy / distance
            new_x = self.x + dx * self.speed
            new_y = self.y + dy * self.speed
            if not dungeon.is_wall(new_x, self.y, self.width, self.height):
                self.x = new_x
            if not dungeon.is_wall(self.x, new_y, self.width, self.height):
                self.y = new_y

    def should_spawn_enemy(self):
        self.spawn_timer += 1
        if self.spawn_timer >= self.spawn_interval:
            self.spawn_timer = 0
            return True
        return False
    
    def get_spawn_position(self, dungeon):
        valid_positions = []
        for tile_y in range(len(dungeon.tiles)):
            for tile_x in range(len(dungeon.tiles[0])):
                if dungeon.tiles[tile_y][tile_x] == 0:
                    pos_x = tile_x * TILE_SIZE + 4
                    pos_y = tile_y * TILE_SIZE + 4
                    dist_to_boss = ((pos_x - self.x) ** 2 + (pos_y - self.y) ** 2) ** 0.5
                    if dist_to_boss < 150 and dist_to_boss > 50:
                        valid_positions.append((pos_x, pos_y))
        
        if valid_positions:
            return random.choice(valid_positions)
        return None

    def take_damage(self, amount=1):
        self.health -= amount
        self.start_blink()
        return self.health <= 0

    def start_blink(self):
        self.blink_timer = self.blink_duration

    def update_blink(self):
        if self.blink_timer > 0:
            self.blink_timer -= 1

    def draw(self, screen):
        bar_width = self.width
        bar_height = 10
        bar_x = self.x
        bar_y = self.y - 18
        
        pygame.draw.rect(screen, (50, 0, 50), (bar_x, bar_y, bar_width, bar_height))
        health_width = int(bar_width * (self.health / self.max_health))
        pygame.draw.rect(screen, FINAL_BOSS_COLOR, (bar_x, bar_y, health_width, bar_height))
        pygame.draw.rect(screen, WHITE, (bar_x, bar_y, bar_width, bar_height), 1)
        
        if self.blink_timer > 0 and self.blink_timer % 2 == 1:
            return
        screen.blit(self.sprite, (self.x, self.y))

    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)

    def collides_with_player(self, player):
        return self.get_rect().colliderect(player.get_rect())

    def is_touching_player(self, player):
        boss_rect = self.get_rect().inflate(4, 4)
        return boss_rect.colliderect(player.get_rect())


class ShadowBoss:
    """Shadow Lord boss for the castle - 150 HP, fast and aggressive."""
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.sprite = create_shadow_boss_sprite()
        self.width = self.sprite.get_width()
        self.height = self.sprite.get_height()
        self.speed = BOSS_SPEED * 1.3
        self.max_health = 150
        self.health = self.max_health
        self.shoot_timer = 0
        self.shoot_interval = 40
        self.teleport_timer = 0
        self.teleport_interval = 180
        self.blink_timer = 0
        self.blink_duration = 8
        self.phase = 1
        self.path = []
        self.path_update_timer = 0
        self.path_update_interval = 12

    def teleport(self, player, dungeon):
        self.teleport_timer += 1
        if self.teleport_timer < self.teleport_interval:
            return

        self.teleport_timer = 0

        valid_positions = []
        for tile_y in range(len(dungeon.tiles)):
            for tile_x in range(len(dungeon.tiles[0])):
                if dungeon.tiles[tile_y][tile_x] == 0:
                    pos_x = tile_x * TILE_SIZE
                    pos_y = tile_y * TILE_SIZE

                    if pos_x + self.width <= SCREEN_WIDTH and pos_y + self.height <= SCREEN_HEIGHT:
                        dist_to_player = ((pos_x - player.x)**2 + (pos_y - player.y)**2)**0.5
                        if dist_to_player > 100 and dist_to_player < 300:
                            valid_positions.append((pos_x, pos_y))

        if valid_positions:
            new_pos = random.choice(valid_positions)
            self.x, self.y = new_pos

    def update_path(self, player, dungeon):
        my_tile = (int((self.x + self.width // 2) // TILE_SIZE),
                   int((self.y + self.height // 2) // TILE_SIZE))
        player_tile = (int((player.x + player.width // 2) // TILE_SIZE),
                       int((player.y + player.height // 2) // TILE_SIZE))
        self.path = find_path_for_large_entity(
            my_tile, player_tile, dungeon.tiles, TILE_SIZE, self.width, self.height
        )

    def move_towards_player(self, player, dungeon):
        dx = player.x - self.x
        dy = player.y - self.y
        distance = (dx ** 2 + dy ** 2) ** 0.5

        if distance < 80:
            return

        self.path_update_timer += 1
        if self.path_update_timer >= self.path_update_interval or not self.path:
            self.path_update_timer = 0
            self.update_path(player, dungeon)

        if not self.path:
            self._move_directly_towards(player, dungeon)
            return

        speed = self.speed if self.phase == 1 else self.speed * 1.2

        target_tile = self.path[0]
        target_x = target_tile[0] * TILE_SIZE
        target_y = target_tile[1] * TILE_SIZE

        dx = target_x - self.x
        dy = target_y - self.y
        dist_to_target = (dx ** 2 + dy ** 2) ** 0.5

        if dist_to_target < speed * 2:
            self.path.pop(0)

        if dist_to_target > 0:
            dx = dx / dist_to_target
            dy = dy / dist_to_target
            new_x = self.x + dx * speed
            new_y = self.y + dy * speed

            moved = False
            if not dungeon.is_wall(new_x, new_y, self.width, self.height):
                self.x = new_x
                self.y = new_y
                moved = True
            else:
                if not dungeon.is_wall(new_x, self.y, self.width, self.height):
                    self.x = new_x
                    moved = True
                if not dungeon.is_wall(self.x, new_y, self.width, self.height):
                    self.y = new_y
                    moved = True

            if not moved:
                self.path = []

    def _move_directly_towards(self, player, dungeon):
        dx = player.x - self.x
        dy = player.y - self.y
        distance = (dx ** 2 + dy ** 2) ** 0.5
        if distance > 0:
            dx = dx / distance
            dy = dy / distance
            speed = self.speed if self.phase == 1 else self.speed * 1.2
            new_x = self.x + dx * speed
            new_y = self.y + dy * speed
            if not dungeon.is_wall(new_x, self.y, self.width, self.height):
                self.x = new_x
            if not dungeon.is_wall(self.x, new_y, self.width, self.height):
                self.y = new_y

    def shoot_at_player(self, player):
        self.shoot_timer += 1
        interval = self.shoot_interval if self.phase == 1 else self.shoot_interval // 2
        if self.shoot_timer >= interval:
            self.shoot_timer = 0

            my_center_x = self.x + self.width // 2
            my_center_y = self.y + self.height // 2
            player_center_x = player.x + player.width // 2
            player_center_y = player.y + player.height // 2

            dx = player_center_x - my_center_x
            dy = player_center_y - my_center_y
            distance = (dx ** 2 + dy ** 2) ** 0.5

            if distance > 0:
                dx = dx / distance
                dy = dy / distance

                proj_x = my_center_x - BOSS_PROJECTILE_SIZE // 2
                proj_y = my_center_y - BOSS_PROJECTILE_SIZE // 2
                return BossProjectile(proj_x, proj_y, (dx, dy))
        return None

    def take_damage(self, amount=1):
        self.health -= amount
        self.start_blink()
        if self.health <= self.max_health // 2:
            self.phase = 2
        return self.health <= 0

    def start_blink(self):
        self.blink_timer = self.blink_duration

    def update_blink(self):
        if self.blink_timer > 0:
            self.blink_timer -= 1

    def draw(self, screen):
        if self.blink_timer > 0 and self.blink_timer % 2 == 1:
            return
        screen.blit(self.sprite, (self.x, self.y))

        bar_width = self.width
        bar_height = 8
        bar_x = self.x
        bar_y = self.y - 15

        pygame.draw.rect(screen, (60, 60, 60), (bar_x, bar_y, bar_width, bar_height))

        health_ratio = self.health / self.max_health
        health_width = int(bar_width * health_ratio)
        bar_color = (200, 30, 30) if self.phase == 2 else (80, 80, 90)
        pygame.draw.rect(screen, bar_color, (bar_x, bar_y, health_width, bar_height))

        pygame.draw.rect(screen, WHITE, (bar_x, bar_y, bar_width, bar_height), 1)

    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)

    def collides_with_player(self, player):
        return self.get_rect().colliderect(player.get_rect())

    def is_touching_player(self, player):
        boss_rect = self.get_rect().inflate(4, 4)
        return boss_rect.colliderect(player.get_rect())
