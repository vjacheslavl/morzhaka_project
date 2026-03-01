import pygame
import sys
import heapq

# Initialize Pygame
pygame.init()

# Screen settings
SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 700
TILE_SIZE = 48

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
LIGHT_GRAY = (180, 180, 180)
GRAY = (100, 100, 100)
DARK_GRAY = (50, 50, 50)
WALL_COLOR = (40, 40, 45)
WALL_BORDER = (25, 25, 30)
YELLOW = (255, 215, 0)
BLUE = (65, 105, 225)
RED = (220, 20, 60)
DARK_RED = (139, 0, 0)
PURPLE = (148, 0, 211)

# Player settings
PIXEL_SIZE = 3
PLAYER_SPEED = 3
ENEMY_SPEED = 2.5
PROJECTILE_SPEED = 8
PROJECTILE_SIZE = 6

# Boss settings
BOSS_PIXEL_SIZE = 9
BOSS_SPEED = 1.5
BOSS_HEALTH = 100
BOSS_PROJECTILE_SIZE = 16
BOSS_PROJECTILE_SPEED = 5
BOSS_SHOOT_INTERVAL = 90


def create_player_sprite():
    """Create pixel art character sprite based on hand-drawn design."""
    # 0 = transparent, 1 = blue (outline), 2 = yellow (fill)
    sprite_data = [
        [1, 1, 1, 1, 1, 1, 1, 1, 1],
        [1, 2, 2, 2, 2, 2, 2, 2, 1],
        [1, 2, 2, 2, 2, 2, 2, 2, 1],
        [1, 1, 1, 2, 2, 2, 1, 1, 1],
        [1, 2, 1, 2, 2, 2, 1, 2, 1],
        [1, 0, 1, 2, 2, 2, 1, 0, 1],
        [1, 1, 1, 2, 2, 2, 1, 1, 1],
        [1, 2, 2, 1, 2, 1, 2, 2, 1],
        [1, 2, 2, 1, 1, 1, 2, 2, 1],
        [1, 2, 2, 1, 2, 1, 2, 2, 1],
        [1, 1, 2, 2, 2, 2, 2, 1, 1],
        [0, 1, 2, 1, 1, 1, 1, 1, 1],
        [0, 1, 2, 1, 0, 0, 1, 1, 0],
        [1, 1, 1, 1, 0, 0, 1, 1, 1]
    ]
    
    width = len(sprite_data[0]) * PIXEL_SIZE
    height = len(sprite_data) * PIXEL_SIZE
    
    sprite = pygame.Surface((width, height), pygame.SRCALPHA)
    
    for y, row in enumerate(sprite_data):
        for x, pixel in enumerate(row):
            if pixel == 1:
                color = BLUE
            elif pixel == 2:
                color = YELLOW
            else:
                continue
            
            pygame.draw.rect(
                sprite, color,
                (x * PIXEL_SIZE, y * PIXEL_SIZE, PIXEL_SIZE, PIXEL_SIZE)
            )
    
    return sprite


def create_enemy_sprite():
    """Create enemy sprite - same as player but red instead of yellow."""
    sprite_data = [
        [1, 1, 1, 1, 1, 1, 1, 1, 1],
        [1, 2, 2, 2, 2, 2, 2, 2, 1],
        [1, 2, 2, 2, 2, 2, 2, 2, 1],
        [1, 1, 1, 2, 2, 2, 1, 1, 1],
        [1, 2, 1, 2, 2, 2, 1, 2, 1],
        [1, 0, 1, 2, 2, 2, 1, 0, 1],
        [1, 1, 1, 2, 2, 2, 1, 1, 1],
        [1, 2, 2, 1, 2, 1, 2, 2, 1],
        [1, 2, 2, 1, 1, 1, 2, 2, 1],
        [1, 2, 2, 1, 2, 1, 2, 2, 1],
        [1, 1, 2, 2, 2, 2, 2, 1, 1],
        [0, 1, 2, 1, 1, 1, 1, 1, 1],
        [0, 1, 2, 1, 0, 0, 1, 1, 0],
        [1, 1, 1, 1, 0, 0, 1, 1, 1]
    ]
    
    width = len(sprite_data[0]) * PIXEL_SIZE
    height = len(sprite_data) * PIXEL_SIZE
    
    sprite = pygame.Surface((width, height), pygame.SRCALPHA)
    
    for y, row in enumerate(sprite_data):
        for x, pixel in enumerate(row):
            if pixel == 1:
                color = DARK_GRAY
            elif pixel == 2:
                color = RED
            else:
                continue
            
            pygame.draw.rect(
                sprite, color,
                (x * PIXEL_SIZE, y * PIXEL_SIZE, PIXEL_SIZE, PIXEL_SIZE)
            )
    
    return sprite


def find_path(start_tile, end_tile, tiles):
    """A* pathfinding algorithm to find path between two tiles."""
    if start_tile == end_tile:
        return [end_tile]
    
    rows = len(tiles)
    cols = len(tiles[0])
    
    def heuristic(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])
    
    def get_neighbors(pos):
        x, y = pos
        neighbors = []
        for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
            nx, ny = x + dx, y + dy
            if 0 <= nx < cols and 0 <= ny < rows and tiles[ny][nx] == 0:
                neighbors.append((nx, ny))
        return neighbors
    
    open_set = []
    heapq.heappush(open_set, (0, start_tile))
    came_from = {}
    g_score = {start_tile: 0}
    f_score = {start_tile: heuristic(start_tile, end_tile)}
    open_set_hash = {start_tile}
    
    while open_set:
        current = heapq.heappop(open_set)[1]
        open_set_hash.discard(current)
        
        if current == end_tile:
            path = []
            while current in came_from:
                path.append(current)
                current = came_from[current]
            path.reverse()
            return path
        
        for neighbor in get_neighbors(current):
            tentative_g = g_score[current] + 1
            
            if neighbor not in g_score or tentative_g < g_score[neighbor]:
                came_from[neighbor] = current
                g_score[neighbor] = tentative_g
                f_score[neighbor] = tentative_g + heuristic(neighbor, end_tile)
                
                if neighbor not in open_set_hash:
                    heapq.heappush(open_set, (f_score[neighbor], neighbor))
                    open_set_hash.add(neighbor)
    
    return []


class Enemy:
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

    def move_towards_player(self, player, dungeon):
        self.path_update_timer += 1
        if self.path_update_timer >= self.path_update_interval or not self.path:
            self.path_update_timer = 0
            self.update_path(player, dungeon)
        
        if not self.path:
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

    def update_path(self, player, dungeon):
        my_tile = (int((self.x + self.width // 2) // TILE_SIZE),
                   int((self.y + self.height // 2) // TILE_SIZE))
        player_tile = (int((player.x + player.width // 2) // TILE_SIZE),
                       int((player.y + player.height // 2) // TILE_SIZE))
        
        self.path = find_path(my_tile, player_tile, dungeon.tiles)

    def draw(self, screen):
        screen.blit(self.sprite, (self.x, self.y))

    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)

    def collides_with_player(self, player):
        return self.get_rect().colliderect(player.get_rect())


def create_boss_sprite():
    """Create boss sprite - 3x bigger enemy with red color."""
    sprite_data = [
        [1, 1, 1, 1, 1, 1, 1, 1, 1],
        [1, 2, 2, 2, 2, 2, 2, 2, 1],
        [1, 2, 2, 2, 2, 2, 2, 2, 1],
        [1, 1, 1, 2, 2, 2, 1, 1, 1],
        [1, 2, 1, 2, 2, 2, 1, 2, 1],
        [1, 0, 1, 2, 2, 2, 1, 0, 1],
        [1, 1, 1, 2, 2, 2, 1, 1, 1],
        [1, 2, 2, 1, 2, 1, 2, 2, 1],
        [1, 2, 2, 1, 1, 1, 2, 2, 1],
        [1, 2, 2, 1, 2, 1, 2, 2, 1],
        [1, 1, 2, 2, 2, 2, 2, 1, 1],
        [0, 1, 2, 1, 1, 1, 1, 1, 1],
        [0, 1, 2, 1, 0, 0, 1, 1, 0],
        [1, 1, 1, 1, 0, 0, 1, 1, 1]
    ]
    
    width = len(sprite_data[0]) * BOSS_PIXEL_SIZE
    height = len(sprite_data) * BOSS_PIXEL_SIZE
    
    sprite = pygame.Surface((width, height), pygame.SRCALPHA)
    
    for y, row in enumerate(sprite_data):
        for x, pixel in enumerate(row):
            if pixel == 1:
                color = BLACK
            elif pixel == 2:
                color = DARK_RED
            else:
                continue
            
            pygame.draw.rect(
                sprite, color,
                (x * BOSS_PIXEL_SIZE, y * BOSS_PIXEL_SIZE, BOSS_PIXEL_SIZE, BOSS_PIXEL_SIZE)
            )
    
    return sprite


class BossProjectile:
    def __init__(self, x, y, direction):
        self.x = x
        self.y = y
        self.direction = direction
        self.speed = BOSS_PROJECTILE_SPEED
        self.size = BOSS_PROJECTILE_SIZE
        self.active = True

    def update(self, dungeon):
        self.x += self.direction[0] * self.speed
        self.y += self.direction[1] * self.speed
        
        if (self.x < 0 or self.x > SCREEN_WIDTH or
            self.y < 0 or self.y > SCREEN_HEIGHT):
            self.active = False

    def draw(self, screen):
        pygame.draw.rect(screen, RED, (self.x, self.y, self.size, self.size))

    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.size, self.size)

    def collides_with_player(self, player):
        return self.get_rect().colliderect(player.get_rect())


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

    def move_towards_player(self, player, dungeon):
        dx = player.x - self.x
        dy = player.y - self.y
        
        distance = (dx ** 2 + dy ** 2) ** 0.5
        if distance < 100:
            return
        
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
            
            dx = player.x - self.x
            dy = player.y - self.y
            distance = (dx ** 2 + dy ** 2) ** 0.5
            
            if distance > 0:
                dx = dx / distance
                dy = dy / distance
                
                proj_x = self.x + self.width // 2 - BOSS_PROJECTILE_SIZE // 2
                proj_y = self.y + self.height // 2 - BOSS_PROJECTILE_SIZE // 2
                return BossProjectile(proj_x, proj_y, (dx, dy))
        return None

    def take_damage(self, amount=1):
        self.health -= amount
        return self.health <= 0

    def draw(self, screen):
        screen.blit(self.sprite, (self.x, self.y))
        
        bar_width = self.width
        bar_height = 8
        bar_x = self.x
        bar_y = self.y - 15
        
        pygame.draw.rect(screen, DARK_RED, (bar_x, bar_y, bar_width, bar_height))
        health_width = int(bar_width * (self.health / self.max_health))
        pygame.draw.rect(screen, RED, (bar_x, bar_y, health_width, bar_height))
        pygame.draw.rect(screen, WHITE, (bar_x, bar_y, bar_width, bar_height), 1)

    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)

    def collides_with_player(self, player):
        return self.get_rect().colliderect(player.get_rect())


class Projectile:
    def __init__(self, x, y, direction):
        self.x = x
        self.y = y
        self.direction = direction
        self.speed = PROJECTILE_SPEED
        self.size = PROJECTILE_SIZE
        self.active = True

    def update(self, dungeon):
        self.x += self.direction[0] * self.speed
        self.y += self.direction[1] * self.speed
        
        tile_x = int((self.x + self.size // 2) // TILE_SIZE)
        tile_y = int((self.y + self.size // 2) // TILE_SIZE)
        
        if (tile_x < 0 or tile_x >= dungeon.width or
            tile_y < 0 or tile_y >= dungeon.height or
            dungeon.tiles[tile_y][tile_x] == 1):
            self.active = False

    def draw(self, screen):
        pygame.draw.rect(screen, PURPLE, (self.x, self.y, self.size, self.size))

    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.size, self.size)

    def collides_with_enemy(self, enemy):
        return self.get_rect().colliderect(enemy.get_rect())


class Player:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.sprite = create_player_sprite()
        self.width = self.sprite.get_width()
        self.height = self.sprite.get_height()
        self.speed = PLAYER_SPEED
        self.max_health = 4
        self.health = self.max_health
        self.last_direction = (1, 0)

    def move(self, dx, dy, dungeon):
        new_x = self.x + dx * self.speed
        new_y = self.y + dy * self.speed
        
        if not dungeon.is_wall(new_x, new_y, self.width, self.height):
            self.x = new_x
            self.y = new_y
            self.last_direction = (dx, dy)

    def shoot(self):
        proj_x = self.x + self.width // 2 - PROJECTILE_SIZE // 2
        proj_y = self.y + self.height // 2 - PROJECTILE_SIZE // 2
        return Projectile(proj_x, proj_y, self.last_direction)

    def take_damage(self, amount=1):
        self.health = max(0, self.health - amount)
        return self.health <= 0

    def heal(self, amount=1):
        self.health = min(self.max_health, self.health + amount)

    def draw(self, screen):
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


class Dungeon:
    def __init__(self, level_data, level_num):
        self.level_num = level_num
        self.tiles = level_data['tiles']
        self.width = len(self.tiles[0])
        self.height = len(self.tiles)
        self.spawn_point = level_data['spawn']
        self.exit_point = level_data['exit']

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

    def draw(self, screen):
        for y, row in enumerate(self.tiles):
            for x, tile in enumerate(row):
                rect = pygame.Rect(x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE)
                
                if tile == 1:
                    pygame.draw.rect(screen, WALL_COLOR, rect)
                    pygame.draw.rect(screen, WALL_BORDER, rect, 2)
                else:
                    pygame.draw.rect(screen, LIGHT_GRAY, rect)
        
        if self.exit_point:
            exit_rect = pygame.Rect(
                self.exit_point[0] * TILE_SIZE + 4,
                self.exit_point[1] * TILE_SIZE + 4,
                TILE_SIZE - 8,
                TILE_SIZE - 8
            )
            pygame.draw.rect(screen, YELLOW, exit_rect)


def create_levels():
    levels = []
    
    # Level 1 - Simple introduction
    level1 = {
        'tiles': [
            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
            [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
            [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
            [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
            [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
            [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
            [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
            [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
            [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
            [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
            [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
            [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
            [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
        ],
        'spawn': (2, 2),
        'exit': (22, 11),
        'enemy_count': 2
    }
    levels.append(level1)
    
    # Level 2 - Maze-like
    level2 = {
        'tiles': [
            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
            [1, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
            [1, 0, 1, 0, 1, 0, 1, 1, 1, 1, 1, 0, 1, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 1],
            [1, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
            [1, 0, 1, 1, 1, 1, 1, 1, 1, 0, 1, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 1],
            [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
            [1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 1, 0, 1, 1, 1, 1, 1, 1, 1, 0, 1, 1, 1, 1, 1],
            [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1],
            [1, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 1, 0, 1, 1, 1, 0, 1],
            [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1],
            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 1, 1, 1, 1, 1, 0, 1, 1, 1],
            [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
            [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
        ],
        'spawn': (1, 1),
        'exit': (23, 11),
        'enemy_count': 3
    }
    levels.append(level2)
    
    # Level 3 - Complex dungeon
    level3 = {
        'tiles': [
            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
            [1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1],
            [1, 0, 1, 1, 1, 0, 1, 0, 1, 1, 1, 1, 1, 1, 1, 0, 1, 0, 1, 1, 1, 1, 1, 0, 1],
            [1, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 1],
            [1, 0, 1, 0, 1, 1, 1, 1, 1, 1, 1, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 1, 0, 1],
            [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1],
            [1, 1, 1, 1, 1, 0, 1, 1, 1, 1, 1, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 1, 0, 1],
            [1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1],
            [1, 0, 1, 1, 1, 1, 1, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 1, 1, 1, 0, 1],
            [1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
            [1, 1, 1, 1, 1, 1, 1, 0, 1, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 1],
            [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
            [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
        ],
        'spawn': (1, 1),
        'exit': (23, 11),
        'enemy_count': 6
    }
    levels.append(level3)
    
    # Level 4 - Boss Arena (empty room)
    boss_level = {
        'tiles': [
            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
            [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
            [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
            [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
            [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
            [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
            [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
            [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
            [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
            [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
            [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
            [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
            [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
        ],
        'spawn': (2, 7),
        'exit': None,
        'enemy_count': 0,
        'is_boss_level': True
    }
    levels.append(boss_level)
    
    return levels


class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Dungeon Crawler")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)
        
        self.levels = create_levels()
        self.current_level = 0
        self.dungeon = Dungeon(self.levels[self.current_level], self.current_level + 1)
        
        spawn = self.dungeon.spawn_point
        self.player = Player(
            spawn[0] * TILE_SIZE + 4,
            spawn[1] * TILE_SIZE + 4
        )
        
        self.enemies = []
        self.spawn_enemies()
        self.damage_cooldown = 0
        
        self.projectiles = []
        self.shoot_cooldown = 0
        self.enemy_spawn_timer = 0
        self.enemy_spawn_interval = 180
        
        self.boss = None
        self.boss_projectiles = []
        self.is_boss_level = False
        
        self.game_won = False
        self.game_over = False
        self.running = True

    def spawn_enemies(self):
        self.enemies = []
        self.boss = None
        self.boss_projectiles = []
        level_data = self.levels[self.current_level]
        
        self.is_boss_level = level_data.get('is_boss_level', False)
        
        if self.is_boss_level:
            boss_x = 20 * TILE_SIZE
            boss_y = 6 * TILE_SIZE
            self.boss = Boss(boss_x, boss_y)
            return
        
        enemy_count = level_data.get('enemy_count', 0)
        exit_pos = level_data['exit']
        tiles = level_data['tiles']
        
        offsets = [
            (-1, 0), (1, 0), (0, -1), (0, 1),
            (-1, -1), (1, -1), (-1, 1), (1, 1),
            (-2, 0), (2, 0), (0, -2), (0, 2),
            (-2, -1), (2, -1), (-2, 1), (2, 1)
        ]
        
        spawned = 0
        for offset in offsets:
            if spawned >= enemy_count:
                break
            
            tile_x = exit_pos[0] + offset[0]
            tile_y = exit_pos[1] + offset[1]
            
            if 0 <= tile_y < len(tiles) and 0 <= tile_x < len(tiles[0]):
                if tiles[tile_y][tile_x] == 0:
                    enemy_x = tile_x * TILE_SIZE + 4
                    enemy_y = tile_y * TILE_SIZE + 4
                    self.enemies.append(Enemy(enemy_x, enemy_y))
                    spawned += 1

    def spawn_one_enemy(self):
        if self.is_boss_level:
            return
        level_data = self.levels[self.current_level]
        exit_pos = level_data['exit']
        if exit_pos is None:
            return
        tiles = level_data['tiles']
        
        offsets = [
            (-1, 0), (1, 0), (0, -1), (0, 1),
            (-1, -1), (1, -1), (-1, 1), (1, 1),
            (-2, 0), (2, 0), (0, -2), (0, 2)
        ]
        
        for offset in offsets:
            tile_x = exit_pos[0] + offset[0]
            tile_y = exit_pos[1] + offset[1]
            
            if 0 <= tile_y < len(tiles) and 0 <= tile_x < len(tiles[0]):
                if tiles[tile_y][tile_x] == 0:
                    enemy_x = tile_x * TILE_SIZE + 4
                    enemy_y = tile_y * TILE_SIZE + 4
                    self.enemies.append(Enemy(enemy_x, enemy_y))
                    return

    def next_level(self):
        self.current_level += 1
        
        if self.current_level >= len(self.levels):
            self.game_won = True
            return
        
        self.dungeon = Dungeon(self.levels[self.current_level], self.current_level + 1)
        spawn = self.dungeon.spawn_point
        self.player.x = spawn[0] * TILE_SIZE + 4
        self.player.y = spawn[1] * TILE_SIZE + 4
        self.spawn_enemies()
        self.projectiles = []
        self.damage_cooldown = 0
        self.shoot_cooldown = 0
        self.enemy_spawn_timer = 0

    def handle_input(self):
        keys = pygame.key.get_pressed()
        
        dx, dy = 0, 0
        
        if keys[pygame.K_w]:
            dy = -1
        if keys[pygame.K_s]:
            dy = 1
        if keys[pygame.K_a]:
            dx = -1
        if keys[pygame.K_d]:
            dx = 1
        
        if dx != 0 or dy != 0:
            self.player.move(dx, dy, self.dungeon)
        
        if keys[pygame.K_SPACE] and self.shoot_cooldown <= 0:
            self.projectiles.append(self.player.shoot())
            self.shoot_cooldown = 15

    def update(self):
        if self.game_won or self.game_over:
            return
        
        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= 1
        
        if not self.is_boss_level:
            self.enemy_spawn_timer += 1
            if self.enemy_spawn_timer >= self.enemy_spawn_interval:
                self.enemy_spawn_timer = 0
                self.spawn_one_enemy()
        
        for projectile in self.projectiles:
            projectile.update(self.dungeon)
        
        for projectile in self.projectiles:
            if not projectile.active:
                continue
            for enemy in self.enemies:
                if projectile.collides_with_enemy(enemy):
                    projectile.active = False
                    self.enemies.remove(enemy)
                    break
        
        if self.boss:
            for projectile in self.projectiles:
                if not projectile.active:
                    continue
                if projectile.get_rect().colliderect(self.boss.get_rect()):
                    projectile.active = False
                    if self.boss.take_damage(1):
                        self.boss = None
                        self.game_won = True
                    break
        
        self.projectiles = [p for p in self.projectiles if p.active]
        
        if self.boss:
            self.boss.move_towards_player(self.player, self.dungeon)
            boss_proj = self.boss.shoot_at_player(self.player)
            if boss_proj:
                self.boss_projectiles.append(boss_proj)
        
        for proj in self.boss_projectiles:
            proj.update(self.dungeon)
        
        self.boss_projectiles = [p for p in self.boss_projectiles if p.active]
        
        for enemy in self.enemies:
            enemy.move_towards_player(self.player, self.dungeon)
        
        if self.damage_cooldown > 0:
            self.damage_cooldown -= 1
        else:
            for enemy in self.enemies:
                if enemy.collides_with_player(self.player):
                    if self.player.take_damage():
                        self.game_over = True
                    self.damage_cooldown = 60
                    break
            
            if self.boss and self.boss.collides_with_player(self.player):
                if self.player.take_damage():
                    self.game_over = True
                self.damage_cooldown = 60
            
            for proj in self.boss_projectiles:
                if proj.collides_with_player(self.player):
                    proj.active = False
                    if self.player.take_damage():
                        self.game_over = True
                    self.damage_cooldown = 60
                    break
        
        if not self.is_boss_level and self.dungeon.check_exit(self.player):
            self.next_level()

    def draw(self):
        self.screen.fill(BLACK)
        
        if self.game_won:
            win_text = self.font.render("Congratulations! You escaped the dungeon!", True, GREEN)
            restart_text = self.small_font.render("Press R to restart or ESC to quit", True, WHITE)
            self.screen.blit(win_text, (SCREEN_WIDTH // 2 - win_text.get_width() // 2, SCREEN_HEIGHT // 2 - 20))
            self.screen.blit(restart_text, (SCREEN_WIDTH // 2 - restart_text.get_width() // 2, SCREEN_HEIGHT // 2 + 20))
        elif self.game_over:
            over_text = self.font.render("GAME OVER", True, RED)
            restart_text = self.small_font.render("Press R to restart or ESC to quit", True, WHITE)
            self.screen.blit(over_text, (SCREEN_WIDTH // 2 - over_text.get_width() // 2, SCREEN_HEIGHT // 2 - 20))
            self.screen.blit(restart_text, (SCREEN_WIDTH // 2 - restart_text.get_width() // 2, SCREEN_HEIGHT // 2 + 20))
        else:
            self.dungeon.draw(self.screen)
            self.player.draw(self.screen)
            
            for enemy in self.enemies:
                enemy.draw(self.screen)
            
            if self.boss:
                self.boss.draw(self.screen)
            
            for projectile in self.projectiles:
                projectile.draw(self.screen)
            
            for proj in self.boss_projectiles:
                proj.draw(self.screen)
            
            if self.is_boss_level:
                level_text = self.font.render("BOSS FIGHT!", True, RED)
            else:
                level_text = self.font.render(f"Level: {self.current_level + 1}/{len(self.levels)}", True, WHITE)
            self.screen.blit(level_text, (10, 10))
            
            health_label = self.small_font.render("HP:", True, WHITE)
            self.screen.blit(health_label, (SCREEN_WIDTH - 140, 10))
            self.player.draw_health(self.screen, SCREEN_WIDTH - 110, 8)
            
            if self.is_boss_level:
                hint_text = self.small_font.render("Defeat the boss to win!", True, RED)
            else:
                hint_text = self.small_font.render("Find the yellow exit! Avoid red enemies!", True, YELLOW)
            self.screen.blit(hint_text, (10, 45))
            
            controls_text = self.small_font.render("WASD to move, SPACE to shoot", True, WHITE)
            self.screen.blit(controls_text, (10, SCREEN_HEIGHT - 30))
        
        pygame.display.flip()

    def run(self):
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.running = False
                    elif event.key == pygame.K_r and (self.game_won or self.game_over):
                        self.current_level = 0
                        self.dungeon = Dungeon(self.levels[self.current_level], self.current_level + 1)
                        spawn = self.dungeon.spawn_point
                        self.player.x = spawn[0] * TILE_SIZE + 4
                        self.player.y = spawn[1] * TILE_SIZE + 4
                        self.player.health = self.player.max_health
                        self.player.last_direction = (1, 0)
                        self.spawn_enemies()
                        self.projectiles = []
                        self.damage_cooldown = 0
                        self.shoot_cooldown = 0
                        self.enemy_spawn_timer = 0
                        self.game_won = False
                        self.game_over = False
            
            self.handle_input()
            self.update()
            self.draw()
            
            self.clock.tick(60)
        
        pygame.quit()
        sys.exit()


if __name__ == "__main__":
    game = Game()
    game.run()
