import pygame
from constants import (
    TILE_SIZE, PROJECTILE_SPEED, PROJECTILE_SIZE,
    BOSS_PROJECTILE_SIZE, BOSS_PROJECTILE_SPEED,
    SCREEN_WIDTH, SCREEN_HEIGHT, PURPLE, RED
)


class Projectile:
    def __init__(self, x, y, direction):
        self.x = x
        self.y = y
        self.direction = list(direction)
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
    def __init__(self, x, y, direction):
        self.x = x
        self.y = y
        self.direction = list(direction)
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
    """Grenade-style projectile - slows down, waits 1 second, then explodes."""
    def __init__(self, x, y, direction):
        self.x = x
        self.y = y
        self.direction = list(direction)
        self.speed = 5.0
        self.friction = 0.96
        self.min_speed = 0.2
        self.size = 12
        self.active = True
        self.exploding = False
        self.stopped = False
        self.fuse_timer = 0
        self.fuse_duration = 60
        self.explosion_timer = 0
        self.explosion_radius = 90
        self.explosion_duration = 20
        self.has_damaged = set()

    def update(self, dungeon):
        if self.exploding:
            self.explosion_timer += 1
            if self.explosion_timer >= self.explosion_duration:
                self.active = False
            return

        if self.stopped:
            self.fuse_timer += 1
            if self.fuse_timer >= self.fuse_duration:
                self.explode()
            return

        self.speed *= self.friction

        if self.speed < self.min_speed:
            self.speed = 0
            self.stopped = True
            return

        new_x = self.x + self.direction[0] * self.speed
        new_y = self.y + self.direction[1] * self.speed

        tile_x = int((new_x + self.size // 2) // TILE_SIZE)
        tile_y = int((new_y + self.size // 2) // TILE_SIZE)

        if tile_x < 0 or tile_x >= dungeon.width or tile_y < 0 or tile_y >= dungeon.height:
            self.speed = 0
            self.stopped = True
            return

        if dungeon.tiles[tile_y][tile_x] == 1:
            self.speed = 0
            self.stopped = True
            return

        self.x = new_x
        self.y = new_y

    def explode(self):
        self.exploding = True
        self.explosion_timer = 0

    def draw(self, screen):
        if self.exploding:
            progress = self.explosion_timer / self.explosion_duration
            radius = int(self.explosion_radius * (0.3 + progress * 0.7))

            center_x = int(self.x + self.size // 2)
            center_y = int(self.y + self.size // 2)

            outer_color = (80, 80, 80)
            mid_color = (120, 120, 120)
            inner_color = (180, 180, 180)
            core_color = (220, 220, 220)

            pygame.draw.circle(screen, outer_color, (center_x, center_y), radius)
            pygame.draw.circle(screen, mid_color, (center_x, center_y), int(radius * 0.75))
            pygame.draw.circle(screen, inner_color, (center_x, center_y), int(radius * 0.5))
            pygame.draw.circle(screen, core_color, (center_x, center_y), int(radius * 0.25))
        else:
            gray = (100, 100, 105)
            dark_gray = (60, 60, 65)
            highlight = (140, 140, 145)

            pygame.draw.circle(screen, dark_gray, (int(self.x + self.size // 2), int(self.y + self.size // 2)), self.size // 2)
            pygame.draw.circle(screen, gray, (int(self.x + self.size // 2), int(self.y + self.size // 2)), self.size // 2 - 2)
            pygame.draw.circle(screen, highlight, (int(self.x + self.size // 2 - 2), int(self.y + self.size // 2 - 2)), 2)

            if self.stopped:
                blink = (self.fuse_timer // 8) % 2 == 0
                if blink:
                    pygame.draw.circle(screen, (255, 80, 80), (int(self.x + self.size // 2), int(self.y + self.size // 2 - 4)), 3)

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
        self.dx = direction[0] * BOSS_PROJECTILE_SPEED
        self.dy = direction[1] * BOSS_PROJECTILE_SPEED

    def update(self, dungeon):
        if self.has_ricocheted:
            self.ricochet_timer += 1
            if self.ricochet_timer >= self.ricochet_lifetime:
                self.active = False
                return
        
        new_x = self.x + self.dx
        new_y = self.y + self.dy
        
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
                
                check_x = int((self.x + self.dx + self.size // 2) // TILE_SIZE)
                check_y = old_tile_y
                hit_x = check_x >= 0 and check_x < dungeon.width and dungeon.tiles[check_y][check_x] == 1
                
                check_y = int((self.y + self.dy + self.size // 2) // TILE_SIZE)
                check_x = old_tile_x
                hit_y = check_y >= 0 and check_y < dungeon.height and dungeon.tiles[check_y][check_x] == 1
                
                if hit_x and hit_y:
                    self.direction[0] = -self.direction[0]
                    self.direction[1] = -self.direction[1]
                    self.dx = -self.dx
                    self.dy = -self.dy
                elif hit_x:
                    self.direction[0] = -self.direction[0]
                    self.dx = -self.dx
                elif hit_y:
                    self.direction[1] = -self.direction[1]
                    self.dy = -self.dy
                else:
                    self.direction[0] = -self.direction[0]
                    self.direction[1] = -self.direction[1]
                    self.dx = -self.dx
                    self.dy = -self.dy
                
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
        self.dx = direction[0] * 4
        self.dy = direction[1] * 4

    def update(self, dungeon):
        self.x += self.dx
        self.y += self.dy
        
        if dungeon.is_wall(self.x, self.y, self.size, self.size):
            self.active = False

    def draw(self, screen):
        ice_blue = (100, 180, 255)
        pygame.draw.rect(screen, ice_blue, (self.x, self.y, self.size, self.size))

    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.size, self.size)

    def collides_with_player(self, player):
        return self.get_rect().colliderect(player.get_rect())


class ShadowProjectile:
    """Gray bullet for Shadow Byako."""
    def __init__(self, x, y, direction):
        self.x = x
        self.y = y
        self.direction = list(direction)
        self.dx = direction[0] * BOSS_PROJECTILE_SPEED
        self.dy = direction[1] * BOSS_PROJECTILE_SPEED
        self.speed = BOSS_PROJECTILE_SPEED
        self.size = BOSS_PROJECTILE_SIZE
        self.active = True

    def update(self, dungeon):
        self.x += self.dx
        self.y += self.dy
        
        if (self.x < 0 or self.x > SCREEN_WIDTH or
            self.y < 0 or self.y > SCREEN_HEIGHT):
            self.active = False
            return
        
        if dungeon.is_wall(self.x, self.y, self.size, self.size):
            self.active = False

    def draw(self, screen):
        gray = (120, 120, 120)
        pygame.draw.rect(screen, gray, (self.x, self.y, self.size, self.size))

    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.size, self.size)

    def collides_with_player(self, player):
        return self.get_rect().colliderect(player.get_rect())


class LongShadowProjectile:
    """Very long tracking gray bullet for Shadow Byako - shoots every 10 seconds."""
    def __init__(self, x, y, direction):
        self.x = x
        self.y = y
        self.direction = list(direction)
        self.speed = BOSS_PROJECTILE_SPEED + 2
        self.dx = direction[0] * self.speed
        self.dy = direction[1] * self.speed
        self.base_width = 80
        self.base_height = 8
        self.width = self.base_width if abs(direction[0]) > abs(direction[1]) else self.base_height
        self.height = self.base_height if abs(direction[0]) > abs(direction[1]) else self.base_width
        self.active = True
        self.tracking = True
        self.track_time = 0
        self.max_track_time = 120

    def update(self, dungeon, player=None):
        if self.tracking and player and self.track_time < self.max_track_time:
            self.track_time += 1
            
            my_center_x = self.x + self.width / 2
            my_center_y = self.y + self.height / 2
            player_center_x = player.x + player.width / 2
            player_center_y = player.y + player.height / 2
            
            target_dx = player_center_x - my_center_x
            target_dy = player_center_y - my_center_y
            distance = (target_dx ** 2 + target_dy ** 2) ** 0.5
            
            if distance > 0:
                target_dx = target_dx / distance
                target_dy = target_dy / distance
                
                turn_speed = 0.08
                self.direction[0] += (target_dx - self.direction[0]) * turn_speed
                self.direction[1] += (target_dy - self.direction[1]) * turn_speed
                
                dir_len = (self.direction[0] ** 2 + self.direction[1] ** 2) ** 0.5
                if dir_len > 0:
                    self.direction[0] /= dir_len
                    self.direction[1] /= dir_len
                
                self.dx = self.direction[0] * self.speed
                self.dy = self.direction[1] * self.speed
                
                if abs(self.direction[0]) > abs(self.direction[1]):
                    self.width = self.base_width
                    self.height = self.base_height
                else:
                    self.width = self.base_height
                    self.height = self.base_width
        else:
            self.tracking = False
        
        self.x += self.dx
        self.y += self.dy

        if (self.x < -self.width - 50 or self.x > SCREEN_WIDTH + 50 or
            self.y < -self.height - 50 or self.y > SCREEN_HEIGHT + 50):
            self.active = False
            return

    def draw(self, screen):
        dark_gray = (60, 60, 60)
        core_gray = (100, 100, 100)
        light_gray = (180, 180, 180)
        
        if self.tracking:
            glow_color = (150, 80, 80, 120)
        else:
            glow_color = (120, 120, 120, 100)
        
        glow_surface = pygame.Surface((self.width + 8, self.height + 8), pygame.SRCALPHA)
        pygame.draw.rect(glow_surface, glow_color, (0, 0, self.width + 8, self.height + 8))
        screen.blit(glow_surface, (self.x - 4, self.y - 4))
        
        pygame.draw.rect(screen, dark_gray, (self.x, self.y, self.width, self.height))
        pygame.draw.rect(screen, core_gray, (self.x + 2, self.y + 2, self.width - 4, self.height - 4))
        pygame.draw.rect(screen, light_gray, (self.x + 3, self.y + 3, self.width - 6, self.height - 6), 1)

    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)

    def collides_with_player(self, player):
        return self.get_rect().colliderect(player.get_rect())


class ShadowOrbProjectile:
    """Powerful shadow orb - pierces enemies, deals massive damage, slight homing."""
    def __init__(self, x, y, direction):
        self.x = x
        self.y = y
        self.direction = list(direction)
        self.speed = PROJECTILE_SPEED + 1
        self.size = 16
        self.active = True
        self.damaged_enemies = set()
        self.lifetime = 0
        self.max_lifetime = 300
        self.pulse_timer = 0
        
    def update(self, dungeon, enemies=None):
        self.lifetime += 1
        self.pulse_timer += 1
        
        if self.lifetime >= self.max_lifetime:
            self.active = False
            return
        
        if enemies and self.lifetime < 120:
            nearest_enemy = None
            nearest_dist = 200
            
            for enemy in enemies:
                dx = enemy.x - self.x
                dy = enemy.y - self.y
                dist = (dx ** 2 + dy ** 2) ** 0.5
                if dist < nearest_dist:
                    nearest_dist = dist
                    nearest_enemy = enemy
            
            if nearest_enemy:
                dx = nearest_enemy.x - self.x
                dy = nearest_enemy.y - self.y
                dist = (dx ** 2 + dy ** 2) ** 0.5
                if dist > 0:
                    target_dx = dx / dist
                    target_dy = dy / dist
                    turn_speed = 0.05
                    self.direction[0] += (target_dx - self.direction[0]) * turn_speed
                    self.direction[1] += (target_dy - self.direction[1]) * turn_speed
                    dir_len = (self.direction[0] ** 2 + self.direction[1] ** 2) ** 0.5
                    if dir_len > 0:
                        self.direction[0] /= dir_len
                        self.direction[1] /= dir_len
        
        new_x = self.x + self.direction[0] * self.speed
        new_y = self.y + self.direction[1] * self.speed
        
        tile_x = int((new_x + self.size // 2) // TILE_SIZE)
        tile_y = int((new_y + self.size // 2) // TILE_SIZE)
        
        if tile_x < 0 or tile_x >= dungeon.width or tile_y < 0 or tile_y >= dungeon.height:
            self.active = False
            return
        
        if dungeon.tiles[tile_y][tile_x] == 1:
            self.active = False
            return
        
        self.x = new_x
        self.y = new_y
    
    def draw(self, screen):
        pulse = abs((self.pulse_timer % 30) - 15) / 15
        
        glow_size = int(self.size * 1.8 + pulse * 6)
        glow_surface = pygame.Surface((glow_size * 2, glow_size * 2), pygame.SRCALPHA)
        glow_alpha = int(80 + pulse * 40)
        pygame.draw.circle(glow_surface, (100, 50, 150, glow_alpha), (glow_size, glow_size), glow_size)
        pygame.draw.circle(glow_surface, (60, 20, 100, glow_alpha // 2), (glow_size, glow_size), int(glow_size * 0.7))
        screen.blit(glow_surface, (int(self.x + self.size // 2 - glow_size), int(self.y + self.size // 2 - glow_size)))
        
        outer_color = (80, 40, 120)
        mid_color = (120, 60, 180)
        inner_color = (180, 100, 255)
        core_color = (255, 200, 255)
        
        center_x = int(self.x + self.size // 2)
        center_y = int(self.y + self.size // 2)
        
        pygame.draw.circle(screen, outer_color, (center_x, center_y), self.size // 2)
        pygame.draw.circle(screen, mid_color, (center_x, center_y), self.size // 2 - 2)
        pygame.draw.circle(screen, inner_color, (center_x, center_y), self.size // 2 - 4)
        pygame.draw.circle(screen, core_color, (center_x - 2, center_y - 2), 3)
    
    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.size, self.size)
    
    def collides_with_enemy(self, enemy):
        if id(enemy) in self.damaged_enemies:
            return False
        if self.get_rect().colliderect(enemy.get_rect()):
            self.damaged_enemies.add(id(enemy))
            return True
        return False
