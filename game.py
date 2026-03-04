import pygame
import sys
import random

from constants import (
    SCREEN_WIDTH, SCREEN_HEIGHT, TILE_SIZE,
    BLACK, WHITE, GREEN, GRAY, YELLOW, RED, DARK_RED,
    ICE_FLOOR_COLOR, FINAL_BOSS_COLOR
)
from sounds import (
    SHOOT_SOUND, DAMAGE_SOUND, KILL_SOUND, HEAL_SOUND, VICTORY_SOUND,
    BACKGROUND_MUSIC, BOSS_MUSIC, ICE_CAVE_MUSIC, FINAL_BOSS_MUSIC, CASTLE_MUSIC
)
from sprites import create_player_sprites, create_player_sprite
from entities import Player, HealthKit, DeathParticle
from enemies import (
    Enemy, IceEnemy, CastleEnemyFast, CastleEnemyShooter,
    Boss, IceBoss, FinalBoss, ShadowBoss
)
from projectiles import Projectile, IceProjectile, ExplosiveProjectile
from dungeon import Dungeon
from levels import create_levels
from menu import MenuEnemy, init_menu_background

pygame.init()


class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Morzhaka Quest")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)
        self.title_font = pygame.font.Font(None, 72)
        self.menu_font = pygame.font.Font(None, 48)
        self.cutscene_font = pygame.font.Font(None, 32)
        
        self.in_menu = True
        self.in_settings = False
        self.in_cutscene = False
        self.cutscene_page = 0
        self.cutscene_timer = 0
        self.cutscene_fade = 0
        self.cutscene_text_progress = 0
        self.menu_selection = 0
        self.settings_selection = 0
        self.master_volume = 0.5
        self.is_fullscreen = False
        self.init_menu_background()
        self.init_cutscene()
        self.set_volume(self.master_volume)
        
        self.levels = create_levels()
        self.current_level = 0
        self.checkpoint_level = 0
        self.ice_bullet_unlocked = False
        self.explosive_bullet_unlocked = False
        self.selected_bullet = 1
        self.death_particles = []
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
        self.shadow_boss = None
        self.boss_projectiles = []
        self.enemy_projectiles = []
        self.is_boss_level = False
        self.is_shadow_boss_level = False
        self.is_final_boss_level = False
        
        self.health_kits = []
        self.health_kit_timer = 0
        self.health_kit_interval = 900
        
        self.game_won = False
        self.game_over = False
        self.running = True
        self.current_music = None

    def init_menu_background(self):
        self.menu_enemies, self.menu_boss, self.menu_player, self.menu_final_boss = init_menu_background()

    def init_cutscene(self):
        self.cutscene_pages = [
            {
                "title": "A PEACEFUL DAY",
                "text": [
                    "You are a young warrior",
                    "training under the legendary Master Morzhaka.",
                    "",
                    "For years, he taught you the ancient arts",
                    "of combat and the way of the warrior."
                ],
                "bg_color": (15, 20, 15)
            },
            {
                "title": "THE DARK LORD STRIKES",
                "text": [
                    "But one fateful night, the evil Dark Lord",
                    "attacked your village with his army!",
                    "",
                    "He kidnapped Master Morzhaka and dragged him",
                    "deep into his cursed dungeon fortress."
                ],
                "bg_color": (25, 10, 10)
            },
            {
                "title": "YOUR MISSION",
                "text": [
                    "You must fight through the dungeon,",
                    "cross the frozen Ice Caves,",
                    "and reach Shadow Byako Castle!",
                    "",
                    "The Dark Lord holds Master Morzhaka there...",
                    "Only you can stop him and save your Master!"
                ],
                "bg_color": (10, 10, 25)
            },
            {
                "title": "CONTROLS",
                "text": [
                    "WASD or Arrow Keys - Move",
                    "SPACE - Shoot",
                    "1 / 2 - Switch bullets",
                    "",
                    "Find yellow exits to progress.",
                    "Save Master Morzhaka!"
                ],
                "bg_color": (20, 15, 20)
            }
        ]
        self.cutscene_player_x = -50
        self.cutscene_player_sprite = create_player_sprites()

    def start_cutscene(self):
        self.in_menu = False
        self.in_cutscene = True
        self.cutscene_page = 0
        self.cutscene_timer = 0
        self.cutscene_fade = 0
        self.cutscene_text_progress = 0
        self.cutscene_player_x = -50

    def advance_cutscene(self):
        self.cutscene_page += 1
        self.cutscene_timer = 0
        self.cutscene_text_progress = 0
        self.cutscene_fade = 0
        self.cutscene_player_x = -50
        
        if self.cutscene_page >= len(self.cutscene_pages):
            self.in_cutscene = False
            self.start_game()

    def update_cutscene(self):
        self.cutscene_timer += 1
        
        if self.cutscene_fade < 255:
            self.cutscene_fade = min(255, self.cutscene_fade + 5)
        
        page_data = self.cutscene_pages[self.cutscene_page]
        total_chars = sum(len(line) for line in page_data["text"])
        if self.cutscene_text_progress < total_chars:
            self.cutscene_text_progress += 0.5
        
        self.cutscene_player_x += 1.5
        if self.cutscene_player_x > SCREEN_WIDTH + 50:
            self.cutscene_player_x = -50

    def draw_cutscene(self):
        page_data = self.cutscene_pages[self.cutscene_page]
        self.screen.fill(page_data["bg_color"])
        
        alpha = self.cutscene_fade
        
        title_color = (min(255, 200 + int(alpha * 0.2)), min(255, 180 + int(alpha * 0.3)), 50)
        title_text = self.title_font.render(page_data["title"], True, title_color)
        title_rect = title_text.get_rect(center=(SCREEN_WIDTH // 2, 100))
        
        title_surface = pygame.Surface(title_text.get_size(), pygame.SRCALPHA)
        title_surface.blit(title_text, (0, 0))
        title_surface.set_alpha(alpha)
        self.screen.blit(title_surface, title_rect)
        
        y_offset = 200
        chars_shown = int(self.cutscene_text_progress)
        current_char = 0
        
        for line in page_data["text"]:
            if current_char >= chars_shown:
                break
            
            line_chars = min(len(line), chars_shown - current_char)
            display_line = line[:line_chars]
            
            text_surface = self.cutscene_font.render(display_line, True, (200, 200, 200))
            text_rect = text_surface.get_rect(center=(SCREEN_WIDTH // 2, y_offset))
            
            text_with_alpha = pygame.Surface(text_surface.get_size(), pygame.SRCALPHA)
            text_with_alpha.blit(text_surface, (0, 0))
            text_with_alpha.set_alpha(alpha)
            self.screen.blit(text_with_alpha, text_rect)
            
            current_char += len(line)
            y_offset += 35
        
        player_y = SCREEN_HEIGHT - 150
        frame = (self.cutscene_timer // 8) % 2
        player_sprite = self.cutscene_player_sprite[frame]
        self.screen.blit(player_sprite, (self.cutscene_player_x, player_y))
        
        progress_text = f"Page {self.cutscene_page + 1}/{len(self.cutscene_pages)}"
        progress_surface = self.small_font.render(progress_text, True, (100, 100, 100))
        self.screen.blit(progress_surface, (10, SCREEN_HEIGHT - 30))
        
        hint_text = "Press SPACE or ENTER to continue..."
        hint_surface = self.small_font.render(hint_text, True, (150, 150, 150))
        hint_rect = hint_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 50))
        self.screen.blit(hint_surface, hint_rect)
        
        skip_text = "Press ESC to skip"
        skip_surface = self.small_font.render(skip_text, True, (80, 80, 80))
        self.screen.blit(skip_surface, (SCREEN_WIDTH - skip_surface.get_width() - 10, SCREEN_HEIGHT - 30))

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
        self.shadow_boss = None
        self.boss_projectiles = []
        self.enemy_projectiles = []
        level_data = self.levels[self.current_level]
        self.current_location = level_data.get('location', 1)
        
        self.is_boss_level = level_data.get('is_boss_level', False)
        self.is_final_boss_level = level_data.get('is_final_boss', False)
        self.is_shadow_boss_level = level_data.get('is_shadow_boss', False)

        if self.is_final_boss_level:
            boss_x = 20 * TILE_SIZE
            boss_y = 6 * TILE_SIZE
            self.final_boss = FinalBoss(boss_x, boss_y)
            return

        if self.is_shadow_boss_level:
            boss_x = 20 * TILE_SIZE
            boss_y = 6 * TILE_SIZE
            self.shadow_boss = ShadowBoss(boss_x, boss_y)
            return

        if self.is_boss_level:
            boss_x = 20 * TILE_SIZE
            boss_y = 6 * TILE_SIZE
            if self.current_location == 2:
                self.boss = IceBoss(boss_x, boss_y)
            else:
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
                    if self.current_location == 3:
                        if random.random() < 0.5:
                            self.enemies.append(CastleEnemyFast(enemy_x, enemy_y))
                        else:
                            self.enemies.append(CastleEnemyShooter(enemy_x, enemy_y))
                    elif self.current_location == 2:
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
                    if self.current_location == 3:
                        if random.random() < 0.5:
                            self.enemies.append(CastleEnemyFast(enemy_x, enemy_y))
                        else:
                            self.enemies.append(CastleEnemyShooter(enemy_x, enemy_y))
                    elif self.current_location == 2:
                        self.enemies.append(IceEnemy(enemy_x, enemy_y))
                    else:
                        self.enemies.append(Enemy(enemy_x, enemy_y))
                    return

    def spawn_health_kit(self):
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

    def spawn_death_particles(self, enemy):
        center_x = enemy.x + enemy.width // 2
        center_y = enemy.y + enemy.height // 2
        
        colors = [
            (200, 50, 50), (220, 80, 80), (180, 30, 30),
            (150, 150, 150), (100, 100, 100), (80, 80, 80)
        ]
        
        for _ in range(12):
            color = random.choice(colors)
            self.death_particles.append(DeathParticle(center_x, center_y, color))

    def next_level(self):
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
        self.death_particles = []
        self.health_kits = []
        self.health_kit_timer = 0
        self.damage_cooldown = 0
        self.shoot_cooldown = 0
        self.enemy_spawn_timer = 0
        
        level_data = self.levels[self.current_level]
        location = level_data.get('location', 1)
        
        if level_data.get('is_final_boss', False):
            self.play_music(FINAL_BOSS_MUSIC)
        elif level_data.get('is_boss_level', False):
            self.play_music(BOSS_MUSIC)
        elif location == 3:
            self.play_music(CASTLE_MUSIC)
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
        
        if keys[pygame.K_1]:
            self.selected_bullet = 1
        if keys[pygame.K_2] and self.ice_bullet_unlocked:
            self.selected_bullet = 2
        if keys[pygame.K_3] and self.explosive_bullet_unlocked:
            self.selected_bullet = 3

        if keys[pygame.K_SPACE] and self.shoot_cooldown <= 0:
            proj_x = self.player.x + self.player.width // 2 - 4
            proj_y = self.player.y + self.player.height // 2 - 4
            if self.selected_bullet == 3 and self.explosive_bullet_unlocked:
                self.projectiles.append(ExplosiveProjectile(proj_x, proj_y, self.player.last_direction))
                self.shoot_cooldown = 18
            elif self.selected_bullet == 2 and self.ice_bullet_unlocked:
                self.projectiles.append(IceProjectile(proj_x, proj_y, self.player.last_direction))
                self.shoot_cooldown = 15
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
        
        self.dungeon.update()
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
            
            if isinstance(projectile, ExplosiveProjectile):
                for enemy in self.enemies[:]:
                    if projectile.damages_enemy(enemy):
                        if hasattr(enemy, 'take_damage'):
                            if enemy.take_damage(2):
                                self.spawn_death_particles(enemy)
                                self.enemies.remove(enemy)
                                KILL_SOUND.play()
                            else:
                                DAMAGE_SOUND.play()
                        else:
                            self.spawn_death_particles(enemy)
                            self.enemies.remove(enemy)
                            KILL_SOUND.play()
            else:
                for enemy in self.enemies[:]:
                    if projectile.collides_with_enemy(enemy):
                        if not isinstance(projectile, IceProjectile):
                            projectile.active = False
                        
                        if hasattr(enemy, 'take_damage'):
                            if enemy.take_damage(1):
                                self.spawn_death_particles(enemy)
                                self.enemies.remove(enemy)
                                KILL_SOUND.play()
                            else:
                                DAMAGE_SOUND.play()
                        else:
                            self.spawn_death_particles(enemy)
                            self.enemies.remove(enemy)
                            KILL_SOUND.play()
                        
                        if not isinstance(projectile, IceProjectile):
                            break
        
        if self.boss:
            for projectile in self.projectiles:
                if not projectile.active:
                    continue
                
                if isinstance(projectile, ExplosiveProjectile):
                    if not projectile.exploding:
                        if projectile.get_rect().colliderect(self.boss.get_rect()):
                            projectile.explode()
                            damage = 2
                            if self.boss.take_damage(damage):
                                self.boss = None
                                self.ice_bullet_unlocked = True
                                VICTORY_SOUND.play()
                                self.next_level()
                            break
                elif projectile.get_rect().colliderect(self.boss.get_rect()):
                    if not isinstance(projectile, IceProjectile):
                        projectile.active = False
                    if self.boss.take_damage(1):
                        self.boss = None
                        self.ice_bullet_unlocked = True
                        VICTORY_SOUND.play()
                        self.next_level()
                    break
        
        if self.final_boss:
            for projectile in self.projectiles:
                if not projectile.active:
                    continue
                
                if isinstance(projectile, ExplosiveProjectile):
                    if not projectile.exploding:
                        if projectile.get_rect().colliderect(self.final_boss.get_rect()):
                            projectile.explode()
                            damage = 2
                            if self.final_boss.take_damage(damage):
                                self.final_boss = None
                                self.explosive_bullet_unlocked = True
                                VICTORY_SOUND.play()
                                self.next_level()
                            break
                elif projectile.get_rect().colliderect(self.final_boss.get_rect()):
                    if not isinstance(projectile, IceProjectile):
                        projectile.active = False
                    if self.final_boss.take_damage(1):
                        self.final_boss = None
                        self.explosive_bullet_unlocked = True
                        VICTORY_SOUND.play()
                        self.next_level()
                    break

        if self.shadow_boss:
            for projectile in self.projectiles:
                if not projectile.active:
                    continue
                
                if isinstance(projectile, ExplosiveProjectile):
                    if not projectile.exploding:
                        if projectile.get_rect().colliderect(self.shadow_boss.get_rect()):
                            projectile.explode()
                            damage = 2
                            if self.shadow_boss.take_damage(damage):
                                self.shadow_boss = None
                                self.game_won = True
                                VICTORY_SOUND.play()
                                if self.current_music:
                                    self.current_music.stop()
                            break
                elif projectile.get_rect().colliderect(self.shadow_boss.get_rect()):
                    if not isinstance(projectile, IceProjectile):
                        projectile.active = False
                    if self.shadow_boss.take_damage(1):
                        self.shadow_boss = None
                        self.game_won = True
                        VICTORY_SOUND.play()
                        if self.current_music:
                            self.current_music.stop()
                    break

        self.projectiles = [p for p in self.projectiles if p.active]

        for particle in self.death_particles:
            particle.update()
        self.death_particles = [p for p in self.death_particles if p.active]

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

        if self.shadow_boss:
            self.shadow_boss.move_towards_player(self.player, self.dungeon)
            self.shadow_boss.teleport(self.player, self.dungeon)
            self.shadow_boss.update_blink()
            proj = self.shadow_boss.shoot_at_player(self.player)
            if proj:
                self.boss_projectiles.append(proj)
                SHOOT_SOUND.play()

        for proj in self.boss_projectiles:
            proj.update(self.dungeon)
        
        self.boss_projectiles = [p for p in self.boss_projectiles if p.active]
        
        for enemy in self.enemies:
            enemy.move_towards_player(self.player, self.dungeon)
            enemy.update_blink()
            if isinstance(enemy, (IceEnemy, CastleEnemyShooter)):
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

            if self.shadow_boss and self.shadow_boss.is_touching_player(self.player):
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
            
            if self.dungeon.check_laser_collision(self.player):
                if self.player.take_damage():
                    self.game_over = True
                DAMAGE_SOUND.play()
                self.damage_cooldown = 60
        
        if not self.is_boss_level and self.dungeon.check_exit(self.player):
            self.next_level()

    def draw(self):
        self.screen.fill(BLACK)
        
        if self.game_won:
            win_text = self.font.render("You defeated the Dark Lord and saved Master Morzhaka!", True, GREEN)
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

            if self.shadow_boss:
                self.shadow_boss.draw(self.screen)

            for projectile in self.projectiles:
                projectile.draw(self.screen)

            for particle in self.death_particles:
                particle.draw(self.screen)

            for proj in self.boss_projectiles:
                proj.draw(self.screen)
            
            for proj in self.enemy_projectiles:
                proj.draw(self.screen)
            
            for kit in self.health_kits:
                kit.draw(self.screen)
            
            if self.is_shadow_boss_level:
                level_text = self.font.render("THE DARK LORD!", True, (200, 30, 30))
            elif self.is_final_boss_level:
                level_text = self.font.render("GUARD!", True, FINAL_BOSS_COLOR)
            elif self.is_boss_level:
                level_text = self.font.render("BOSS FIGHT!", True, RED)
            else:
                location = self.levels[self.current_level].get('location', 1)
                if location == 3:
                    level_text = self.font.render(f"Shadow Byako Castle - Level: {self.current_level + 1}/{len(self.levels)}", True, (150, 150, 160))
                elif location == 2:
                    level_text = self.font.render(f"Ice Caves - Level: {self.current_level + 1}/{len(self.levels)}", True, ICE_FLOOR_COLOR)
                else:
                    level_text = self.font.render(f"Level: {self.current_level + 1}/{len(self.levels)}", True, WHITE)
            self.screen.blit(level_text, (10, 10))
            
            health_label = self.small_font.render("HP:", True, WHITE)
            self.screen.blit(health_label, (SCREEN_WIDTH - 185, 10))
            self.player.draw_health(self.screen, SCREEN_WIDTH - 155, 8)
            
            bullet1_color = YELLOW if self.selected_bullet == 1 else GRAY
            bullet1_text = self.small_font.render("[1] Normal", True, bullet1_color)
            self.screen.blit(bullet1_text, (SCREEN_WIDTH - 185, 35))
            
            if self.ice_bullet_unlocked:
                bullet2_color = (0, 255, 255) if self.selected_bullet == 2 else GRAY
                bullet2_text = self.small_font.render("[2] Ice", True, bullet2_color)
                self.screen.blit(bullet2_text, (SCREEN_WIDTH - 185, 55))

            if self.explosive_bullet_unlocked:
                bullet3_color = (150, 150, 155) if self.selected_bullet == 3 else GRAY
                bullet3_text = self.small_font.render("[3] Boom", True, bullet3_color)
                self.screen.blit(bullet3_text, (SCREEN_WIDTH - 185, 75))

            if self.is_shadow_boss_level:
                hint_text = self.small_font.render("Defeat the Dark Lord and save Master Morzhaka!", True, (200, 30, 30))
            elif self.is_final_boss_level:
                hint_text = self.small_font.render("Defeat the Guard to reach the Castle!", True, FINAL_BOSS_COLOR)
            elif self.is_boss_level:
                hint_text = self.small_font.render("Defeat this guardian to continue!", True, RED)
            elif self.current_location == 3:
                hint_text = self.small_font.render("The Dark Lord awaits in his throne room!", True, (150, 150, 160))
            else:
                hint_text = self.small_font.render("Find the exit! Your Master needs you!", True, YELLOW)
            self.screen.blit(hint_text, (10, 45))
            
            controls_text = self.small_font.render("WASD/Arrows: move | SPACE: shoot | 1/2/3: switch bullets", True, WHITE)
            self.screen.blit(controls_text, (10, SCREEN_HEIGHT - 30))
        
        pygame.display.flip()

    def draw_menu(self):
        self.screen.fill((20, 20, 30))

        for enemy in self.menu_enemies:
            enemy.update()
            enemy.draw(self.screen)

        self.menu_boss.update()
        self.menu_boss.draw(self.screen)

        self.menu_player.update()
        self.menu_player.draw(self.screen)

        self.menu_final_boss.update()
        self.menu_final_boss.draw(self.screen)

        title_text = self.title_font.render("MORZHAKA QUEST", True, YELLOW)
        title_shadow = self.title_font.render("MORZHAKA QUEST", True, (80, 60, 0))
        self.screen.blit(title_shadow, (SCREEN_WIDTH // 2 - title_text.get_width() // 2 + 3, 53))
        self.screen.blit(title_text, (SCREEN_WIDTH // 2 - title_text.get_width() // 2, 50))

        start_color = YELLOW if self.menu_selection == 0 else WHITE
        settings_color = YELLOW if self.menu_selection == 1 else WHITE
        quit_color = YELLOW if self.menu_selection == 2 else WHITE

        start_text = self.menu_font.render("START GAME", True, start_color)
        settings_text = self.menu_font.render("SETTINGS", True, settings_color)
        quit_text = self.menu_font.render("QUIT GAME", True, quit_color)

        menu_items = [start_text, settings_text, quit_text]
        menu_y_positions = [150, 210, 270]
        
        arrow_text = self.menu_font.render(">", True, YELLOW)
        self.screen.blit(arrow_text, (SCREEN_WIDTH // 2 - menu_items[self.menu_selection].get_width() // 2 - 40, menu_y_positions[self.menu_selection]))

        self.screen.blit(start_text, (SCREEN_WIDTH // 2 - start_text.get_width() // 2, 150))
        self.screen.blit(settings_text, (SCREEN_WIDTH // 2 - settings_text.get_width() // 2, 210))
        self.screen.blit(quit_text, (SCREEN_WIDTH // 2 - quit_text.get_width() // 2, 270))

        controls_text = self.small_font.render("Use UP/DOWN to select, ENTER to confirm", True, GRAY)
        self.screen.blit(controls_text, (SCREEN_WIDTH // 2 - controls_text.get_width() // 2, SCREEN_HEIGHT - 50))

    def draw_settings(self):
        self.screen.fill((20, 20, 30))
        
        title_text = self.title_font.render("SETTINGS", True, YELLOW)
        title_shadow = self.title_font.render("SETTINGS", True, (80, 60, 0))
        self.screen.blit(title_shadow, (SCREEN_WIDTH // 2 - title_text.get_width() // 2 + 3, 53))
        self.screen.blit(title_text, (SCREEN_WIDTH // 2 - title_text.get_width() // 2, 50))
        
        volume_color = YELLOW if self.settings_selection == 0 else WHITE
        fullscreen_color = YELLOW if self.settings_selection == 1 else WHITE
        back_color = YELLOW if self.settings_selection == 2 else WHITE
        
        volume_pct = int(self.master_volume * 100)
        volume_bar = "=" * (volume_pct // 10) + "-" * (10 - volume_pct // 10)
        volume_text = self.menu_font.render(f"VOLUME: [{volume_bar}] {volume_pct}%", True, volume_color)
        
        fullscreen_status = "ON" if self.is_fullscreen else "OFF"
        fullscreen_text = self.menu_font.render(f"FULLSCREEN: {fullscreen_status}", True, fullscreen_color)
        
        back_text = self.menu_font.render("BACK", True, back_color)
        
        settings_items = [volume_text, fullscreen_text, back_text]
        settings_y_positions = [150, 210, 270]
        
        arrow_text = self.menu_font.render(">", True, YELLOW)
        self.screen.blit(arrow_text, (SCREEN_WIDTH // 2 - settings_items[self.settings_selection].get_width() // 2 - 40, settings_y_positions[self.settings_selection]))
        
        self.screen.blit(volume_text, (SCREEN_WIDTH // 2 - volume_text.get_width() // 2, 150))
        self.screen.blit(fullscreen_text, (SCREEN_WIDTH // 2 - fullscreen_text.get_width() // 2, 210))
        self.screen.blit(back_text, (SCREEN_WIDTH // 2 - back_text.get_width() // 2, 270))
        
        controls_text = self.small_font.render("UP/DOWN: select | LEFT/RIGHT: adjust | ENTER/ESC: back", True, GRAY)
        self.screen.blit(controls_text, (SCREEN_WIDTH // 2 - controls_text.get_width() // 2, SCREEN_HEIGHT - 50))

    def toggle_fullscreen(self):
        self.is_fullscreen = not self.is_fullscreen
        if self.is_fullscreen:
            self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.FULLSCREEN)
        else:
            self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

    def set_volume(self, volume):
        self.master_volume = max(0.0, min(1.0, volume))
        SHOOT_SOUND.set_volume(self.master_volume * 0.6)
        DAMAGE_SOUND.set_volume(self.master_volume * 0.8)
        KILL_SOUND.set_volume(self.master_volume * 0.7)
        HEAL_SOUND.set_volume(self.master_volume * 0.7)
        VICTORY_SOUND.set_volume(self.master_volume * 0.8)
        BACKGROUND_MUSIC.set_volume(self.master_volume * 0.5)
        BOSS_MUSIC.set_volume(self.master_volume * 0.6)
        ICE_CAVE_MUSIC.set_volume(self.master_volume * 0.5)
        CASTLE_MUSIC.set_volume(self.master_volume * 0.5)
        FINAL_BOSS_MUSIC.set_volume(self.master_volume * 0.6)

    def run(self):
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.KEYDOWN:
                    if self.in_settings:
                        if event.key == pygame.K_UP or event.key == pygame.K_w:
                            self.settings_selection = (self.settings_selection - 1) % 3
                        elif event.key == pygame.K_DOWN or event.key == pygame.K_s:
                            self.settings_selection = (self.settings_selection + 1) % 3
                        elif event.key == pygame.K_LEFT or event.key == pygame.K_a:
                            if self.settings_selection == 0:
                                self.set_volume(self.master_volume - 0.1)
                        elif event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                            if self.settings_selection == 0:
                                self.set_volume(self.master_volume + 0.1)
                        elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                            if self.settings_selection == 1:
                                self.toggle_fullscreen()
                            elif self.settings_selection == 2:
                                self.in_settings = False
                        elif event.key == pygame.K_ESCAPE:
                            self.in_settings = False
                    elif self.in_menu:
                        if event.key == pygame.K_UP or event.key == pygame.K_w:
                            self.menu_selection = (self.menu_selection - 1) % 3
                        elif event.key == pygame.K_DOWN or event.key == pygame.K_s:
                            self.menu_selection = (self.menu_selection + 1) % 3
                        elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                            if self.menu_selection == 0:
                                self.start_cutscene()
                            elif self.menu_selection == 1:
                                self.in_settings = True
                                self.settings_selection = 0
                            else:
                                self.running = False
                        elif event.key == pygame.K_ESCAPE:
                            self.running = False
                    elif self.in_cutscene:
                        if event.key == pygame.K_SPACE or event.key == pygame.K_RETURN:
                            self.advance_cutscene()
                        elif event.key == pygame.K_ESCAPE:
                            self.in_cutscene = False
                            self.start_game()
                    else:
                        if event.key == pygame.K_ESCAPE:
                            self.running = False
                        elif event.key == pygame.K_p and not self.game_won and not self.game_over:
                            self.next_level()
                        elif event.key == pygame.K_r and (self.game_won or self.game_over):
                            if self.game_won:
                                self.current_level = 0
                                self.checkpoint_level = 0
                                self.ice_bullet_unlocked = False
                                self.explosive_bullet_unlocked = False
                                self.selected_bullet = 1
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
                            self.death_particles = []
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
            
            if self.in_settings:
                self.draw_settings()
                pygame.display.flip()
            elif self.in_menu:
                self.draw_menu()
                pygame.display.flip()
            elif self.in_cutscene:
                self.update_cutscene()
                self.draw_cutscene()
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
