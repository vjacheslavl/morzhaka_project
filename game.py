import pygame
import sys
import heapq

# Initialize Pygame
pygame.init()
pygame.mixer.init()

# Sound effects
def create_shoot_sound():
    sample_rate = 22050
    duration = 0.1
    import array
    n_samples = int(sample_rate * duration)
    buf = array.array('h', [0] * n_samples)
    for i in range(n_samples):
        t = i / sample_rate
        freq = 800 - (t * 4000)
        import math
        buf[i] = int(4000 * math.sin(2 * math.pi * freq * t) * (1 - t / duration))
    sound = pygame.mixer.Sound(buffer=buf)
    sound.set_volume(0.3)
    return sound

def create_damage_sound():
    sample_rate = 22050
    duration = 0.15
    import array
    n_samples = int(sample_rate * duration)
    buf = array.array('h', [0] * n_samples)
    for i in range(n_samples):
        t = i / sample_rate
        freq = 200 + (t * 100)
        import math
        buf[i] = int(6000 * math.sin(2 * math.pi * freq * t) * (1 - t / duration))
    sound = pygame.mixer.Sound(buffer=buf)
    sound.set_volume(0.4)
    return sound

def create_kill_sound():
    sample_rate = 22050
    duration = 0.2
    import array
    import math
    n_samples = int(sample_rate * duration)
    buf = array.array('h', [0] * n_samples)
    for i in range(n_samples):
        t = i / sample_rate
        freq = 400 + (t * 800)
        buf[i] = int(5000 * math.sin(2 * math.pi * freq * t) * (1 - t / duration))
    sound = pygame.mixer.Sound(buffer=buf)
    sound.set_volume(0.4)
    return sound

def create_heal_sound():
    sample_rate = 22050
    duration = 0.25
    import array
    import math
    n_samples = int(sample_rate * duration)
    buf = array.array('h', [0] * n_samples)
    for i in range(n_samples):
        t = i / sample_rate
        freq = 600 + (t * 400)
        buf[i] = int(3000 * math.sin(2 * math.pi * freq * t) * math.sin(math.pi * t / duration))
    sound = pygame.mixer.Sound(buffer=buf)
    sound.set_volume(0.4)
    return sound

SHOOT_SOUND = create_shoot_sound()
DAMAGE_SOUND = create_damage_sound()
KILL_SOUND = create_kill_sound()
HEAL_SOUND = create_heal_sound()

def create_background_music():
    import array
    import math
    sample_rate = 22050
    duration = 8.0
    n_samples = int(sample_rate * duration)
    buf = array.array('h', [0] * n_samples)
    
    notes = [130.81, 146.83, 164.81, 174.61, 196.00, 220.00, 246.94, 261.63]
    melody = [0, 2, 4, 5, 4, 2, 3, 1, 0, 4, 5, 7, 5, 4, 2, 0]
    note_duration = duration / len(melody)
    
    for i in range(n_samples):
        t = i / sample_rate
        note_idx = int(t / note_duration) % len(melody)
        freq = notes[melody[note_idx]]
        
        bass_freq = freq / 2
        val = int(1500 * math.sin(2 * math.pi * freq * t))
        val += int(1000 * math.sin(2 * math.pi * bass_freq * t))
        val += int(500 * math.sin(2 * math.pi * freq * 1.5 * t))
        
        envelope = min(1.0, (t % note_duration) * 10) * max(0.3, 1 - (t % note_duration) / note_duration)
        buf[i] = int(val * envelope * 0.4)
    
    sound = pygame.mixer.Sound(buffer=buf)
    sound.set_volume(0.25)
    return sound

def create_boss_music():
    import array
    import math
    sample_rate = 22050
    duration = 3.0
    n_samples = int(sample_rate * duration)
    buf = array.array('h', [0] * n_samples)
    
    power_chords = [55.00, 61.74, 55.00, 73.42, 55.00, 82.41, 73.42, 55.00]
    note_duration = duration / len(power_chords)
    
    for i in range(n_samples):
        t = i / sample_rate
        note_idx = int(t / note_duration) % len(power_chords)
        root = power_chords[note_idx]
        fifth = root * 1.5
        octave = root * 2
        
        guitar = math.sin(2 * math.pi * root * t)
        guitar += 0.9 * math.sin(2 * math.pi * fifth * t)
        guitar += 0.7 * math.sin(2 * math.pi * octave * t)
        guitar += 0.5 * math.sin(2 * math.pi * root * 0.5 * t)
        
        distortion = math.tanh(guitar * 4) * 0.8
        
        for h in range(2, 10):
            distortion += 0.2 * math.sin(2 * math.pi * root * h * t + math.sin(t * 5)) / h
        
        beat_pos = (t * 6) % 1
        kick = 0
        if beat_pos < 0.08:
            kick = math.sin(2 * math.pi * 50 * beat_pos) * (1 - beat_pos * 12) * 1.0
        snare = 0
        if int(t * 6) % 2 == 1 and beat_pos < 0.04:
            snare = (hash(int(t * 10000)) % 1000 / 500 - 1) * 0.6
        double_kick = 0
        if int(t * 12) % 4 == 3 and (t * 12) % 1 < 0.1:
            double_kick = math.sin(2 * math.pi * 55 * ((t * 12) % 1)) * 0.5
        
        envelope = min(1.0, (t % note_duration) * 30) * max(0.7, 1 - (t % note_duration) / note_duration * 0.4)
        val = int((distortion * 3000 + kick * 3500 + snare * 2500 + double_kick * 2000) * envelope)
        buf[i] = max(-32767, min(32767, val))
    
    sound = pygame.mixer.Sound(buffer=buf)
    sound.set_volume(0.35)
    return sound

BACKGROUND_MUSIC = create_background_music()
BOSS_MUSIC = create_boss_music()

def create_ice_cave_music():
    import array
    import math
    sample_rate = 22050
    duration = 4.0
    n_samples = int(sample_rate * duration)
    buf = array.array('h', [0] * n_samples)
    
    notes = [329.63, 369.99, 392.00, 440.00, 493.88, 523.25, 493.88, 440.00]
    note_duration = duration / len(notes)
    
    for i in range(n_samples):
        t = i / sample_rate
        note_idx = int(t / note_duration) % len(notes)
        freq = notes[note_idx]
        
        crystal = math.sin(2 * math.pi * freq * t) * 0.4
        crystal += math.sin(2 * math.pi * freq * 2 * t) * 0.2 * math.sin(t * 3)
        crystal += math.sin(2 * math.pi * freq * 0.5 * t + math.sin(t * 0.5)) * 0.3
        
        shimmer = math.sin(2 * math.pi * freq * 3 * t) * 0.1 * (1 + math.sin(t * 8))
        
        pad = 0
        for j in range(3):
            pad += math.sin(2 * math.pi * freq * (0.25 + j * 0.25) * t + j) * 0.15
        
        fade = min(1.0, (t % note_duration) * 8) * max(0.3, 1 - (t % note_duration) / note_duration * 0.6)
        val = int((crystal + shimmer + pad) * 5000 * fade)
        buf[i] = max(-32767, min(32767, val))
    
    sound = pygame.mixer.Sound(buffer=buf)
    sound.set_volume(0.25)
    return sound

def create_final_boss_music():
    import array
    import math
    sample_rate = 22050
    duration = 2.5
    n_samples = int(sample_rate * duration)
    buf = array.array('h', [0] * n_samples)
    
    chords = [110.00, 130.81, 146.83, 164.81, 130.81, 110.00, 98.00, 110.00]
    note_duration = duration / len(chords)
    
    for i in range(n_samples):
        t = i / sample_rate
        note_idx = int(t / note_duration) % len(chords)
        root = chords[note_idx]
        fifth = root * 1.5
        
        bass = math.sin(2 * math.pi * root * 0.5 * t) * 1.2
        distorted = math.tanh(math.sin(2 * math.pi * root * t) * 5) * 0.6
        distorted += math.tanh(math.sin(2 * math.pi * fifth * t) * 5) * 0.5
        
        for h in range(2, 12):
            distorted += 0.15 * math.sin(2 * math.pi * root * h * t + math.sin(t * 7)) / h
        
        beat_pos = (t * 8) % 1
        kick = 0
        if beat_pos < 0.06:
            kick = math.sin(2 * math.pi * 45 * beat_pos) * (1 - beat_pos * 16) * 1.2
        
        snare = 0
        if int(t * 8) % 2 == 1 and beat_pos < 0.03:
            snare = (hash(int(t * 10000)) % 1000 / 500 - 1) * 0.8
        
        synth = math.sin(2 * math.pi * root * 4 * t + math.sin(t * 15)) * 0.3
        
        envelope = min(1.0, (t % note_duration) * 40) * max(0.8, 1 - (t % note_duration) / note_duration * 0.3)
        val = int((bass * 2500 + distorted * 3500 + kick * 4000 + snare * 3000 + synth * 2000) * envelope)
        buf[i] = max(-32767, min(32767, val))
    
    sound = pygame.mixer.Sound(buffer=buf)
    sound.set_volume(0.4)
    return sound

ICE_CAVE_MUSIC = create_ice_cave_music()
FINAL_BOSS_MUSIC = create_final_boss_music()
current_music = None

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

# Location 2 - Ice Cave colors
ICE_WALL_COLOR = (70, 100, 130)
ICE_WALL_BORDER = (50, 80, 110)
ICE_FLOOR_COLOR = (200, 220, 240)

# Final boss colors
FINAL_BOSS_COLOR = (100, 0, 150)
FINAL_BOSS_OUTLINE = (50, 0, 100)
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
BOSS_HEALTH = 30
BOSS_PROJECTILE_SIZE = 16
BOSS_PROJECTILE_SPEED = 5
BOSS_SHOOT_INTERVAL = 90


def create_player_sprites():
    """Create pixel art character sprites with walking animation frames."""
    # 0 = transparent, 1 = tan/beige skin, 2 = dark blue eyes, 3 = white body
    # 4 = red weapon, 5 = brown accent, 6 = light blue boots
    
    # Frame 1 - left foot forward
    sprite_data_1 = [
        [0, 0, 5, 1, 1, 1, 5, 0, 0],
        [0, 1, 1, 5, 1, 5, 1, 1, 0],
        [5, 2, 2, 1, 1, 1, 2, 2, 5],
        [1, 2, 3, 1, 1, 1, 2, 3, 1],
        [5, 1, 1, 1, 2, 1, 1, 1, 5],
        [1, 3, 2, 2, 2, 2, 2, 1, 1],
        [3, 3, 2, 3, 3, 3, 2, 3, 3],
        [3, 3, 3, 2, 3, 2, 3, 3, 3],
        [0, 3, 3, 3, 3, 3, 3, 3, 0],
        [0, 3, 6, 0, 0, 0, 6, 3, 0],
        [3, 5, 3, 0, 0, 0, 3, 5, 3],
    ]
    
    # Frame 2 - right foot forward (swap feet positions)
    sprite_data_2 = [
        [0, 0, 5, 1, 1, 1, 5, 0, 0],
        [0, 1, 1, 5, 1, 5, 1, 1, 0],
        [5, 2, 2, 1, 1, 1, 2, 2, 5],
        [1, 2, 3, 1, 1, 1, 2, 3, 1],
        [5, 1, 1, 1, 2, 1, 1, 1, 5],
        [1, 3, 2, 2, 2, 2, 2, 1, 1],
        [3, 3, 2, 3, 3, 3, 2, 3, 3],
        [3, 3, 3, 2, 3, 2, 3, 3, 3],
        [0, 3, 3, 3, 3, 3, 3, 3, 0],
        [0, 3, 0, 6, 0, 6, 0, 3, 0],
        [3, 5, 0, 3, 0, 3, 0, 5, 3],
    ]
    
    tan_skin = (212, 184, 150)
    dark_blue_eyes = (26, 74, 110)
    white_body = (245, 245, 240)
    red_weapon = (200, 60, 60)
    brown_accent = (139, 105, 20)
    light_blue = (135, 180, 220)
    
    colors = {
        1: tan_skin,
        2: dark_blue_eyes,
        3: white_body,
        4: red_weapon,
        5: brown_accent,
        6: light_blue
    }
    
    sprites = []
    for sprite_data in [sprite_data_1, sprite_data_2]:
        width = len(sprite_data[0]) * PIXEL_SIZE
        height = len(sprite_data) * PIXEL_SIZE
        sprite = pygame.Surface((width, height), pygame.SRCALPHA)
        
        for y, row in enumerate(sprite_data):
            for x, pixel in enumerate(row):
                if pixel in colors:
                    pygame.draw.rect(
                        sprite, colors[pixel],
                        (x * PIXEL_SIZE, y * PIXEL_SIZE, PIXEL_SIZE, PIXEL_SIZE)
                    )
        
        sprites.append(sprite)
    
    return sprites


def create_player_sprite():
    """Create single player sprite (for compatibility)."""
    return create_player_sprites()[0]


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


def create_ice_enemy_sprite():
    """Create ice enemy sprite - same as player but blue instead of yellow."""
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
    
    ice_blue = (100, 180, 255)
    dark_ice = (50, 100, 150)
    
    width = len(sprite_data[0]) * PIXEL_SIZE
    height = len(sprite_data) * PIXEL_SIZE
    
    sprite = pygame.Surface((width, height), pygame.SRCALPHA)
    
    for y, row in enumerate(sprite_data):
        for x, pixel in enumerate(row):
            if pixel == 1:
                color = dark_ice
            elif pixel == 2:
                color = ice_blue
            else:
                continue
            
            pygame.draw.rect(
                sprite, color,
                (x * PIXEL_SIZE, y * PIXEL_SIZE, PIXEL_SIZE, PIXEL_SIZE)
            )
    
    return sprite


def find_path(start_tile, end_tile, tiles, variation_seed=0):
    """A* pathfinding algorithm to find path between two tiles.
    
    variation_seed: unique value per enemy to create path diversity
    """
    if start_tile == end_tile:
        return [end_tile]
    
    rows = len(tiles)
    cols = len(tiles[0])
    
    def heuristic(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])
    
    def tile_cost(pos):
        if variation_seed == 0:
            return 0
        x, y = pos
        return ((x * 7 + y * 13 + variation_seed) % 5) * 0.3
    
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
            tentative_g = g_score[current] + 1 + tile_cost(neighbor)
            
            if neighbor not in g_score or tentative_g < g_score[neighbor]:
                came_from[neighbor] = current
                g_score[neighbor] = tentative_g
                f_score[neighbor] = tentative_g + heuristic(neighbor, end_tile)
                
                if neighbor not in open_set_hash:
                    heapq.heappush(open_set, (f_score[neighbor], neighbor))
                    open_set_hash.add(neighbor)
    
    return []


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

    def would_collide_with_player(self, new_x, new_y, player):
        enemy_rect = pygame.Rect(new_x, new_y, self.width, self.height)
        return enemy_rect.colliderect(player.get_rect())

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
            if not self.would_collide_with_player(target_x, target_y, player):
                self.x = target_x
                self.y = target_y
            self.path.pop(0)
        else:
            dx = dx / distance
            dy = dy / distance
            
            new_x = self.x + dx * self.speed
            new_y = self.y + dy * self.speed
            
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

    def would_collide_with_player(self, new_x, new_y, player):
        enemy_rect = pygame.Rect(new_x, new_y, self.width, self.height)
        return enemy_rect.colliderect(player.get_rect())

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
            if not self.would_collide_with_player(target_x, target_y, player):
                self.x = target_x
                self.y = target_y
            self.path.pop(0)
        else:
            dx = dx / distance
            dy = dy / distance
            
            new_x = self.x + dx * self.speed
            new_y = self.y + dy * self.speed
            
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
            
            dx = player.x - self.x
            dy = player.y - self.y
            distance = (dx ** 2 + dy ** 2) ** 0.5
            
            if distance > 0:
                dx = dx / distance
                dy = dy / distance
                
                proj_x = self.x + self.width // 2 - 4
                proj_y = self.y + self.height // 2 - 4
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


# Final boss settings
FINAL_BOSS_PIXEL_SIZE = 12
FINAL_BOSS_HEALTH = 30
FINAL_BOSS_SPEED = 2.0


def create_final_boss_sprite():
    """Create final boss sprite - 4x bigger enemy with purple color."""
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
    
    width = len(sprite_data[0]) * FINAL_BOSS_PIXEL_SIZE
    height = len(sprite_data) * FINAL_BOSS_PIXEL_SIZE
    
    sprite = pygame.Surface((width, height), pygame.SRCALPHA)
    
    for y, row in enumerate(sprite_data):
        for x, pixel in enumerate(row):
            if pixel == 1:
                color = FINAL_BOSS_OUTLINE
            elif pixel == 2:
                color = FINAL_BOSS_COLOR
            else:
                continue
            
            pygame.draw.rect(
                sprite, color,
                (x * FINAL_BOSS_PIXEL_SIZE, y * FINAL_BOSS_PIXEL_SIZE, FINAL_BOSS_PIXEL_SIZE, FINAL_BOSS_PIXEL_SIZE)
            )
    
    return sprite


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

    def teleport(self, player, dungeon):
        import random
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

    def teleport(self, player, dungeon):
        import random
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

    def move_towards_player(self, player, dungeon):
        dx = player.x - self.x
        dy = player.y - self.y
        
        distance = (dx ** 2 + dy ** 2) ** 0.5
        if distance < 80:
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

    def should_spawn_enemy(self):
        self.spawn_timer += 1
        if self.spawn_timer >= self.spawn_interval:
            self.spawn_timer = 0
            return True
        return False
    
    def get_spawn_position(self, dungeon):
        import random
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
        self.size = 8
        self.active = True
        self.has_ricocheted = False
        self.ricochet_timer = 0
        self.ricochet_lifetime = 180
        self.hit_enemies = set()

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


class Player:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.sprites = create_player_sprites()
        self.sprite = self.sprites[0]
        self.width = self.sprite.get_width()
        self.height = self.sprite.get_height()
        self.speed = PLAYER_SPEED
        self.max_health = 4
        self.health = self.max_health
        self.last_direction = (1, 0)
        self.walk_frame = 0
        self.walk_timer = 0
        self.walk_speed = 8
        self.is_moving = False
        self.blink_timer = 0
        self.blink_duration = 10

    def would_collide_with_enemies(self, new_x, new_y, enemies, boss=None, final_boss=None):
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


class Dungeon:
    def __init__(self, level_data, level_num):
        self.level_num = level_num
        self.tiles = level_data['tiles']
        self.width = len(self.tiles[0])
        self.height = len(self.tiles)
        self.spawn_point = level_data['spawn']
        self.exit_point = level_data['exit']
        self.location = level_data.get('location', 1)
        
        # Set colors based on location
        if self.location == 2:
            self.wall_color = ICE_WALL_COLOR
            self.wall_border = ICE_WALL_BORDER
            self.floor_color = ICE_FLOOR_COLOR
        else:
            self.wall_color = WALL_COLOR
            self.wall_border = WALL_BORDER
            self.floor_color = LIGHT_GRAY

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
                    pygame.draw.rect(screen, self.wall_color, rect)
                    pygame.draw.rect(screen, self.wall_border, rect, 2)
                else:
                    pygame.draw.rect(screen, self.floor_color, rect)
        
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
        'enemy_spawn': (20, 10),
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
        'enemy_spawn': (21, 9),
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
        'enemy_spawn': (20, 9),
        'enemy_count': 6
    }
    levels.append(level3)
    
    # Level 4 - Boss Arena with cover
    boss_level = {
        'tiles': [
            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
            [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
            [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
            [1, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 1],
            [1, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 1],
            [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
            [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
            [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
            [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
            [1, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 1],
            [1, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 1],
            [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
            [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
        ],
        'spawn': (2, 7),
        'exit': None,
        'enemy_spawn': None,
        'enemy_count': 0,
        'is_boss_level': True,
        'checkpoint': True
    }
    levels.append(boss_level)
    
    # === LOCATION 2: Ice Caves (after boss checkpoint) ===
    
    # Level 5 - Ice Cave Entrance (Winding Path)
    level5 = {
        'tiles': [
            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
            [1, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 1],
            [1, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 0, 1],
            [1, 0, 1, 1, 1, 1, 1, 1, 1, 0, 1, 0, 1, 1, 1, 1, 1, 1, 1, 0, 1, 0, 1, 0, 1],
            [1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1, 0, 1],
            [1, 1, 1, 1, 1, 1, 1, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 1, 1, 1, 1, 1, 0, 1],
            [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
            [1, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 1],
            [1, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1],
            [1, 0, 1, 0, 1, 1, 1, 1, 1, 1, 1, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 1, 0, 1],
            [1, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1],
            [1, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 1, 1, 1, 1, 1, 1, 1, 0, 1],
            [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
        ],
        'spawn': (1, 1),
        'exit': (23, 12),
        'enemy_count': 3,
        'location': 2
    }
    levels.append(level5)
    
    # Level 6 - Frozen Maze (Complex Corridors)
    level6 = {
        'tiles': [
            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
            [1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1],
            [1, 0, 1, 1, 1, 0, 1, 0, 1, 1, 1, 1, 0, 1, 1, 1, 1, 0, 1, 0, 1, 1, 1, 0, 1],
            [1, 0, 1, 0, 0, 0, 1, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 0, 0, 0, 1, 0, 1],
            [1, 0, 1, 0, 1, 1, 1, 0, 1, 0, 1, 1, 1, 1, 1, 0, 1, 0, 1, 1, 1, 0, 1, 0, 1],
            [1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1],
            [1, 1, 1, 1, 1, 1, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 1, 1, 1, 1, 1, 1, 0, 1],
            [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
            [1, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 1, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 1],
            [1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1],
            [1, 1, 1, 1, 1, 0, 1, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 1, 0, 1, 1, 1, 1, 1],
            [1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1],
            [1, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 1],
            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
        ],
        'spawn': (1, 1),
        'exit': (23, 11),
        'enemy_count': 4,
        'location': 2
    }
    levels.append(level6)
    
    # Level 7 - Crystal Labyrinth (Dead Ends)
    level7 = {
        'tiles': [
            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
            [1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1],
            [1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 1, 1, 1, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1],
            [1, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 1],
            [1, 0, 1, 1, 1, 1, 1, 1, 1, 0, 1, 0, 1, 0, 1, 0, 1, 1, 1, 1, 1, 1, 1, 0, 1],
            [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
            [1, 1, 1, 0, 1, 1, 1, 1, 1, 1, 1, 0, 1, 0, 1, 1, 1, 1, 1, 1, 1, 0, 1, 1, 1],
            [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
            [1, 0, 1, 1, 1, 1, 1, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 1, 1, 1, 1, 1, 0, 1],
            [1, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1],
            [1, 0, 1, 0, 1, 1, 1, 1, 1, 0, 1, 0, 1, 0, 1, 0, 1, 1, 1, 1, 1, 0, 1, 0, 1],
            [1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1],
            [1, 1, 1, 0, 1, 0, 1, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 1, 0, 1, 0, 1, 0, 1],
            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
        ],
        'spawn': (1, 1),
        'exit': (23, 11),
        'enemy_count': 5,
        'location': 2
    }
    levels.append(level7)
    
    # Level 8 - Icy Nightmare (Ultimate Maze)
    level8 = {
        'tiles': [
            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
            [1, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1],
            [1, 0, 1, 0, 1, 0, 1, 1, 1, 0, 1, 0, 1, 0, 1, 0, 1, 1, 1, 0, 1, 0, 1, 0, 1],
            [1, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1, 0, 1],
            [1, 0, 1, 1, 1, 1, 1, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 1, 1, 1, 1, 1, 0, 1],
            [1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1],
            [1, 1, 1, 1, 1, 0, 1, 1, 1, 0, 1, 1, 0, 1, 1, 0, 1, 1, 1, 0, 1, 1, 1, 1, 1],
            [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
            [1, 0, 1, 1, 1, 1, 1, 1, 1, 0, 1, 0, 1, 0, 1, 0, 1, 1, 1, 1, 1, 1, 1, 0, 1],
            [1, 0, 1, 0, 0, 0, 0, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 0, 0, 0, 0, 1, 0, 1],
            [1, 0, 1, 0, 1, 1, 1, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 1, 1, 1, 0, 1, 0, 1],
            [1, 0, 0, 0, 1, 0, 0, 0, 1, 1, 1, 0, 1, 0, 1, 1, 1, 0, 0, 0, 1, 0, 0, 0, 1],
            [1, 1, 1, 0, 1, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 0, 1, 0, 1],
            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
        ],
        'spawn': (1, 1),
        'exit': (23, 12),
        'enemy_count': 6,
        'location': 2
    }
    levels.append(level8)
    
    # Level 9 - Final Boss Arena
    final_boss = {
        'tiles': [
            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
            [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
            [1, 0, 0, 0, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 0, 0, 0, 0, 1],
            [1, 0, 0, 0, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 0, 0, 0, 0, 1],
            [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
            [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
            [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
            [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
            [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
            [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
            [1, 0, 0, 0, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 0, 0, 0, 0, 1],
            [1, 0, 0, 0, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 0, 0, 0, 0, 1],
            [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
        ],
        'spawn': (2, 7),
        'exit': None,
        'enemy_count': 0,
        'is_boss_level': True,
        'is_final_boss': True,
        'location': 2
    }
    levels.append(final_boss)
    
    return levels


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
        import random
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


class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Morzhaka Quest")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)
        self.title_font = pygame.font.Font(None, 72)
        self.menu_font = pygame.font.Font(None, 48)
        
        self.in_menu = True
        self.menu_selection = 0
        self.init_menu_background()
        
        self.levels = create_levels()
        self.current_level = 0
        self.checkpoint_level = 0
        self.ice_bullet_unlocked = False
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
        self.final_boss = None
        self.boss_projectiles = []
        self.enemy_projectiles = []
        self.is_boss_level = False
        self.is_final_boss_level = False
        
        self.health_kits = []
        self.health_kit_timer = 0
        self.health_kit_interval = 900
        
        self.game_won = False
        self.game_over = False
        self.running = True
        self.current_music = None

    def init_menu_background(self):
        import random
        self.menu_enemies = []
        
        for _ in range(3):
            x = random.randint(100, SCREEN_WIDTH - 200)
            y = random.randint(200, SCREEN_HEIGHT - 150)
            self.menu_enemies.append(MenuEnemy(x, y, create_enemy_sprite(), 1.5))
        
        for _ in range(2):
            x = random.randint(100, SCREEN_WIDTH - 200)
            y = random.randint(200, SCREEN_HEIGHT - 150)
            self.menu_enemies.append(MenuEnemy(x, y, create_ice_enemy_sprite(), 1.2))
        
        boss_x = SCREEN_WIDTH // 2 - 40
        boss_y = SCREEN_HEIGHT // 2 + 50
        self.menu_boss = MenuEnemy(boss_x, boss_y, create_boss_sprite(), 0.8)

    def start_game(self):
        self.in_menu = False
        self.play_music(BACKGROUND_MUSIC)

    def play_music(self, music):
        if self.current_music:
            self.current_music.stop()
        self.current_music = music
        self.current_music.play(-1)

    def spawn_enemies(self):
        self.enemies = []
        self.boss = None
        self.final_boss = None
        self.boss_projectiles = []
        self.enemy_projectiles = []
        level_data = self.levels[self.current_level]
        self.current_location = level_data.get('location', 1)
        
        self.is_boss_level = level_data.get('is_boss_level', False)
        self.is_final_boss_level = level_data.get('is_final_boss', False)
        
        if self.is_final_boss_level:
            boss_x = 20 * TILE_SIZE
            boss_y = 6 * TILE_SIZE
            self.final_boss = FinalBoss(boss_x, boss_y)
            return
        
        if self.is_boss_level:
            boss_x = 20 * TILE_SIZE
            boss_y = 6 * TILE_SIZE
            self.boss = Boss(boss_x, boss_y)
            return
        
        enemy_count = level_data.get('enemy_count', 0)
        exit_pos = level_data.get('exit')
        if not exit_pos:
            return
        tiles = level_data['tiles']
        
        offsets = [
            (0, 0), (-1, 0), (1, 0), (0, -1), (0, 1),
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
                    if self.current_location == 2:
                        self.enemies.append(IceEnemy(enemy_x, enemy_y))
                    else:
                        self.enemies.append(Enemy(enemy_x, enemy_y))
                    spawned += 1

    def spawn_one_enemy(self):
        if self.is_boss_level or self.is_final_boss_level:
            return
        level_data = self.levels[self.current_level]
        exit_pos = level_data.get('exit')
        if exit_pos is None:
            return
        tiles = level_data['tiles']
        
        offsets = [
            (0, 0), (-1, 0), (1, 0), (0, -1), (0, 1),
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
                    if self.current_location == 2:
                        self.enemies.append(IceEnemy(enemy_x, enemy_y))
                    else:
                        self.enemies.append(Enemy(enemy_x, enemy_y))
                    return

    def spawn_health_kit(self):
        import random
        level_data = self.levels[self.current_level]
        tiles = level_data['tiles']
        
        valid_positions = []
        for y in range(len(tiles)):
            for x in range(len(tiles[0])):
                if tiles[y][x] == 0:
                    valid_positions.append((x, y))
        
        if valid_positions:
            pos = random.choice(valid_positions)
            kit_x = pos[0] * TILE_SIZE + (TILE_SIZE - 20) // 2
            kit_y = pos[1] * TILE_SIZE + (TILE_SIZE - 20) // 2
            self.health_kits.append(HealthKit(kit_x, kit_y))

    def next_level(self):
        # Save checkpoint if we just completed a boss level
        prev_level_data = self.levels[self.current_level]
        if prev_level_data.get('checkpoint', False):
            self.checkpoint_level = self.current_level + 1
        
        self.current_level += 1
        
        if self.current_level >= len(self.levels):
            self.game_won = True
            if self.current_music:
                self.current_music.stop()
            return
        
        self.dungeon = Dungeon(self.levels[self.current_level], self.current_level + 1)
        spawn = self.dungeon.spawn_point
        self.player.x = spawn[0] * TILE_SIZE + 4
        self.player.y = spawn[1] * TILE_SIZE + 4
        self.spawn_enemies()
        self.projectiles = []
        self.enemy_projectiles = []
        self.health_kits = []
        self.health_kit_timer = 0
        self.damage_cooldown = 0
        self.shoot_cooldown = 0
        self.enemy_spawn_timer = 0
        
        # Play appropriate music based on level type and location
        level_data = self.levels[self.current_level]
        location = level_data.get('location', 1)
        
        if level_data.get('is_final_boss', False):
            self.play_music(FINAL_BOSS_MUSIC)
        elif level_data.get('is_boss_level', False):
            self.play_music(BOSS_MUSIC)
        elif location == 2:
            self.play_music(ICE_CAVE_MUSIC)
        else:
            self.play_music(BACKGROUND_MUSIC)

    def handle_input(self):
        keys = pygame.key.get_pressed()
        
        dx, dy = 0, 0
        
        if keys[pygame.K_w] or keys[pygame.K_UP]:
            dy = -1
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:
            dy = 1
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            dx = -1
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            dx = 1
        
        if dx != 0 or dy != 0:
            self.player.move(dx, dy, self.dungeon, self.enemies, self.boss, self.final_boss)
        
        if keys[pygame.K_SPACE] and self.shoot_cooldown <= 0:
            if self.ice_bullet_unlocked:
                proj_x = self.player.x + self.player.width // 2 - 4
                proj_y = self.player.y + self.player.height // 2 - 4
                self.projectiles.append(IceProjectile(proj_x, proj_y, self.player.last_direction))
            else:
                self.projectiles.append(self.player.shoot())
            self.shoot_cooldown = 15
            SHOOT_SOUND.play()

    def update(self):
        if self.game_won or self.game_over:
            if self.current_music:
                self.current_music.stop()
                self.current_music = None
            return
        
        self.player.update()
        
        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= 1
        
        if not self.is_boss_level:
            self.enemy_spawn_timer += 1
            if self.enemy_spawn_timer >= self.enemy_spawn_interval:
                self.enemy_spawn_timer = 0
                self.spawn_one_enemy()
        
        self.health_kit_timer += 1
        if self.health_kit_timer >= self.health_kit_interval:
            self.health_kit_timer = 0
            self.spawn_health_kit()
        
        for kit in self.health_kits:
            if kit.collides_with_player(self.player):
                if self.player.health < self.player.max_health:
                    self.player.heal(1)
                    HEAL_SOUND.play()
                kit.active = False
        self.health_kits = [k for k in self.health_kits if k.active]
        
        for projectile in self.projectiles:
            projectile.update(self.dungeon)
        
        for projectile in self.projectiles:
            if not projectile.active:
                continue
            for enemy in self.enemies[:]:
                if projectile.collides_with_enemy(enemy):
                    if not isinstance(projectile, IceProjectile):
                        projectile.active = False
                    
                    if hasattr(enemy, 'take_damage'):
                        if enemy.take_damage(1):
                            self.enemies.remove(enemy)
                            KILL_SOUND.play()
                        else:
                            DAMAGE_SOUND.play()
                    else:
                        self.enemies.remove(enemy)
                        KILL_SOUND.play()
                    
                    if not isinstance(projectile, IceProjectile):
                        break
        
        if self.boss:
            for projectile in self.projectiles:
                if not projectile.active:
                    continue
                if projectile.get_rect().colliderect(self.boss.get_rect()):
                    if not isinstance(projectile, IceProjectile):
                        projectile.active = False
                    if self.boss.take_damage(1):
                        self.boss = None
                        self.ice_bullet_unlocked = True
                        self.next_level()
                        KILL_SOUND.play()
                    break
        
        if self.final_boss:
            for projectile in self.projectiles:
                if not projectile.active:
                    continue
                if projectile.get_rect().colliderect(self.final_boss.get_rect()):
                    if not isinstance(projectile, IceProjectile):
                        projectile.active = False
                    if self.final_boss.take_damage(1):
                        self.final_boss = None
                        self.game_won = True
                        KILL_SOUND.play()
                        if self.current_music:
                            self.current_music.stop()
                    break
        
        self.projectiles = [p for p in self.projectiles if p.active]
        
        if self.boss:
            self.boss.move_towards_player(self.player, self.dungeon)
            self.boss.teleport(self.player, self.dungeon)
            self.boss.update_blink()
            boss_proj = self.boss.shoot_at_player(self.player)
            if boss_proj:
                self.boss_projectiles.append(boss_proj)
                SHOOT_SOUND.play()
        
        if self.final_boss:
            self.final_boss.move_towards_player(self.player, self.dungeon)
            self.final_boss.teleport(self.player, self.dungeon)
            self.final_boss.update_blink()
            if self.final_boss.should_spawn_enemy():
                spawn_pos = self.final_boss.get_spawn_position(self.dungeon)
                if spawn_pos:
                    self.enemies.append(IceEnemy(spawn_pos[0], spawn_pos[1]))
        
        for proj in self.boss_projectiles:
            proj.update(self.dungeon)
        
        self.boss_projectiles = [p for p in self.boss_projectiles if p.active]
        
        for enemy in self.enemies:
            enemy.move_towards_player(self.player, self.dungeon)
            enemy.update_blink()
            if isinstance(enemy, IceEnemy):
                proj = enemy.shoot_at_player(self.player)
                if proj:
                    self.enemy_projectiles.append(proj)
                    SHOOT_SOUND.play()
        
        for proj in self.enemy_projectiles:
            proj.update(self.dungeon)
        
        self.enemy_projectiles = [p for p in self.enemy_projectiles if p.active]
        
        if self.damage_cooldown > 0:
            self.damage_cooldown -= 1
        else:
            for enemy in self.enemies:
                if enemy.is_touching_player(self.player):
                    if self.player.take_damage():
                        self.game_over = True
                    DAMAGE_SOUND.play()
                    self.damage_cooldown = 60
                    break
            
            if self.boss and self.boss.is_touching_player(self.player):
                if self.player.take_damage():
                    self.game_over = True
                DAMAGE_SOUND.play()
                self.damage_cooldown = 60
            
            if self.final_boss and self.final_boss.is_touching_player(self.player):
                if self.player.take_damage():
                    self.game_over = True
                DAMAGE_SOUND.play()
                self.damage_cooldown = 60
            
            for proj in self.boss_projectiles:
                if proj.collides_with_player(self.player):
                    proj.active = False
                    if self.player.take_damage():
                        self.game_over = True
                    DAMAGE_SOUND.play()
                    self.damage_cooldown = 60
                    break
            
            for proj in self.enemy_projectiles:
                if proj.collides_with_player(self.player):
                    proj.active = False
                    if self.player.take_damage():
                        self.game_over = True
                    DAMAGE_SOUND.play()
                    self.damage_cooldown = 60
                    break
        
        if not self.is_boss_level and self.dungeon.check_exit(self.player):
            self.next_level()

    def draw(self):
        self.screen.fill(BLACK)
        
        if self.game_won:
            win_text = self.font.render("Congratulations! You completed Morzhaka Quest!", True, GREEN)
            restart_text = self.small_font.render("Press R to restart or ESC to quit", True, WHITE)
            self.screen.blit(win_text, (SCREEN_WIDTH // 2 - win_text.get_width() // 2, SCREEN_HEIGHT // 2 - 20))
            self.screen.blit(restart_text, (SCREEN_WIDTH // 2 - restart_text.get_width() // 2, SCREEN_HEIGHT // 2 + 20))
        elif self.game_over:
            over_text = self.font.render("GAME OVER", True, RED)
            if self.checkpoint_level > 0:
                checkpoint_text = self.small_font.render(f"Checkpoint: Level {self.checkpoint_level + 1}", True, YELLOW)
                restart_text = self.small_font.render("Press R to restart from checkpoint or ESC to quit", True, WHITE)
            else:
                checkpoint_text = None
                restart_text = self.small_font.render("Press R to restart or ESC to quit", True, WHITE)
            self.screen.blit(over_text, (SCREEN_WIDTH // 2 - over_text.get_width() // 2, SCREEN_HEIGHT // 2 - 30))
            if checkpoint_text:
                self.screen.blit(checkpoint_text, (SCREEN_WIDTH // 2 - checkpoint_text.get_width() // 2, SCREEN_HEIGHT // 2 + 10))
                self.screen.blit(restart_text, (SCREEN_WIDTH // 2 - restart_text.get_width() // 2, SCREEN_HEIGHT // 2 + 40))
            else:
                self.screen.blit(restart_text, (SCREEN_WIDTH // 2 - restart_text.get_width() // 2, SCREEN_HEIGHT // 2 + 20))
        else:
            self.dungeon.draw(self.screen)
            self.player.draw(self.screen)
            
            for enemy in self.enemies:
                enemy.draw(self.screen)
            
            if self.boss:
                self.boss.draw(self.screen)
            
            if self.final_boss:
                self.final_boss.draw(self.screen)
            
            for projectile in self.projectiles:
                projectile.draw(self.screen)
            
            for proj in self.boss_projectiles:
                proj.draw(self.screen)
            
            for proj in self.enemy_projectiles:
                proj.draw(self.screen)
            
            for kit in self.health_kits:
                kit.draw(self.screen)
            
            if self.is_final_boss_level:
                level_text = self.font.render("FINAL BOSS!", True, FINAL_BOSS_COLOR)
            elif self.is_boss_level:
                level_text = self.font.render("BOSS FIGHT!", True, RED)
            else:
                location = self.levels[self.current_level].get('location', 1)
                if location == 2:
                    level_text = self.font.render(f"Ice Caves - Level: {self.current_level + 1}/{len(self.levels)}", True, ICE_FLOOR_COLOR)
                else:
                    level_text = self.font.render(f"Level: {self.current_level + 1}/{len(self.levels)}", True, WHITE)
            self.screen.blit(level_text, (10, 10))
            
            health_label = self.small_font.render("HP:", True, WHITE)
            self.screen.blit(health_label, (SCREEN_WIDTH - 140, 10))
            self.player.draw_health(self.screen, SCREEN_WIDTH - 110, 8)
            
            if self.ice_bullet_unlocked:
                bullet_text = self.small_font.render("ICE BULLET", True, (0, 255, 255))
                self.screen.blit(bullet_text, (SCREEN_WIDTH - 110, 35))
            
            if self.is_final_boss_level:
                hint_text = self.small_font.render("Defeat the Final Boss to escape!", True, FINAL_BOSS_COLOR)
            elif self.is_boss_level:
                hint_text = self.small_font.render("Defeat the boss to reach the Ice Caves!", True, RED)
            else:
                hint_text = self.small_font.render("Find the yellow exit! Avoid red enemies!", True, YELLOW)
            self.screen.blit(hint_text, (10, 45))
            
            controls_text = self.small_font.render("WASD/Arrows to move, SPACE to shoot", True, WHITE)
            self.screen.blit(controls_text, (10, SCREEN_HEIGHT - 30))
        
        pygame.display.flip()

    def draw_menu(self):
        self.screen.fill((20, 20, 30))
        
        for enemy in self.menu_enemies:
            enemy.update()
            enemy.draw(self.screen)
        
        self.menu_boss.update()
        self.menu_boss.draw(self.screen)
        
        title_text = self.title_font.render("MORZHAKA QUEST", True, YELLOW)
        title_shadow = self.title_font.render("MORZHAKA QUEST", True, (80, 60, 0))
        self.screen.blit(title_shadow, (SCREEN_WIDTH // 2 - title_text.get_width() // 2 + 3, 53))
        self.screen.blit(title_text, (SCREEN_WIDTH // 2 - title_text.get_width() // 2, 50))
        
        start_color = YELLOW if self.menu_selection == 0 else WHITE
        quit_color = YELLOW if self.menu_selection == 1 else WHITE
        
        start_text = self.menu_font.render("START GAME", True, start_color)
        quit_text = self.menu_font.render("QUIT GAME", True, quit_color)
        
        if self.menu_selection == 0:
            arrow_text = self.menu_font.render(">", True, YELLOW)
            self.screen.blit(arrow_text, (SCREEN_WIDTH // 2 - start_text.get_width() // 2 - 40, 150))
        else:
            arrow_text = self.menu_font.render(">", True, YELLOW)
            self.screen.blit(arrow_text, (SCREEN_WIDTH // 2 - quit_text.get_width() // 2 - 40, 210))
        
        self.screen.blit(start_text, (SCREEN_WIDTH // 2 - start_text.get_width() // 2, 150))
        self.screen.blit(quit_text, (SCREEN_WIDTH // 2 - quit_text.get_width() // 2, 210))
        
        controls_text = self.small_font.render("Use UP/DOWN to select, ENTER to confirm", True, GRAY)
        self.screen.blit(controls_text, (SCREEN_WIDTH // 2 - controls_text.get_width() // 2, SCREEN_HEIGHT - 50))

    def run(self):
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.KEYDOWN:
                    if self.in_menu:
                        if event.key == pygame.K_UP or event.key == pygame.K_w:
                            self.menu_selection = (self.menu_selection - 1) % 2
                        elif event.key == pygame.K_DOWN or event.key == pygame.K_s:
                            self.menu_selection = (self.menu_selection + 1) % 2
                        elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                            if self.menu_selection == 0:
                                self.start_game()
                            else:
                                self.running = False
                        elif event.key == pygame.K_ESCAPE:
                            self.running = False
                    else:
                        if event.key == pygame.K_ESCAPE:
                            self.running = False
                        elif event.key == pygame.K_r and (self.game_won or self.game_over):
                            if self.game_won:
                                self.current_level = 0
                                self.checkpoint_level = 0
                                self.ice_bullet_unlocked = False
                            else:
                                self.current_level = self.checkpoint_level
                            self.dungeon = Dungeon(self.levels[self.current_level], self.current_level + 1)
                            spawn = self.dungeon.spawn_point
                            self.player.x = spawn[0] * TILE_SIZE + 4
                            self.player.y = spawn[1] * TILE_SIZE + 4
                            self.player.health = self.player.max_health
                            self.player.last_direction = (1, 0)
                            self.spawn_enemies()
                            self.projectiles = []
                            self.enemy_projectiles = []
                            self.health_kits = []
                            self.health_kit_timer = 0
                            self.damage_cooldown = 0
                            self.shoot_cooldown = 0
                            self.enemy_spawn_timer = 0
                            self.game_won = False
                            self.game_over = False
                            level_data = self.levels[self.current_level]
                            location = level_data.get('location', 1)
                            if location == 2:
                                self.play_music(ICE_CAVE_MUSIC)
                            else:
                                self.play_music(BACKGROUND_MUSIC)
            
            if self.in_menu:
                self.draw_menu()
                pygame.display.flip()
            else:
                self.handle_input()
                self.update()
                self.draw()
            
            self.clock.tick(60)
        
        pygame.quit()
        sys.exit()


if __name__ == "__main__":
    game = Game()
    game.run()
