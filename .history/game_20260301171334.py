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
GRAY = (100, 100, 100)
DARK_GRAY = (50, 50, 50)
BROWN = (139, 69, 19)
YELLOW = (255, 215, 0)
BLUE = (65, 105, 225)
RED = (220, 20, 60)
DARK_RED = (139, 0, 0)

# Player settings
PIXEL_SIZE = 3
PLAYER_SPEED = 3
ENEMY_SPEED = 2.5


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

    def move(self, dx, dy, dungeon):
        new_x = self.x + dx * self.speed
        new_y = self.y + dy * self.speed
        
        if not dungeon.is_wall(new_x, new_y, self.width, self.height):
            self.x = new_x
            self.y = new_y

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
                    pygame.draw.rect(screen, GRAY, rect)
                    pygame.draw.rect(screen, DARK_GRAY, rect, 2)
                else:
                    pygame.draw.rect(screen, BROWN, rect)
        
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
        'enemy_count': 2
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
        'enemy_count': 4
    }
    levels.append(level3)
    
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
        
        self.game_won = False
        self.game_over = False
        self.running = True

    def spawn_enemies(self):
        self.enemies = []
        level_data = self.levels[self.current_level]
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
        self.damage_cooldown = 0

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

    def update(self):
        if self.game_won or self.game_over:
            return
        
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
        
        if self.dungeon.check_exit(self.player):
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
            
            level_text = self.font.render(f"Level: {self.current_level + 1}/{len(self.levels)}", True, WHITE)
            self.screen.blit(level_text, (10, 10))
            
            health_label = self.small_font.render("HP:", True, WHITE)
            self.screen.blit(health_label, (SCREEN_WIDTH - 140, 10))
            self.player.draw_health(self.screen, SCREEN_WIDTH - 110, 8)
            
            hint_text = self.small_font.render("Find the yellow exit! Avoid red enemies!", True, YELLOW)
            self.screen.blit(hint_text, (10, 45))
            
            controls_text = self.small_font.render("WASD to move", True, WHITE)
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
                        self.spawn_enemies()
                        self.damage_cooldown = 0
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
