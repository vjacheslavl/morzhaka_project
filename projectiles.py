import pygame
import random
from constants import (
    TILE_SIZE, PROJECTILE_SPEED, PROJECTILE_SIZE,
    BOSS_PROJECTILE_SIZE, BOSS_PROJECTILE_SPEED,
    SCREEN_WIDTH, SCREEN_HEIGHT, PURPLE, RED
)


class Projectile:
    SPREAD_AMOUNT = 0.05
    
    def __init__(self, x, y, direction):
        self.x = x
        self.y = y
        spread = random.choice([-Projectile.SPREAD_AMOUNT, 0, Projectile.SPREAD_AMOUNT])
        if direction[0] != 0 and direction[1] == 0:
            self.direction = [direction[0], spread]
        elif direction[1] != 0 and direction[0] == 0:
            self.direction = [spread, direction[1]]
        else:
            self.direction = [direction[0] + spread * 0.5, direction[1] + spread * 0.5]
        self.speed = PROJECTILE_SPEED
        self.size = PROJECTILE_SIZE
        self.active = True
        self.has_ricocheted = False
        self.ricochet_timer = 0
        self.ricochet_lifetime = 180

    def update(self, dungeon):
        if self.has_ricocheted:
            self.ricochet_timer += 1
            if self.ricochet_timer >= self.ricochet_lifetime:
                self.active = False
                return
        
        new_x = self.x + self.direction[0] * self.speed
        new_y = self.y + self.direction[1] * self.speed
        
        tile_x = int((new_x + self.size // 2) // TILE_SIZE)
        tile_y = int((new_y + self.size // 2) // TILE_SIZE)
        
        if tile_x < 0 or tile_x >= dungeon.width or tile_y < 0 or tile_y >= dungeon.height:
            self.active = False
            return
        
        if dungeon.tiles[tile_y][tile_x] == 1:
            is_diagonal = self.direction[0] != 0 and self.direction[1] != 0
            
            if is_diagonal and not self.has_ricocheted:
                old_tile_x = int((self.x + self.size // 2) // TILE_SIZE)
                old_tile_y = int((self.y + self.size // 2) // TILE_SIZE)
                
                check_x = int((self.x + self.direction[0] * self.speed + self.size // 2) // TILE_SIZE)
                check_y = old_tile_y
                hit_x = check_x >= 0 and check_x < dungeon.width and dungeon.tiles[check_y][check_x] == 1
                
                check_y = int((self.y + self.direction[1] * self.speed + self.size // 2) // TILE_SIZE)
                check_x = old_tile_x
                hit_y = check_y >= 0 and check_y < dungeon.height and dungeon.tiles[check_y][check_x] == 1
                
                if hit_x and hit_y:
                    self.direction[0] = -self.direction[0]
                    self.direction[1] = -self.direction[1]
                elif hit_x:
                    self.direction[0] = -self.direction[0]
                elif hit_y:
                    self.direction[1] = -self.direction[1]
                else:
                    self.direction[0] = -self.direction[0]
                    self.direction[1] = -self.direction[1]
                
                self.has_ricocheted = True
            else:
                self.active = False
            return
        
        self.x = new_x
        self.y = new_y

    def draw(self, screen):
        pygame.draw.rect(screen, PURPLE, (self.x, self.y, self.size, self.size))

    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.size, self.size)

    def collides_with_enemy(self, enemy):
        return self.get_rect().colliderect(enemy.get_rect())


class IceProjectile:
    """Piercing ice bullet - goes through enemies and deals damage to all in path."""
    SPREAD_AMOUNT = 0.05
    
    def __init__(self, x, y, direction):
        self.x = x
        self.y = y
        spread = random.choice([-IceProjectile.SPREAD_AMOUNT, 0, IceProjectile.SPREAD_AMOUNT])
        if direction[0] != 0 and direction[1] == 0:
            self.direction = [direction[0], spread]
        elif direction[1] != 0 and direction[0] == 0:
            self.direction = [spread, direction[1]]
        else:
            self.direction = [direction[0] + spread * 0.5, direction[1] + spread * 0.5]
        self.speed = PROJECTILE_SPEED + 2
        self.acceleration = 0.15
        self.max_speed = PROJECTILE_SPEED + 10
        self.size = 8
        self.active = True
        self.has_ricocheted = False
        self.ricochet_timer = 0
        self.ricochet_lifetime = 180
        self.hit_enemies = set()

    def update(self, dungeon):
        if self.speed < self.max_speed:
            self.speed += self.acceleration
        
        if self.has_ricocheted:
            self.ricochet_timer += 1
            if self.ricochet_timer >= self.ricochet_lifetime:
                self.active = False
                return
        
        new_x = self.x + self.direction[0] * self.speed
        new_y = self.y + self.direction[1] * self.speed
        
        tile_x = int((new_x + self.size // 2) // TILE_SIZE)
        tile_y = int((new_y + self.size // 2) // TILE_SIZE)
        
        if tile_x < 0 or tile_x >= dungeon.width or tile_y < 0 or tile_y >= dungeon.height:
            self.active = False
            return
        
        if dungeon.tiles[tile_y][tile_x] == 1:
            is_diagonal = self.direction[0] != 0 and self.direction[1] != 0
            
            if is_diagonal and not self.has_ricocheted:
                old_tile_x = int((self.x + self.size // 2) // TILE_SIZE)
                old_tile_y = int((self.y + self.size // 2) // TILE_SIZE)
                
                check_x = int((self.x + self.direction[0] * self.speed + self.size // 2) // TILE_SIZE)
                check_y = old_tile_y
                hit_x = check_x >= 0 and check_x < dungeon.width and dungeon.tiles[check_y][check_x] == 1
                
                check_y = int((self.y + self.direction[1] * self.speed + self.size // 2) // TILE_SIZE)
                check_x = old_tile_x
                hit_y = check_y >= 0 and check_y < dungeon.height and dungeon.tiles[check_y][check_x] == 1
                
                if hit_x and not hit_y:
                    self.direction[0] = -self.direction[0]
                elif hit_y and not hit_x:
                    self.direction[1] = -self.direction[1]
                else:
                    self.direction[0] = -self.direction[0]
                    self.direction[1] = -self.direction[1]
                
                self.has_ricocheted = True
            else:
                self.active = False
            return
        
        self.x = new_x
        self.y = new_y

    def draw(self, screen):
        cyan = (0, 255, 255)
        pygame.draw.rect(screen, cyan, (self.x, self.y, self.size, self.size))
        light_cyan = (150, 255, 255)
        pygame.draw.rect(screen, light_cyan, (self.x + 2, self.y + 2, self.size - 4, self.size - 4))

    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.size, self.size)

    def collides_with_enemy(self, enemy):
        if id(enemy) in self.hit_enemies:
            return False
        if self.get_rect().colliderect(enemy.get_rect()):
            self.hit_enemies.add(id(enemy))
            return True
        return False


class ExplosiveProjectile:
    """Gray explosive bullet - explodes on impact, damages nearby enemies."""
    SPREAD_AMOUNT = 0.05
    
    def __init__(self, x, y, direction):
        self.x = x
        self.y = y
        spread = random.choice([-ExplosiveProjectile.SPREAD_AMOUNT, 0, ExplosiveProjectile.SPREAD_AMOUNT])
        if direction[0] != 0 and direction[1] == 0:
            self.direction = [direction[0], spread]
        elif direction[1] != 0 and direction[0] == 0:
            self.direction = [spread, direction[1]]
        else:
            self.direction = [direction[0] + spread * 0.5, direction[1] + spread * 0.5]
        self.speed = PROJECTILE_SPEED + 3
        self.size = 10
        self.active = True
        self.exploding = False
        self.explosion_timer = 0
        self.explosion_radius = 60
        self.explosion_duration = 15
        self.has_damaged = set()

    def update(self, dungeon):
        if self.exploding:
            self.explosion_timer += 1
            if self.explosion_timer >= self.explosion_duration:
                self.active = False
            return

        new_x = self.x + self.direction[0] * self.speed
        new_y = self.y + self.direction[1] * self.speed

        tile_x = int((new_x + self.size // 2) // TILE_SIZE)
        tile_y = int((new_y + self.size // 2) // TILE_SIZE)

        if tile_x < 0 or tile_x >= dungeon.width or tile_y < 0 or tile_y >= dungeon.height:
            self.explode()
            return

        if dungeon.tiles[tile_y][tile_x] == 1:
            self.explode()
            return

        self.x = new_x
        self.y = new_y

    def explode(self):
        self.exploding = True
        self.explosion_timer = 0

    def draw(self, screen):
        if self.exploding:
            progress = self.explosion_timer / self.explosion_duration
            radius = int(self.explosion_radius * (0.5 + progress * 0.5))
            
            center_x = int(self.x + self.size // 2)
            center_y = int(self.y + self.size // 2)
            
            pygame.draw.circle(screen, (100, 100, 100), (center_x, center_y), radius)
            pygame.draw.circle(screen, (150, 150, 150), (center_x, center_y), int(radius * 0.7))
            pygame.draw.circle(screen, (200, 200, 200), (center_x, center_y), int(radius * 0.4))
        else:
            gray = (120, 120, 125)
            dark_gray = (80, 80, 85)
            pygame.draw.rect(screen, dark_gray, (self.x, self.y, self.size, self.size))
            pygame.draw.rect(screen, gray, (self.x + 2, self.y + 2, self.size - 4, self.size - 4))

    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.size, self.size)

    def get_explosion_rect(self):
        center_x = self.x + self.size // 2
        center_y = self.y + self.size // 2
        return pygame.Rect(
            center_x - self.explosion_radius,
            center_y - self.explosion_radius,
            self.explosion_radius * 2,
            self.explosion_radius * 2
        )

    def damages_enemy(self, enemy):
        if not self.exploding:
            if self.get_rect().colliderect(enemy.get_rect()):
                self.explode()
                return True
            return False
        
        if id(enemy) in self.has_damaged:
            return False
        
        center_x = self.x + self.size // 2
        center_y = self.y + self.size // 2
        enemy_center_x = enemy.x + enemy.width // 2
        enemy_center_y = enemy.y + enemy.height // 2
        
        dist = ((center_x - enemy_center_x) ** 2 + (center_y - enemy_center_y) ** 2) ** 0.5
        if dist <= self.explosion_radius:
            self.has_damaged.add(id(enemy))
            return True
        return False


class BossProjectile:
    def __init__(self, x, y, direction):
        self.x = x
        self.y = y
        self.direction = list(direction)
        self.speed = BOSS_PROJECTILE_SPEED
        self.size = BOSS_PROJECTILE_SIZE
        self.active = True
        self.has_ricocheted = False
        self.ricochet_timer = 0
        self.ricochet_lifetime = 180

    def update(self, dungeon):
        if self.has_ricocheted:
            self.ricochet_timer += 1
            if self.ricochet_timer >= self.ricochet_lifetime:
                self.active = False
                return
        
        new_x = self.x + self.direction[0] * self.speed
        new_y = self.y + self.direction[1] * self.speed
        
        if (new_x < 0 or new_x > SCREEN_WIDTH or
            new_y < 0 or new_y > SCREEN_HEIGHT):
            self.active = False
            return
        
        tile_x = int((new_x + self.size // 2) // TILE_SIZE)
        tile_y = int((new_y + self.size // 2) // TILE_SIZE)
        
        if tile_x < 0 or tile_x >= dungeon.width or tile_y < 0 or tile_y >= dungeon.height:
            self.active = False
            return
        
        if dungeon.tiles[tile_y][tile_x] == 1:
            is_diagonal = self.direction[0] != 0 and self.direction[1] != 0
            
            if is_diagonal and not self.has_ricocheted:
                old_tile_x = int((self.x + self.size // 2) // TILE_SIZE)
                old_tile_y = int((self.y + self.size // 2) // TILE_SIZE)
                
                check_x = int((self.x + self.direction[0] * self.speed + self.size // 2) // TILE_SIZE)
                check_y = old_tile_y
                hit_x = check_x >= 0 and check_x < dungeon.width and dungeon.tiles[check_y][check_x] == 1
                
                check_y = int((self.y + self.direction[1] * self.speed + self.size // 2) // TILE_SIZE)
                check_x = old_tile_x
                hit_y = check_y >= 0 and check_y < dungeon.height and dungeon.tiles[check_y][check_x] == 1
                
                if hit_x and hit_y:
                    self.direction[0] = -self.direction[0]
                    self.direction[1] = -self.direction[1]
                elif hit_x:
                    self.direction[0] = -self.direction[0]
                elif hit_y:
                    self.direction[1] = -self.direction[1]
                else:
                    self.direction[0] = -self.direction[0]
                    self.direction[1] = -self.direction[1]
                
                self.has_ricocheted = True
            else:
                self.active = False
            return
        
        self.x = new_x
        self.y = new_y

    def draw(self, screen):
        pygame.draw.rect(screen, RED, (self.x, self.y, self.size, self.size))

    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.size, self.size)

    def collides_with_player(self, player):
        return self.get_rect().colliderect(player.get_rect())


class EnemyProjectile:
    def __init__(self, x, y, direction):
        self.x = x
        self.y = y
        self.direction = list(direction)
        self.speed = 4
        self.size = 8
        self.active = True

    def update(self, dungeon):
        self.x += self.direction[0] * self.speed
        self.y += self.direction[1] * self.speed
        
        if dungeon.is_wall(self.x, self.y, self.size, self.size):
            self.active = False

    def draw(self, screen):
        ice_blue = (100, 180, 255)
        pygame.draw.rect(screen, ice_blue, (self.x, self.y, self.size, self.size))

    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.size, self.size)

    def collides_with_player(self, player):
        return self.get_rect().colliderect(player.get_rect())
