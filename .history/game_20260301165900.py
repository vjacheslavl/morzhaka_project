import pygame
import sys

# Initialize Pygame
pygame.init()

# Screen settings
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
TILE_SIZE = 32

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
GRAY = (100, 100, 100)
DARK_GRAY = (50, 50, 50)
BROWN = (139, 69, 19)
YELLOW = (255, 215, 0)
BLUE = (65, 105, 225)

# Player settings
PIXEL_SIZE = 3
PLAYER_SPEED = 3


def create_player_sprite():
    """Create pixel art character sprite based on hand-drawn design."""
    # 0 = transparent, 1 = blue (outline), 2 = yellow (fill)
    sprite_data = [
        [1, 1, 1, 1, 1, 1, 1, 1, 1],
        [1, 2, 2, 2, 2, 2, 2, 2, 1],
        [1, 2, 2, 2, 2, 2, 2, 2, 1],
        [1, 1, 1, 2, 2, 1, 1, 1, 1],
        [1, 2, 1, 2, 2, 1, 2, 2, 1],
        [1, 0, 1, 2, 2, 1, 1, 0, 1],
        [1, 1, 1, 2, 2, 1, 1, 1, 1],
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


class Player:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.sprite = create_player_sprite()
        self.width = self.sprite.get_width()
        self.height = self.sprite.get_height()
        self.speed = PLAYER_SPEED

    def move(self, dx, dy, dungeon):
        new_x = self.x + dx * self.speed
        new_y = self.y + dy * self.speed
        
        if not dungeon.is_wall(new_x, new_y, self.width, self.height):
            self.x = new_x
            self.y = new_y

    def draw(self, screen):
        screen.blit(self.sprite, (self.x, self.y))

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
        'exit': (22, 11)
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
        'exit': (23, 11)
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
        'exit': (23, 11)
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
        
        self.game_won = False
        self.running = True

    def next_level(self):
        self.current_level += 1
        
        if self.current_level >= len(self.levels):
            self.game_won = True
            return
        
        self.dungeon = Dungeon(self.levels[self.current_level], self.current_level + 1)
        spawn = self.dungeon.spawn_point
        self.player.x = spawn[0] * TILE_SIZE + 4
        self.player.y = spawn[1] * TILE_SIZE + 4

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
        if not self.game_won:
            if self.dungeon.check_exit(self.player):
                self.next_level()

    def draw(self):
        self.screen.fill(BLACK)
        
        if self.game_won:
            win_text = self.font.render("Congratulations! You escaped the dungeon!", True, GREEN)
            restart_text = self.small_font.render("Press R to restart or ESC to quit", True, WHITE)
            self.screen.blit(win_text, (SCREEN_WIDTH // 2 - win_text.get_width() // 2, SCREEN_HEIGHT // 2 - 20))
            self.screen.blit(restart_text, (SCREEN_WIDTH // 2 - restart_text.get_width() // 2, SCREEN_HEIGHT // 2 + 20))
        else:
            self.dungeon.draw(self.screen)
            self.player.draw(self.screen)
            
            level_text = self.font.render(f"Level: {self.current_level + 1}/{len(self.levels)}", True, WHITE)
            self.screen.blit(level_text, (10, 10))
            
            hint_text = self.small_font.render("Find the yellow exit!", True, YELLOW)
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
                    elif event.key == pygame.K_r and self.game_won:
                        self.current_level = 0
                        self.dungeon = Dungeon(self.levels[self.current_level], self.current_level + 1)
                        spawn = self.dungeon.spawn_point
                        self.player.x = spawn[0] * TILE_SIZE + 4
                        self.player.y = spawn[1] * TILE_SIZE + 4
                        self.game_won = False
            
            self.handle_input()
            self.update()
            self.draw()
            
            self.clock.tick(60)
        
        pygame.quit()
        sys.exit()


if __name__ == "__main__":
    game = Game()
    game.run()
