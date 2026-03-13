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
        self.width = 36
        self.height = 24
        self.active = True

    def draw(self, screen):
        P = 3
        x, y = int(self.x), int(self.y)
        fish_body = (255, 180, 100)
        fish_belly = (255, 220, 180)
        fish_fin = (255, 140, 60)
        fish_eye = (40, 40, 40)
        fish_highlight = (255, 240, 200)
        pygame.draw.rect(screen, fish_fin, (x, y + 4*P, 2*P, 4*P))
        pygame.draw.rect(screen, fish_body, (x + 2*P, y + 2*P, 6*P, 4*P))
        pygame.draw.rect(screen, fish_belly, (x + 2*P, y + 4*P, 6*P, 2*P))
        pygame.draw.rect(screen, fish_body, (x + 8*P, y + 3*P, 2*P, 2*P))
        pygame.draw.rect(screen, fish_fin, (x + 4*P, y + P, 2*P, P))
        pygame.draw.rect(screen, fish_fin, (x + 4*P, y + 6*P, 2*P, P))
        pygame.draw.rect(screen, fish_highlight, (x + 3*P, y + 3*P, P, P))
        pygame.draw.rect(screen, fish_eye, (x + 7*P, y + 3*P, P, P))

    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)

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


class NPC:
    PHRASES = [
        "i am morzhaka",
        "hello morzhaka",
        "i cut water with scissors",
        "i want steak",
        "me be morzhaka",
        "i love morzhaka tea",
    ]
    
    def __init__(self, x, y, hat_type='wizard', name='Villager', custom_phrases=None):
        from sprites import create_npc_sprite
        self.x = x
        self.y = y
        self.hat_type = hat_type
        self.name = name
        self.sprite = create_npc_sprite(hat_type)
        self.width = self.sprite.get_width()
        self.height = self.sprite.get_height()
        self.custom_phrases = custom_phrases
        self.phrases = custom_phrases if custom_phrases else self.PHRASES
        self.current_phrase = None
        self.phrase_timer = 0
        self.phrase_duration = 180
        self.animation_timer = 0
        self.bob_offset = 0
    
    def interact(self):
        self.current_phrase = random.choice(self.phrases)
        self.phrase_timer = self.phrase_duration
    
    def update(self):
        self.animation_timer += 1
        self.bob_offset = int(2 * ((self.animation_timer // 20) % 2))
        
        if self.phrase_timer > 0:
            self.phrase_timer -= 1
            if self.phrase_timer <= 0:
                self.current_phrase = None
    
    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)
    
    def is_player_nearby(self, player, distance=60):
        px = player.x + player.width // 2
        py = player.y + player.height // 2
        nx = self.x + self.width // 2
        ny = self.y + self.height // 2
        return ((px - nx) ** 2 + (py - ny) ** 2) ** 0.5 < distance
    
    def draw(self, screen):
        screen.blit(self.sprite, (int(self.x), int(self.y) - self.bob_offset))
    
    def draw_speech_bubble(self, screen, font):
        if not self.current_phrase:
            return
        
        bubble_padding = 10
        text_surface = font.render(self.current_phrase, True, (40, 40, 40))
        text_width = text_surface.get_width()
        text_height = text_surface.get_height()
        
        bubble_width = text_width + bubble_padding * 2
        bubble_height = text_height + bubble_padding * 2
        
        bubble_x = int(self.x + self.width // 2 - bubble_width // 2)
        bubble_y = int(self.y - bubble_height - 20)
        
        if bubble_x < 10:
            bubble_x = 10
        if bubble_x + bubble_width > 1190:
            bubble_x = 1190 - bubble_width
        
        pygame.draw.rect(screen, (255, 255, 240), (bubble_x, bubble_y, bubble_width, bubble_height), border_radius=8)
        pygame.draw.rect(screen, (100, 80, 60), (bubble_x, bubble_y, bubble_width, bubble_height), 2, border_radius=8)
        
        tail_points = [
            (int(self.x + self.width // 2) - 5, bubble_y + bubble_height),
            (int(self.x + self.width // 2) + 5, bubble_y + bubble_height),
            (int(self.x + self.width // 2), bubble_y + bubble_height + 10)
        ]
        pygame.draw.polygon(screen, (255, 255, 240), tail_points)
        pygame.draw.line(screen, (100, 80, 60), tail_points[0], tail_points[2], 2)
        pygame.draw.line(screen, (100, 80, 60), tail_points[1], tail_points[2], 2)
        
        screen.blit(text_surface, (bubble_x + bubble_padding, bubble_y + bubble_padding))
        
        name_surface = font.render(self.name, True, (80, 60, 40))
        name_x = int(self.x + self.width // 2 - name_surface.get_width() // 2)
        name_y = int(self.y + self.height + 5)
        screen.blit(name_surface, (name_x, name_y))


class SummonedAlly:
    """Morzhaka ally that fights alongside the player."""
    def __init__(self, x, y):
        from sprites import create_summoned_ally_sprite
        from constants import TILE_SIZE
        self.TILE_SIZE = TILE_SIZE
        self.x = x
        self.y = y
        self.sprite = create_summoned_ally_sprite()
        self.width = self.sprite.get_width()
        self.height = self.sprite.get_height()
        self.speed = 2.5
        self.max_health = 20
        self.health = self.max_health
        self.attack_cooldown = 0
        self.attack_cooldown_max = 84
        self.damage_cooldown = 0
        self.damage_cooldown_max = 60
        self.detection_range = 150
        self.attack_range = 35
        self.target = None
        self.blink_timer = 0
        self.path = []
        self.path_update_timer = 0
        self.path_update_interval = 20
    
    def update(self, player, enemies, boss, final_boss, shadow_boss, dungeon):
        self.find_target(player, enemies, boss, final_boss, shadow_boss)
        
        self.path_update_timer += 1
        
        if self.target:
            self.move_towards_target(dungeon)
        else:
            self.follow_player(player, dungeon)
        
        if self.attack_cooldown > 0:
            self.attack_cooldown -= 1
        
        if self.damage_cooldown > 0:
            self.damage_cooldown -= 1
        
        if self.blink_timer > 0:
            self.blink_timer -= 1
    
    def find_target(self, player, enemies, boss, final_boss, shadow_boss):
        if boss:
            self.target = boss
            return
        
        if final_boss:
            self.target = final_boss
            return
        
        if shadow_boss:
            self.target = shadow_boss
            return
        
        closest_dist = float('inf')
        closest_target = None
        
        px = player.x + player.width // 2
        py = player.y + player.height // 2
        
        for enemy in enemies:
            enemy_dist_to_player = ((px - enemy.x) ** 2 + (py - enemy.y) ** 2) ** 0.5
            if enemy_dist_to_player < self.detection_range:
                dist = ((self.x - enemy.x) ** 2 + (self.y - enemy.y) ** 2) ** 0.5
                if dist < closest_dist:
                    closest_dist = dist
                    closest_target = enemy
        
        self.target = closest_target
    
    def update_path(self, target_x, target_y, dungeon):
        from pathfinding import find_path
        my_tile = (int((self.x + self.width // 2) // self.TILE_SIZE),
                   int((self.y + self.height // 2) // self.TILE_SIZE))
        target_tile = (int((target_x) // self.TILE_SIZE),
                       int((target_y) // self.TILE_SIZE))
        self.path = find_path(my_tile, target_tile, dungeon.tiles)
    
    def move_towards_target(self, dungeon):
        if not self.target:
            return
        
        dx = self.target.x - self.x
        dy = self.target.y - self.y
        dist = (dx ** 2 + dy ** 2) ** 0.5
        
        if dist <= self.attack_range:
            return
        
        if dist < 60:
            if dist > 0:
                dx = dx / dist * self.speed
                dy = dy / dist * self.speed
            new_x = self.x + dx
            new_y = self.y + dy
            if not dungeon.is_wall(new_x, self.y, self.width, self.height):
                self.x = new_x
            if not dungeon.is_wall(self.x, new_y, self.width, self.height):
                self.y = new_y
            return
        
        if self.path_update_timer >= self.path_update_interval or not self.path:
            self.path_update_timer = 0
            self.update_path(self.target.x + self.target.width // 2, 
                           self.target.y + self.target.height // 2, dungeon)
        
        if not self.path:
            if dist > 0:
                dx = dx / dist * self.speed
                dy = dy / dist * self.speed
            new_x = self.x + dx
            new_y = self.y + dy
            if not dungeon.is_wall(new_x, self.y, self.width, self.height):
                self.x = new_x
            if not dungeon.is_wall(self.x, new_y, self.width, self.height):
                self.y = new_y
            return
        
        target_tile = self.path[0]
        target_x = target_tile[0] * self.TILE_SIZE + self.TILE_SIZE // 2 - self.width // 2
        target_y = target_tile[1] * self.TILE_SIZE + self.TILE_SIZE // 2 - self.height // 2
        
        dx = target_x - self.x
        dy = target_y - self.y
        dist_to_tile = (dx ** 2 + dy ** 2) ** 0.5
        
        if dist_to_tile < self.speed:
            self.x = target_x
            self.y = target_y
            self.path.pop(0)
        else:
            dx = dx / dist_to_tile * self.speed
            dy = dy / dist_to_tile * self.speed
            new_x = self.x + dx
            new_y = self.y + dy
            if not dungeon.is_wall(new_x, self.y, self.width, self.height):
                self.x = new_x
            if not dungeon.is_wall(self.x, new_y, self.width, self.height):
                self.y = new_y
    
    def follow_player(self, player, dungeon):
        dx = player.x - self.x
        dy = player.y - self.y
        dist = (dx ** 2 + dy ** 2) ** 0.5
        
        if dist <= 40:
            return
        
        if dist < 80:
            if dist > 0:
                dx = dx / dist * self.speed
                dy = dy / dist * self.speed
            new_x = self.x + dx
            new_y = self.y + dy
            if not dungeon.is_wall(new_x, self.y, self.width, self.height):
                self.x = new_x
            if not dungeon.is_wall(self.x, new_y, self.width, self.height):
                self.y = new_y
            return
        
        if self.path_update_timer >= self.path_update_interval or not self.path:
            self.path_update_timer = 0
            self.update_path(player.x + player.width // 2, 
                           player.y + player.height // 2, dungeon)
        
        if not self.path:
            if dist > 0:
                dx = dx / dist * self.speed
                dy = dy / dist * self.speed
            new_x = self.x + dx
            new_y = self.y + dy
            if not dungeon.is_wall(new_x, self.y, self.width, self.height):
                self.x = new_x
            if not dungeon.is_wall(self.x, new_y, self.width, self.height):
                self.y = new_y
            return
        
        target_tile = self.path[0]
        target_x = target_tile[0] * self.TILE_SIZE + self.TILE_SIZE // 2 - self.width // 2
        target_y = target_tile[1] * self.TILE_SIZE + self.TILE_SIZE // 2 - self.height // 2
        
        dx = target_x - self.x
        dy = target_y - self.y
        dist_to_tile = (dx ** 2 + dy ** 2) ** 0.5
        
        if dist_to_tile < self.speed:
            self.x = target_x
            self.y = target_y
            self.path.pop(0)
        else:
            dx = dx / dist_to_tile * self.speed
            dy = dy / dist_to_tile * self.speed
            new_x = self.x + dx
            new_y = self.y + dy
            if not dungeon.is_wall(new_x, self.y, self.width, self.height):
                self.x = new_x
            if not dungeon.is_wall(self.x, new_y, self.width, self.height):
                self.y = new_y
    
    def try_attack(self, enemies, boss, final_boss, shadow_boss):
        if self.attack_cooldown > 0:
            return None
        
        if not self.target:
            return None
        
        dx = self.target.x - self.x
        dy = self.target.y - self.y
        dist = (dx ** 2 + dy ** 2) ** 0.5
        
        if dist <= self.attack_range + 15:
            self.attack_cooldown = self.attack_cooldown_max
            return self.target
        
        return None
    
    def take_damage(self, amount=1):
        if self.damage_cooldown > 0:
            return False
        self.health -= amount
        self.blink_timer = 10
        self.damage_cooldown = self.damage_cooldown_max
        return self.health <= 0
    
    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)
    
    def draw(self, screen):
        if self.blink_timer > 0 and self.blink_timer % 2 == 1:
            return
        screen.blit(self.sprite, (int(self.x), int(self.y)))
        
        bar_width = 30
        bar_height = 4
        bar_x = int(self.x + self.width // 2 - bar_width // 2)
        bar_y = int(self.y - 8)
        
        pygame.draw.rect(screen, (60, 60, 60), (bar_x, bar_y, bar_width, bar_height))
        health_width = int(bar_width * self.health / self.max_health)
        pygame.draw.rect(screen, (100, 255, 100), (bar_x, bar_y, health_width, bar_height))
        pygame.draw.rect(screen, (255, 255, 255), (bar_x, bar_y, bar_width, bar_height), 1)


class ShadowAlly:
    """Gray shadow morzhaka that fights alongside the player - unlimited summons."""
    def __init__(self, x, y):
        from sprites import create_shadow_ally_sprite
        from constants import TILE_SIZE
        self.TILE_SIZE = TILE_SIZE
        self.x = x
        self.y = y
        self.sprite = create_shadow_ally_sprite()
        self.width = self.sprite.get_width()
        self.height = self.sprite.get_height()
        self.speed = 2.8
        self.max_health = 8
        self.health = self.max_health
        self.attack_cooldown = 0
        self.attack_cooldown_max = 60
        self.damage_cooldown = 0
        self.damage_cooldown_max = 45
        self.detection_range = 180
        self.attack_range = 30
        self.target = None
        self.blink_timer = 0
        self.lifetime = 1800
        self.path = []
        self.path_update_timer = 0
        self.path_update_interval = 15

    def update(self, player, enemies, boss, final_boss, shadow_boss, dungeon):
        self.lifetime -= 1
        if self.lifetime <= 0:
            self.health = 0
            return
        
        self.find_target(player, enemies, boss, final_boss, shadow_boss)

        self.path_update_timer += 1

        if self.target:
            self.move_towards_target(dungeon)
        else:
            self.follow_player(player, dungeon)

        if self.attack_cooldown > 0:
            self.attack_cooldown -= 1

        if self.damage_cooldown > 0:
            self.damage_cooldown -= 1

        if self.blink_timer > 0:
            self.blink_timer -= 1

    def find_target(self, player, enemies, boss, final_boss, shadow_boss):
        if boss:
            self.target = boss
            return

        if final_boss:
            self.target = final_boss
            return

        if shadow_boss:
            self.target = shadow_boss
            return

        closest_dist = float('inf')
        closest_target = None

        for enemy in enemies:
            dx = enemy.x - self.x
            dy = enemy.y - self.y
            dist = (dx ** 2 + dy ** 2) ** 0.5
            if dist < self.detection_range and dist < closest_dist:
                closest_dist = dist
                closest_target = enemy

        self.target = closest_target

    def move_towards_target(self, dungeon):
        if not self.target:
            return

        dx = self.target.x - self.x
        dy = self.target.y - self.y
        dist = (dx ** 2 + dy ** 2) ** 0.5

        if dist <= self.attack_range:
            return

        if dist > 0:
            dx = dx / dist * self.speed
            dy = dy / dist * self.speed
            new_x = self.x + dx
            new_y = self.y + dy
            if not dungeon.is_wall(new_x, self.y, self.width, self.height):
                self.x = new_x
            if not dungeon.is_wall(self.x, new_y, self.width, self.height):
                self.y = new_y

    def follow_player(self, player, dungeon):
        dx = player.x - self.x
        dy = player.y - self.y
        dist = (dx ** 2 + dy ** 2) ** 0.5

        if dist < 50:
            return

        if dist > 0:
            dx = dx / dist * self.speed
            dy = dy / dist * self.speed
            new_x = self.x + dx
            new_y = self.y + dy
            if not dungeon.is_wall(new_x, self.y, self.width, self.height):
                self.x = new_x
            if not dungeon.is_wall(self.x, new_y, self.width, self.height):
                self.y = new_y

    def try_attack(self, enemies, boss, final_boss, shadow_boss):
        if self.attack_cooldown > 0:
            return None

        if not self.target:
            return None

        dx = self.target.x - self.x
        dy = self.target.y - self.y
        dist = (dx ** 2 + dy ** 2) ** 0.5

        if dist <= self.attack_range + 15:
            self.attack_cooldown = self.attack_cooldown_max
            return self.target

        return None

    def take_damage(self, amount=1):
        if self.damage_cooldown > 0:
            return False
        self.health -= amount
        self.blink_timer = 10
        self.damage_cooldown = self.damage_cooldown_max
        return self.health <= 0

    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)

    def draw(self, screen):
        if self.blink_timer > 0 and self.blink_timer % 2 == 1:
            return
        screen.blit(self.sprite, (int(self.x), int(self.y)))

        bar_width = 25
        bar_height = 3
        bar_x = int(self.x + self.width // 2 - bar_width // 2)
        bar_y = int(self.y - 6)

        pygame.draw.rect(screen, (40, 40, 40), (bar_x, bar_y, bar_width, bar_height))
        health_width = int(bar_width * self.health / self.max_health)
        pygame.draw.rect(screen, (150, 150, 180), (bar_x, bar_y, health_width, bar_height))


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
