import pygame
import random
from constants import (
    TILE_SIZE, PLAYER_SPEED, PROJECTILE_SIZE,
    WHITE, GREEN, RED, DARK_RED, PIXEL_SIZE
)
from sprites import create_player_sprites
from projectiles import Projectile


class Player:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.sprites = create_player_sprites()
        self.sprite = self.sprites[0]
        self.width = self.sprite.get_width()
        self.height = self.sprite.get_height()
        self.speed = PLAYER_SPEED
        self.max_health = 6
        self.health = self.max_health
        self.last_direction = (1, 0)
        self.walk_frame = 0
        self.walk_timer = 0
        self.walk_speed = 8
        self.is_moving = False
        self.blink_timer = 0
        self.blink_duration = 10
        self.velocity_x = 0.0
        self.velocity_y = 0.0
        self.ice_friction = 0.92
        self.ice_acceleration = 0.4
        self.ice_max_speed = PLAYER_SPEED * 1.2
        self.can_pass_through_enemies = False

    def would_collide_with_enemies(self, new_x, new_y, enemies, boss=None, final_boss=None):
        if self.can_pass_through_enemies:
            return False
        player_rect = pygame.Rect(new_x, new_y, self.width, self.height)
        for enemy in enemies:
            if player_rect.colliderect(enemy.get_rect()):
                return True
        if boss and player_rect.colliderect(boss.get_rect()):
            return True
        if final_boss and player_rect.colliderect(final_boss.get_rect()):
            return True
        return False

    def move(self, dx, dy, dungeon, enemies=None, boss=None, final_boss=None):
        if enemies is None:
            enemies = []
        
        old_x, old_y = self.x, self.y
        new_x = self.x + dx * self.speed
        new_y = self.y + dy * self.speed

        can_move_x = not dungeon.is_wall(new_x, self.y, self.width, self.height)
        can_move_y = not dungeon.is_wall(self.x, new_y, self.width, self.height)
        
        if can_move_x and not self.would_collide_with_enemies(new_x, self.y, enemies, boss, final_boss):
            self.x = new_x
        if can_move_y and not self.would_collide_with_enemies(self.x, new_y, enemies, boss, final_boss):
            self.y = new_y
        
        if self.x != old_x or self.y != old_y:
            self.last_direction = (dx, dy)
            self.is_moving = True
            
            self.walk_timer += 1
            if self.walk_timer >= self.walk_speed:
                self.walk_timer = 0
                self.walk_frame = 1 - self.walk_frame
                self.sprite = self.sprites[self.walk_frame]
        else:
            self.is_moving = False

    def move_on_ice(self, dx, dy, dungeon, enemies=None, boss=None, final_boss=None):
        if enemies is None:
            enemies = []
        
        if dx != 0 or dy != 0:
            self.velocity_x += dx * self.ice_acceleration
            self.velocity_y += dy * self.ice_acceleration
            self.last_direction = (dx, dy)
        
        self.velocity_x *= self.ice_friction
        self.velocity_y *= self.ice_friction
        
        speed = (self.velocity_x ** 2 + self.velocity_y ** 2) ** 0.5
        if speed > self.ice_max_speed:
            self.velocity_x = (self.velocity_x / speed) * self.ice_max_speed
            self.velocity_y = (self.velocity_y / speed) * self.ice_max_speed
        
        if abs(self.velocity_x) < 0.1:
            self.velocity_x = 0
        if abs(self.velocity_y) < 0.1:
            self.velocity_y = 0
        
        old_x, old_y = self.x, self.y
        new_x = self.x + self.velocity_x
        new_y = self.y + self.velocity_y
        
        can_move_x = not dungeon.is_wall(new_x, self.y, self.width, self.height)
        can_move_y = not dungeon.is_wall(self.x, new_y, self.width, self.height)
        
        if can_move_x and not self.would_collide_with_enemies(new_x, self.y, enemies, boss, final_boss):
            self.x = new_x
        else:
            self.velocity_x = 0
        
        if can_move_y and not self.would_collide_with_enemies(self.x, new_y, enemies, boss, final_boss):
            self.y = new_y
        else:
            self.velocity_y = 0
        
        if self.x != old_x or self.y != old_y:
            self.is_moving = True
            self.walk_timer += 1
            if self.walk_timer >= self.walk_speed:
                self.walk_timer = 0
                self.walk_frame = 1 - self.walk_frame
                self.sprite = self.sprites[self.walk_frame]
        else:
            self.is_moving = False

    def reset_velocity(self):
        self.velocity_x = 0.0
        self.velocity_y = 0.0

    def update(self):
        if not self.is_moving:
            self.walk_frame = 0
            self.sprite = self.sprites[0]
        self.is_moving = False
        
        if self.blink_timer > 0:
            self.blink_timer -= 1

    def shoot(self):
        proj_x = self.x + self.width // 2 - PROJECTILE_SIZE // 2
        proj_y = self.y + self.height // 2 - PROJECTILE_SIZE // 2
        return Projectile(proj_x, proj_y, self.last_direction)

    def take_damage(self, amount=1):
        self.health = max(0, self.health - amount)
        self.start_blink()
        return self.health <= 0

    def start_blink(self):
        self.blink_timer = self.blink_duration

    def heal(self, amount=1):
        self.health = min(self.max_health, self.health + amount)

    def draw(self, screen):
        if self.blink_timer > 0 and self.blink_timer % 2 == 1:
            return
        screen.blit(self.sprite, (self.x, self.y))

    def draw_health(self, screen, x, y):
        heart_size = 20
        spacing = 5
        
        for i in range(self.max_health):
            heart_x = x + i * (heart_size + spacing)
            if i < self.health:
                self.draw_heart(screen, heart_x, y, heart_size, RED)
            else:
                self.draw_heart(screen, heart_x, y, heart_size, DARK_RED)

    def draw_heart(self, screen, x, y, size, color):
        half = size // 2
        quarter = size // 4
        pygame.draw.circle(screen, color, (x + quarter, y + quarter), quarter)
        pygame.draw.circle(screen, color, (x + half + quarter, y + quarter), quarter)
        points = [
            (x, y + quarter),
            (x + half, y + size),
            (x + size, y + quarter)
        ]
        pygame.draw.polygon(screen, color, points)

    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)


class HealthKit:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.size = 20
        self.active = True

    def draw(self, screen):
        pygame.draw.rect(screen, WHITE, (self.x, self.y, self.size, self.size))
        pygame.draw.rect(screen, GREEN, (self.x + 2, self.y + 2, self.size - 4, self.size - 4))
        pygame.draw.rect(screen, WHITE, (self.x + 7, self.y + 4, 6, 12))
        pygame.draw.rect(screen, WHITE, (self.x + 4, self.y + 7, 12, 6))

    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.size, self.size)

    def collides_with_player(self, player):
        return self.get_rect().colliderect(player.get_rect())


class Laser:
    MAX_LENGTH_TILES = 4
    
    def __init__(self, start_tile, end_tile, on_duration=90, off_duration=90, start_on=True):
        self.start_tile = start_tile
        
        dx = end_tile[0] - start_tile[0]
        dy = end_tile[1] - start_tile[1]
        if abs(dx) > self.MAX_LENGTH_TILES:
            dx = self.MAX_LENGTH_TILES if dx > 0 else -self.MAX_LENGTH_TILES
        if abs(dy) > self.MAX_LENGTH_TILES:
            dy = self.MAX_LENGTH_TILES if dy > 0 else -self.MAX_LENGTH_TILES
        self.end_tile = (start_tile[0] + dx, start_tile[1] + dy)
        
        self.on_duration = on_duration
        self.off_duration = off_duration
        self.is_on = start_on
        self.timer = 0
        self.beam_width = 6
        self.warning_time = 30
        
        start_x = self.start_tile[0] * TILE_SIZE + TILE_SIZE // 2
        start_y = self.start_tile[1] * TILE_SIZE + TILE_SIZE // 2
        end_x = self.end_tile[0] * TILE_SIZE + TILE_SIZE // 2
        end_y = self.end_tile[1] * TILE_SIZE + TILE_SIZE // 2
        
        if start_x == end_x:
            self.orientation = 'vertical'
            self.rect = pygame.Rect(
                start_x - self.beam_width // 2,
                min(start_y, end_y),
                self.beam_width,
                abs(end_y - start_y)
            )
        else:
            self.orientation = 'horizontal'
            self.rect = pygame.Rect(
                min(start_x, end_x),
                start_y - self.beam_width // 2,
                abs(end_x - start_x),
                self.beam_width
            )
        
        self.emitter1_pos = (start_x, start_y)
        self.emitter2_pos = (end_x, end_y)
        self.animation_offset = 0

    def update(self):
        self.timer += 1
        self.animation_offset = (self.animation_offset + 2) % 20
        
        if self.is_on:
            if self.timer >= self.on_duration:
                self.is_on = False
                self.timer = 0
        else:
            if self.timer >= self.off_duration:
                self.is_on = True
                self.timer = 0

    def is_warning(self):
        return not self.is_on and self.timer >= self.off_duration - self.warning_time

    def collides_with_player(self, player):
        if not self.is_on:
            return False
        return self.rect.colliderect(player.get_rect())

    def draw(self, screen):
        e1x, e1y = self.emitter1_pos
        e2x, e2y = self.emitter2_pos
        emitter_size = 10
        pygame.draw.rect(screen, (80, 80, 90), 
                        (e1x - emitter_size // 2, e1y - emitter_size // 2, emitter_size, emitter_size))
        pygame.draw.rect(screen, (80, 80, 90), 
                        (e2x - emitter_size // 2, e2y - emitter_size // 2, emitter_size, emitter_size))
        
        if self.is_on:
            core_color = (255, 50, 50)
            edge_color = (255, 200, 200)
            
            glow_rect = self.rect.inflate(8, 8)
            glow_surface = pygame.Surface((glow_rect.width, glow_rect.height), pygame.SRCALPHA)
            pygame.draw.rect(glow_surface, (255, 50, 50, 60), glow_surface.get_rect())
            screen.blit(glow_surface, glow_rect.topleft)
            
            pygame.draw.rect(screen, core_color, self.rect)
            
            if self.orientation == 'horizontal':
                pygame.draw.line(screen, edge_color, 
                               (self.rect.left, self.rect.top),
                               (self.rect.right, self.rect.top), 1)
                pygame.draw.line(screen, edge_color, 
                               (self.rect.left, self.rect.bottom - 1),
                               (self.rect.right, self.rect.bottom - 1), 1)
            else:
                pygame.draw.line(screen, edge_color, 
                               (self.rect.left, self.rect.top),
                               (self.rect.left, self.rect.bottom), 1)
                pygame.draw.line(screen, edge_color, 
                               (self.rect.right - 1, self.rect.top),
                               (self.rect.right - 1, self.rect.bottom), 1)
            
            pygame.draw.circle(screen, (255, 100, 100), (e1x, e1y), emitter_size // 2 + 2)
            pygame.draw.circle(screen, (255, 100, 100), (e2x, e2y), emitter_size // 2 + 2)
        elif self.is_warning():
            warning_alpha = int(128 + 127 * (self.timer % 10) / 10)
            warning_color = (255, 100, 100, warning_alpha)
            
            warning_surface = pygame.Surface((self.rect.width, self.rect.height), pygame.SRCALPHA)
            pygame.draw.rect(warning_surface, warning_color, warning_surface.get_rect())
            screen.blit(warning_surface, self.rect.topleft)
            
            pygame.draw.circle(screen, (255, 150, 50), (e1x, e1y), emitter_size // 2 + 1)
            pygame.draw.circle(screen, (255, 150, 50), (e2x, e2y), emitter_size // 2 + 1)
        else:
            off_color = (100, 40, 40)
            if self.orientation == 'horizontal':
                for x in range(self.rect.left, self.rect.right, 20):
                    segment_x = x + self.animation_offset
                    if segment_x < self.rect.right:
                        pygame.draw.line(screen, off_color,
                                       (segment_x, self.rect.centery),
                                       (min(segment_x + 8, self.rect.right), self.rect.centery), 2)
            else:
                for y in range(self.rect.top, self.rect.bottom, 20):
                    segment_y = y + self.animation_offset
                    if segment_y < self.rect.bottom:
                        pygame.draw.line(screen, off_color,
                                       (self.rect.centerx, segment_y),
                                       (self.rect.centerx, min(segment_y + 8, self.rect.bottom)), 2)


class DeathParticle:
    """Particle effect for enemy deaths."""
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.color = color
        self.vx = random.uniform(-3, 3)
        self.vy = random.uniform(-4, 1)
        self.gravity = 0.15
        self.lifetime = random.randint(20, 40)
        self.size = random.randint(3, 6)
        self.active = True

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vy += self.gravity
        self.lifetime -= 1
        if self.lifetime <= 0:
            self.active = False

    def draw(self, screen):
        if self.active:
            size = max(1, int(self.size * (self.lifetime / 40)))
            pygame.draw.rect(screen, self.color, (int(self.x), int(self.y), size, size))
