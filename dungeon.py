import pygame
import random
from constants import TILE_SIZE, PIXEL_SIZE
from entities import Laser


class Dungeon:
    def __init__(self, level_data, level_num):
        self.level_num = level_num
        self.tiles = level_data['tiles']
        self.width = len(self.tiles[0])
        self.height = len(self.tiles)
        self.spawn_point = level_data['spawn']
        self.exit_point = level_data['exit']
        self.location = level_data.get('location', 1)
        self.animation_timer = 0
        self.P = PIXEL_SIZE
        
        if self.location == 0:
            self.colors = {
                'wall_main': (60, 120, 50),
                'wall_light': (80, 150, 65),
                'wall_dark': (40, 90, 35),
                'wall_outline': (30, 70, 25),
                'floor_main': (110, 90, 60),
                'floor_light': (130, 110, 75),
                'floor_dark': (85, 70, 45),
                'floor_accent': (100, 80, 55),
            }
        elif self.location == 3:
            self.colors = {
                'wall_main': (45, 45, 50),
                'wall_light': (70, 70, 80),
                'wall_dark': (25, 25, 30),
                'wall_outline': (15, 15, 18),
                'floor_main': (65, 65, 70),
                'floor_light': (85, 85, 95),
                'floor_dark': (40, 40, 45),
                'floor_accent': (55, 55, 60),
            }
        elif self.location == 2:
            self.colors = {
                'wall_main': (80, 120, 160),
                'wall_light': (120, 160, 200),
                'wall_dark': (50, 80, 110),
                'wall_outline': (30, 50, 70),
                'floor_main': (170, 190, 210),
                'floor_light': (200, 215, 230),
                'floor_dark': (130, 155, 180),
                'floor_accent': (100, 140, 180),
            }
        else:
            self.colors = {
                'wall_main': (85, 65, 50),
                'wall_light': (120, 95, 75),
                'wall_dark': (55, 42, 32),
                'wall_outline': (35, 25, 18),
                'floor_main': (140, 125, 105),
                'floor_light': (170, 155, 130),
                'floor_dark': (100, 88, 72),
                'floor_accent': (125, 110, 90),
            }
        
        self.generate_decorations()
        self.create_cached_surfaces()
        self.create_lasers(level_data.get('lasers', []))
    
    def create_lasers(self, laser_data):
        self.lasers = []
        for laser_def in laser_data:
            start = laser_def['start']
            end = laser_def['end']
            on_duration = laser_def.get('on_duration', 90)
            off_duration = laser_def.get('off_duration', 90)
            start_on = laser_def.get('start_on', True)
            self.lasers.append(Laser(start, end, on_duration, off_duration, start_on))
    
    def generate_decorations(self):
        random.seed(self.level_num * 1337)
        
        self.floor_pattern = {}
        self.wall_pattern = {}
        self.torches = []
        
        for y in range(self.height):
            for x in range(self.width):
                if self.tiles[y][x] == 0:
                    self.floor_pattern[(x, y)] = random.randint(0, 5)
                else:
                    self.wall_pattern[(x, y)] = random.randint(0, 3)
        
        for y in range(self.height):
            for x in range(self.width):
                if self.tiles[y][x] == 1:
                    if y + 1 < self.height and self.tiles[y + 1][x] == 0:
                        if random.random() < 0.1:
                            self.torches.append((x, y))

    def create_cached_surfaces(self):
        self.static_surface = pygame.Surface((self.width * TILE_SIZE, self.height * TILE_SIZE))
        
        for y in range(self.height):
            for x in range(self.width):
                if self.tiles[y][x] == 1:
                    self.render_wall_tile(self.static_surface, x, y)
                else:
                    self.render_floor_tile(self.static_surface, x, y)
        
        self.render_shadows(self.static_surface)
        
        self.torch_frames = []
        for frame in range(4):
            self.torch_frames.append(self.create_torch_frame(frame))
        
        self.portal_frames = []
        for frame in range(4):
            self.portal_frames.append(self.create_portal_frame(frame))

    def px_surf(self, surface, x, y, color):
        pygame.draw.rect(surface, color, (x, y, self.P, self.P))

    def render_floor_tile(self, surface, x, y):
        tx, ty = x * TILE_SIZE, y * TILE_SIZE
        P = self.P
        pattern = self.floor_pattern.get((x, y), 0)
        c = self.colors
        
        pygame.draw.rect(surface, c['floor_main'], (tx, ty, TILE_SIZE, TILE_SIZE))
        
        if self.location == 0:
            grass_colors = [(90, 140, 70), (80, 130, 60), (100, 150, 80)]
            if pattern in [1, 2]:
                self.px_surf(surface, tx + P * 3, ty + P * 5, grass_colors[pattern % 3])
                self.px_surf(surface, tx + P * 10, ty + P * 8, grass_colors[(pattern + 1) % 3])
            if pattern in [3, 4]:
                self.px_surf(surface, tx + P * 7, ty + P * 3, grass_colors[0])
                self.px_surf(surface, tx + P * 12, ty + P * 10, grass_colors[1])
        else:
            if pattern == 1:
                self.px_surf(surface, tx + P * 3, ty + P * 5, c['floor_dark'])
                self.px_surf(surface, tx + P * 10, ty + P * 8, c['floor_dark'])
            elif pattern == 2:
                self.px_surf(surface, tx + P * 7, ty + P * 4, c['floor_light'])
                self.px_surf(surface, tx + P * 12, ty + P * 11, c['floor_light'])
            elif pattern == 3:
                self.px_surf(surface, tx + P * 5, ty + P * 9, c['floor_dark'])
            elif pattern == 4:
                self.px_surf(surface, tx + P * 2, ty + P * 12, c['floor_light'])
                self.px_surf(surface, tx + P * 9, ty + P * 3, c['floor_dark'])

    def render_wall_tile(self, surface, x, y):
        tx, ty = x * TILE_SIZE, y * TILE_SIZE
        P = self.P
        pattern = self.wall_pattern.get((x, y), 0)
        c = self.colors
        
        pygame.draw.rect(surface, c['wall_main'], (tx, ty, TILE_SIZE, TILE_SIZE))
        
        if self.location == 0:
            leaf_positions = [
                (2, 2), (5, 1), (9, 3), (12, 1), (14, 2),
                (3, 6), (7, 5), (11, 7), (13, 5),
                (1, 10), (4, 9), (8, 11), (10, 9), (14, 10),
                (2, 13), (6, 12), (9, 14), (12, 13)
            ]
            for lx, ly in leaf_positions:
                if (lx + ly + pattern) % 3 == 0:
                    self.px_surf(surface, tx + P * lx, ty + P * ly, c['wall_light'])
                elif (lx + ly + pattern) % 3 == 1:
                    self.px_surf(surface, tx + P * lx, ty + P * ly, c['wall_dark'])
            
            trunk_color = (80, 60, 40)
            self.px_surf(surface, tx + P * 7, ty + P * 14, trunk_color)
            self.px_surf(surface, tx + P * 8, ty + P * 14, trunk_color)
            self.px_surf(surface, tx + P * 7, ty + P * 15, trunk_color)
            self.px_surf(surface, tx + P * 8, ty + P * 15, trunk_color)
        else:
            for row in range(4):
                brick_y = ty + row * 4 * P
                offset = (8 * P) if row % 2 == 1 else 0
                
                for i in range(16):
                    self.px_surf(surface, tx + i * P, brick_y, c['wall_dark'])
                
                for bx in range(-1, 3):
                    line_x = tx + bx * 8 * P + offset
                    if line_x >= tx and line_x < tx + TILE_SIZE:
                        for by in range(4):
                            if brick_y + by * P < ty + TILE_SIZE:
                                self.px_surf(surface, line_x, brick_y + by * P, c['wall_dark'])
            
            self.px_surf(surface, tx + P, ty + P, c['wall_light'])
            self.px_surf(surface, tx + P * 2, ty + P, c['wall_light'])
            self.px_surf(surface, tx + P, ty + P * 2, c['wall_light'])
            
            if pattern == 1:
                self.px_surf(surface, tx + P * 10, ty + P * 6, c['wall_dark'])
            elif pattern == 2:
                self.px_surf(surface, tx + P * 5, ty + P * 10, c['wall_light'])

    def render_shadows(self, surface):
        P = self.P
        c = self.colors
        
        for y in range(self.height):
            for x in range(self.width):
                if self.tiles[y][x] == 0:
                    tx, ty = x * TILE_SIZE, y * TILE_SIZE
                    
                    if y > 0 and self.tiles[y - 1][x] == 1:
                        pygame.draw.rect(surface, c['floor_dark'], (tx, ty, TILE_SIZE, P * 2))

    def create_torch_frame(self, frame):
        P = self.P
        surf = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
        
        holder = (90, 65, 40)
        
        pygame.draw.rect(surf, holder, (7 * P, 12 * P, 2 * P, 3 * P))
        
        flame_main = [(255, 200, 60), (255, 180, 50), (255, 220, 80), (255, 160, 40)]
        flame_top = [(255, 120, 30), (255, 100, 25), (255, 140, 40), (255, 90, 20)]
        
        pygame.draw.rect(surf, flame_main[frame], (7 * P, 10 * P, 2 * P, 2 * P))
        pygame.draw.rect(surf, flame_top[frame], (7 * P, 9 * P, 2 * P, P))
        
        if frame == 0 or frame == 2:
            pygame.draw.rect(surf, flame_top[frame], (7 * P, 8 * P, P, P))
        else:
            pygame.draw.rect(surf, flame_top[frame], (8 * P, 8 * P, P, P))
        
        return surf

    def create_portal_frame(self, frame):
        P = self.P
        surf = pygame.Surface((TILE_SIZE, TILE_SIZE))
        surf.fill(self.colors['floor_main'])
        
        colors = [
            (200, 170, 60),
            (230, 200, 80),
            (255, 230, 120),
            (255, 245, 180)
        ]
        
        c = [colors[(i + frame) % 4] for i in range(4)]
        
        pygame.draw.rect(surf, c[0], (3 * P, 3 * P, 10 * P, 10 * P))
        pygame.draw.rect(surf, c[1], (5 * P, 5 * P, 6 * P, 6 * P))
        pygame.draw.rect(surf, c[2], (6 * P, 6 * P, 4 * P, 4 * P))
        pygame.draw.rect(surf, c[3], (7 * P, 7 * P, 2 * P, 2 * P))
        
        return surf

    def is_wall(self, x, y, width, height):
        corners = [
            (x, y),
            (x + width - 1, y),
            (x, y + height - 1),
            (x + width - 1, y + height - 1)
        ]
        
        for cx, cy in corners:
            tile_x = int(cx // TILE_SIZE)
            tile_y = int(cy // TILE_SIZE)
            
            if tile_x < 0 or tile_x >= self.width or tile_y < 0 or tile_y >= self.height:
                return True
            
            if self.tiles[tile_y][tile_x] == 1:
                return True
        
        return False

    def check_exit(self, player):
        if self.exit_point is None:
            return False
        player_rect = player.get_rect()
        exit_rect = pygame.Rect(
            self.exit_point[0] * TILE_SIZE + TILE_SIZE // 4,
            self.exit_point[1] * TILE_SIZE + TILE_SIZE // 4,
            TILE_SIZE // 2,
            TILE_SIZE // 2
        )
        return player_rect.colliderect(exit_rect)

    def update(self):
        self.animation_timer += 1
        for laser in self.lasers:
            laser.update()

    def check_laser_collision(self, player):
        for laser in self.lasers:
            if laser.collides_with_player(player):
                return True
        return False

    def draw(self, screen):
        screen.blit(self.static_surface, (0, 0))
        
        frame = (self.animation_timer // 8) % 4
        for x, y in self.torches:
            screen.blit(self.torch_frames[frame], (x * TILE_SIZE, y * TILE_SIZE))
        
        for laser in self.lasers:
            laser.draw(screen)
        
        if self.exit_point:
            portal_frame = (self.animation_timer // 10) % 4
            ex, ey = self.exit_point
            screen.blit(self.portal_frames[portal_frame], (ex * TILE_SIZE, ey * TILE_SIZE))
