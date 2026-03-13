import pygame
import sys
import random

from constants import (
    SCREEN_WIDTH, SCREEN_HEIGHT, TILE_SIZE, PLAYER_SPEED,
    BLACK, WHITE, GREEN, GRAY, YELLOW, RED, DARK_RED,
    ICE_FLOOR_COLOR, FINAL_BOSS_COLOR
)
from sounds import (
    SHOOT_SOUND, DAMAGE_SOUND, KILL_SOUND, HEAL_SOUND, VICTORY_SOUND,
    BACKGROUND_MUSIC, BOSS_MUSIC, ICE_CAVE_MUSIC, FINAL_BOSS_MUSIC, CASTLE_MUSIC
)
from sprites import create_player_sprites, create_player_sprite
from entities import Player, HealthKit, DeathParticle, NPC, SummonedAlly, ShadowAlly
from enemies import (
    Enemy, IceEnemy, CastleEnemyFast, CastleEnemyShooter,
    Boss, IceBoss, FinalBoss, ShadowBoss, ShadowEnemy, BigShadowEnemy
)
from projectiles import Projectile, IceProjectile, ExplosiveProjectile, ShadowOrbProjectile
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
        self.in_ending_cutscene = False
        self.paused = False
        self.pause_selection = 0
        self.cutscene_page = 0
        self.cutscene_timer = 0
        self.cutscene_fade = 0
        self.cutscene_text_progress = 0
        self.menu_selection = 0
        self.settings_selection = 0
        self.master_volume = 0.5
        self.is_fullscreen = False
        self.hard_mode = False
        self.init_menu_background()
        self.init_cutscene()
        self.init_ending_cutscene()
        self.set_volume(self.master_volume)
        
        self.levels = create_levels()
        self.current_level = 0
        self.checkpoint_level = 0
        self.ice_bullet_unlocked = False
        self.explosive_bullet_unlocked = False
        self.shadow_bullet_unlocked = False
        self.selected_bullet = 1
        self.death_particles = []
        
        self.dungeon_unlocked = True
        self.ice_cave_unlocked = False
        self.castle_unlocked = False
        self.dungeon_completed = False
        self.ice_cave_completed = False
        self.castle_completed = False
        self.is_village = True
        
        self.location_start_time = 0
        self.show_rank_screen = False
        self.rank_screen_data = None
        self.rank_display_timer = 0
        self.pending_ending_cutscene = False
        self.best_ranks = {
            'dungeon': {'rank': None, 'time': None},
            'ice_cave': {'rank': None, 'time': None},
            'castle': {'rank': None, 'time': None}
        }
        self.coins = 0
        
        self.has_dash = False
        self.has_laser = False
        self.has_shield = False
        self.has_wall_breaker = False
        self.has_regeneration = False
        self.has_summon = False
        self.has_shadow_army = False
        self.shadow_allies = []
        self.shadow_army_cooldown = 0
        self.has_cape = False
        self.cape_cooldown = 0
        self.cape_active = False
        self.cape_timer = 0
        self.current_ability = 0
        self.wall_breaker_cooldown = 0
        self.regeneration_cooldown = 0
        self.regeneration_active = False
        self.regeneration_timer = 0
        self.summon_cooldown = 0
        self.summoned_ally = None
        self.summon_phrase_timer = 0
        self.ability_cooldown = 0
        self.dash_active = False
        self.dash_timer = 0
        self.shield_active = False
        self.shield_timer = 0
        self.player_lasers = []
        self.laser_cooldown = 0
        self.laser_immune_enemies = {}
        self.in_shop = False
        self.shop_selection = 0
        self.in_inventory = False
        self.inventory_selection = 0
        
        self.ability_slots = 1
        self.second_ability = 0
        
        self.quests_completed = set()
        self.active_quest = None
        self.quest_kill_count = 0
        self.in_quest_dialog = False
        self.quest_dialog_page = 0
        self.quest_giver_talked = False
        
        self.dungeon = Dungeon(self.levels[self.current_level], self.current_level + 1)
        
        spawn = self.dungeon.spawn_point
        self.player = Player(
            spawn[0] * TILE_SIZE + 4,
            spawn[1] * TILE_SIZE + 4
        )
        
        self.enemies = []
        self.npcs = []
        self.spawn_enemies()
        self.spawn_npcs()
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

    def init_ending_cutscene(self):
        self.ending_pages = [
            {
                "title": "VICTORY!",
                "text": [
                    "With a final strike, Shadow Byako falls.",
                    "The dark lord's reign of terror has ended.",
                    "Light returns to the land..."
                ],
                "bg_color": (20, 15, 30)
            },
            {
                "title": "THE SHADOW FADES",
                "text": [
                    "As Shadow Byako's form dissolves,",
                    "the cursed castle begins to crumble.",
                    "You must escape quickly!"
                ],
                "bg_color": (30, 20, 25)
            },
            {
                "title": "MASTER MORZHAKA",
                "text": [
                    "You return to Morzhaka Village as a hero.",
                    "Master Morzhaka greets you with pride:",
                    "\"You have surpassed all my teachings.\"",
                    "\"The darkness will not return for generations.\""
                ],
                "bg_color": (25, 35, 20)
            },
            {
                "title": "A NEW DAWN",
                "text": [
                    "Peace returns to the land.",
                    "The villages rebuild, the people rejoice.",
                    "But you know that evil never truly dies...",
                    "",
                    "Perhaps one day, a new threat will arise.",
                    "And you will be ready."
                ],
                "bg_color": (40, 50, 60)
            },
            {
                "title": "THE END",
                "text": [
                    "Thank you for playing!",
                    "",
                    "You have defeated Shadow Byako",
                    "and saved the world of Morzhaka.",
                    "",
                    "Congratulations, hero!"
                ],
                "bg_color": (10, 10, 20)
            }
        ]
        self.ending_page = 0
        self.ending_timer = 0
        self.ending_fade = 0
        self.ending_text_progress = 0

    def start_ending_cutscene(self):
        self.in_ending_cutscene = True
        self.paused = False
        self.in_shop = False
        self.in_inventory = False
        self.in_settings = False
        self.game_won = False
        self.game_over = False
        self.ending_page = 0
        self.ending_timer = 0
        self.ending_fade = 0
        self.ending_text_progress = 0
        if self.current_music:
            self.current_music.stop()

    def advance_ending_cutscene(self):
        self.ending_page += 1
        self.ending_timer = 0
        self.ending_text_progress = 0
        self.ending_fade = 0

        if self.ending_page >= len(self.ending_pages):
            self.in_ending_cutscene = False
            self.castle_completed = True
            self.return_to_village()

    def update_ending_cutscene(self):
        self.ending_timer += 1

        if self.ending_fade < 255:
            self.ending_fade = min(255, self.ending_fade + 4)

        page_data = self.ending_pages[self.ending_page]
        total_chars = sum(len(line) for line in page_data["text"])
        if self.ending_text_progress < total_chars:
            self.ending_text_progress += 0.4

    def draw_ending_cutscene(self):
        page_data = self.ending_pages[self.ending_page]
        self.screen.fill(page_data["bg_color"])

        alpha = self.ending_fade

        if page_data["title"] == "THE END":
            title_color = (255, 215, 0)
        elif page_data["title"] == "VICTORY!":
            title_color = (100, 255, 100)
        else:
            title_color = (200, 180, 150)
        
        title_text = self.title_font.render(page_data["title"], True, title_color)
        title_rect = title_text.get_rect(center=(SCREEN_WIDTH // 2, 80))

        title_with_alpha = pygame.Surface(title_text.get_size(), pygame.SRCALPHA)
        title_with_alpha.blit(title_text, (0, 0))
        title_with_alpha.set_alpha(alpha)
        self.screen.blit(title_with_alpha, title_rect)

        y_offset = 180
        chars_shown = int(self.ending_text_progress)
        current_char = 0

        for line in page_data["text"]:
            if current_char >= chars_shown:
                break
            line_chars = min(len(line), chars_shown - current_char)
            current_char += len(line)
            display_line = line[:line_chars]

            text_surface = self.cutscene_font.render(display_line, True, (220, 220, 220))
            text_rect = text_surface.get_rect(center=(SCREEN_WIDTH // 2, y_offset))

            text_with_alpha = pygame.Surface(text_surface.get_size(), pygame.SRCALPHA)
            text_with_alpha.blit(text_surface, (0, 0))
            text_with_alpha.set_alpha(alpha)
            self.screen.blit(text_with_alpha, text_rect)

            y_offset += 40

        progress_text = f"Page {self.ending_page + 1}/{len(self.ending_pages)}"
        progress_surface = self.small_font.render(progress_text, True, (100, 100, 100))
        self.screen.blit(progress_surface, (10, SCREEN_HEIGHT - 30))

        hint_text = "Press SPACE or ENTER to continue..."
        hint_surface = self.small_font.render(hint_text, True, (150, 150, 150))
        hint_rect = hint_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 50))
        self.screen.blit(hint_surface, hint_rect)

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

    def check_village_doors(self):
        if not self.is_village:
            return
        
        level_data = self.levels[self.current_level]
        doors = level_data.get('doors', {})
        
        player_tile_x = int(self.player.x // TILE_SIZE)
        player_tile_y = int(self.player.y // TILE_SIZE)
        
        if 'castle' in doors:
            door_pos = doors['castle']
            if player_tile_y <= 2 and 10 <= player_tile_x <= 14:
                if self.castle_unlocked:
                    self.location_start_time = pygame.time.get_ticks()
                    self.go_to_level(20)
                    return

        if 'ice_cave' in doors:
            door_pos = doors['ice_cave']
            if player_tile_x <= 2 and 6 <= player_tile_y <= 8:
                if self.ice_cave_unlocked:
                    self.location_start_time = pygame.time.get_ticks()
                    self.go_to_level(10)
                    return

        if 'dungeon' in doors:
            door_pos = doors['dungeon']
            if player_tile_x >= 22 and 6 <= player_tile_y <= 8:
                if self.dungeon_unlocked:
                    self.location_start_time = pygame.time.get_ticks()
                    self.go_to_level(1)
                    return

    def get_player_damage(self, base_damage):
        """Get player damage adjusted for hard mode."""
        if self.hard_mode:
            return max(1, base_damage // 2)
        return base_damage

    def get_enemy_damage(self, base_damage):
        """Get enemy damage adjusted for hard mode."""
        if self.hard_mode:
            return base_damage * 2
        return base_damage

    def buff_enemy_for_hard_mode(self, enemy):
        """Buff enemy stats for hard mode."""
        if self.hard_mode and hasattr(enemy, 'health'):
            enemy.health *= 2
            enemy.max_health = enemy.health
        return enemy

    def buff_boss_for_hard_mode(self, boss):
        """Buff boss stats for hard mode."""
        if self.hard_mode and boss:
            if hasattr(boss, 'health'):
                boss.health = int(boss.health * 1.5)
                boss.max_health = boss.health
            if hasattr(boss, 'speed'):
                boss.speed *= 1.5
        return boss

    def spawn_enemies(self):
        self.enemies = []
        self.boss = None
        self.final_boss = None
        self.shadow_boss = None
        self.boss_projectiles = []
        self.enemy_projectiles = []
        level_data = self.levels[self.current_level]
        self.current_location = level_data.get('location', 1)
        self.is_village = level_data.get('is_village', False)
        
        self.is_boss_level = level_data.get('is_boss_level', False)
        self.is_shadow_boss_level = level_data.get('is_shadow_boss', False)

        if self.is_village:
            return

        if self.is_shadow_boss_level:
            boss_x = 20 * TILE_SIZE
            boss_y = 6 * TILE_SIZE
            self.shadow_boss = ShadowBoss(boss_x, boss_y)
            self.buff_boss_for_hard_mode(self.shadow_boss)
            return

        if self.is_boss_level:
            boss_x = 20 * TILE_SIZE
            boss_y = 6 * TILE_SIZE
            if level_data.get('is_ice_boss', False):
                self.final_boss = FinalBoss(boss_x, boss_y)
                self.buff_boss_for_hard_mode(self.final_boss)
            elif level_data.get('is_dungeon_boss', False):
                self.boss = Boss(boss_x, boss_y)
                self.buff_boss_for_hard_mode(self.boss)
            elif self.current_location == 2:
                self.boss = IceBoss(boss_x, boss_y)
                self.buff_boss_for_hard_mode(self.boss)
            else:
                self.boss = Boss(boss_x, boss_y)
                self.buff_boss_for_hard_mode(self.boss)
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
                            enemy = CastleEnemyFast(enemy_x, enemy_y)
                        else:
                            enemy = CastleEnemyShooter(enemy_x, enemy_y)
                    elif self.current_location == 2:
                        enemy = IceEnemy(enemy_x, enemy_y)
                    else:
                        enemy = Enemy(enemy_x, enemy_y)
                    self.buff_enemy_for_hard_mode(enemy)
                    self.enemies.append(enemy)
                    spawned += 1

    def spawn_npcs(self):
        self.npcs = []
        level_data = self.levels[self.current_level]
        
        npc_data = level_data.get('npcs', [])
        if not npc_data:
            return
        
        for npc_info in npc_data:
            pos = npc_info['pos']
            npc_x = pos[0] * TILE_SIZE + (TILE_SIZE - 36) // 2
            npc_y = pos[1] * TILE_SIZE + (TILE_SIZE - 42) // 2
            hat_type = npc_info.get('hat', 'wizard')
            name = npc_info.get('name', 'Villager')
            custom_phrases = npc_info.get('phrases', None)
            self.npcs.append(NPC(npc_x, npc_y, hat_type, name, custom_phrases))

    def spawn_one_enemy(self):
        if self.is_boss_level or self.is_shadow_boss_level or self.is_village:
            return
        level_data = self.levels[self.current_level]
        if level_data.get('enemy_count', 0) == 0:
            return
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
                            enemy = CastleEnemyFast(enemy_x, enemy_y)
                        else:
                            enemy = CastleEnemyShooter(enemy_x, enemy_y)
                    elif self.current_location == 2:
                        enemy = IceEnemy(enemy_x, enemy_y)
                    else:
                        enemy = Enemy(enemy_x, enemy_y)
                    self.buff_enemy_for_hard_mode(enemy)
                    self.enemies.append(enemy)
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

    def activate_ability(self, slot=1):
        ability = self.current_ability if slot == 1 else self.second_ability
        
        if ability == 0:
            return
        
        if ability == 4:
            if self.wall_breaker_cooldown <= 0:
                self.break_wall()
                self.wall_breaker_cooldown = 1800
            return

        if ability == 5:
            if self.regeneration_cooldown <= 0 and not self.regeneration_active:
                self.regeneration_active = True
                self.regeneration_timer = 0
                self.regeneration_cooldown = 3600
            return

        if ability == 6:
            if self.summon_cooldown <= 0 and self.summoned_ally is None:
                self.summon_ally()
                self.summon_cooldown = 18000
            return

        if ability == 7:
            if self.shadow_army_cooldown <= 0:
                self.summon_shadow_ally()
                self.shadow_army_cooldown = 900
            return

        if ability == 8:
            if self.cape_cooldown <= 0 and not self.cape_active:
                self.cape_active = True
                self.cape_timer = 600
                self.cape_cooldown = 2700
            return

        if self.ability_cooldown > 0:
            return

        if ability == 1:
            self.dash_active = True
            self.dash_timer = 60
            self.ability_cooldown = 1800
        elif ability == 2:
            if self.laser_cooldown <= 0:
                self.spawn_player_laser()
                self.laser_cooldown = 2100
        elif ability == 3:
            self.shield_active = True
            self.shield_timer = 900
            self.ability_cooldown = 1800
    
    def break_wall(self):
        px = self.player.x + self.player.width // 2
        py = self.player.y + self.player.height // 2
        
        dx, dy = self.player.last_direction
        
        check_x = px + dx * TILE_SIZE
        check_y = py + dy * TILE_SIZE
        
        tile_x = int(check_x // TILE_SIZE)
        tile_y = int(check_y // TILE_SIZE)
        
        level_data = self.levels[self.current_level]
        tiles = level_data['tiles']
        
        if 0 <= tile_y < len(tiles) and 0 <= tile_x < len(tiles[0]):
            if tiles[tile_y][tile_x] == 1:
                tiles[tile_y][tile_x] = 0
                self.dungeon.tiles[tile_y][tile_x] = 0
                self.dungeon.floor_pattern[(tile_x, tile_y)] = 0
                self.dungeon.create_cached_surfaces()
    
    def summon_ally(self):
        ally_x = self.player.x + self.player.width + 10
        ally_y = self.player.y
        self.summoned_ally = SummonedAlly(ally_x, ally_y)
        self.summon_phrase_timer = 180

    def summon_shadow_ally(self):
        import random
        offset_x = random.randint(-30, 30)
        offset_y = random.randint(-30, 30)
        ally_x = self.player.x + offset_x
        ally_y = self.player.y + offset_y
        self.shadow_allies.append(ShadowAlly(ally_x, ally_y))

    def spawn_player_laser(self):
        px = self.player.x + self.player.width // 2
        py = self.player.y + self.player.height // 2
        direction = self.player.last_direction
        
        player_tile_x = int(px // TILE_SIZE)
        player_tile_y = int(py // TILE_SIZE)
        
        if direction[0] > 0:
            start = (player_tile_x, player_tile_y)
            end = (player_tile_x + 4, player_tile_y)
            orientation = 'horizontal'
        elif direction[0] < 0:
            start = (player_tile_x - 4, player_tile_y)
            end = (player_tile_x, player_tile_y)
            orientation = 'horizontal'
        elif direction[1] > 0:
            start = (player_tile_x, player_tile_y)
            end = (player_tile_x, player_tile_y + 4)
            orientation = 'vertical'
        else:
            start = (player_tile_x, player_tile_y - 4)
            end = (player_tile_x, player_tile_y)
            orientation = 'vertical'
        
        start_x = start[0] * TILE_SIZE + TILE_SIZE // 2
        start_y = start[1] * TILE_SIZE + TILE_SIZE // 2
        end_x = end[0] * TILE_SIZE + TILE_SIZE // 2
        end_y = end[1] * TILE_SIZE + TILE_SIZE // 2
        
        beam_width = 6
        if orientation == 'vertical':
            rect = pygame.Rect(
                start_x - beam_width // 2,
                min(start_y, end_y),
                beam_width,
                abs(end_y - start_y)
            )
        else:
            rect = pygame.Rect(
                min(start_x, end_x),
                start_y - beam_width // 2,
                abs(end_x - start_x),
                beam_width
            )
        
        self.player_lasers.append({
            'start': start,
            'end': end,
            'orientation': orientation,
            'rect': rect,
            'emitter1': (start_x, start_y),
            'emitter2': (end_x, end_y),
            'animation_offset': 0
        })

    def update_abilities(self):
        if self.ability_cooldown > 0:
            self.ability_cooldown -= 1
        
        if self.dash_active:
            self.dash_timer -= 1
            if self.dash_timer <= 0:
                self.dash_active = False
        
        if self.shield_active:
            self.shield_timer -= 1
            if self.shield_timer <= 0:
                self.shield_active = False
        
        if self.laser_cooldown > 0:
            self.laser_cooldown -= 1
        
        if self.wall_breaker_cooldown > 0:
            self.wall_breaker_cooldown -= 1
        
        if self.regeneration_cooldown > 0:
            self.regeneration_cooldown -= 1
        
        if self.summon_cooldown > 0:
            self.summon_cooldown -= 1

        if self.shadow_army_cooldown > 0:
            self.shadow_army_cooldown -= 1

        if self.cape_cooldown > 0:
            self.cape_cooldown -= 1

        if self.cape_active:
            self.cape_timer -= 1
            if self.cape_timer <= 0:
                self.cape_active = False

        for shadow_ally in self.shadow_allies[:]:
            shadow_ally.update(self.player, self.enemies, self.boss, self.final_boss, self.shadow_boss, self.dungeon)
            if shadow_ally.health <= 0:
                self.shadow_allies.remove(shadow_ally)
                continue
            attack_target = shadow_ally.try_attack(self.enemies, self.boss, self.final_boss, self.shadow_boss)
            if attack_target:
                if attack_target == self.boss:
                    self.boss.take_damage(2)
                    if self.boss.health <= 0:
                        self.spawn_death_particles(self.boss)
                        self.show_location_rank('dungeon', (pygame.time.get_ticks() - self.location_start_time) / 1000)
                        self.boss = None
                        self.return_to_village()
                elif attack_target == self.final_boss:
                    self.final_boss.take_damage(2)
                    if self.final_boss.health <= 0:
                        self.spawn_death_particles(self.final_boss)
                        self.show_location_rank('ice_cave', (pygame.time.get_ticks() - self.location_start_time) / 1000)
                        self.final_boss = None
                        self.ice_bullet_unlocked = True
                        self.return_to_village()
                elif attack_target == self.shadow_boss:
                    self.shadow_boss.take_damage(2)
                    if self.shadow_boss.health <= 0:
                        self.spawn_death_particles(self.shadow_boss)
                        self.shadow_boss = None
                        self.shadow_bullet_unlocked = True
                        self.has_shadow_army = True
                        self.show_location_rank('castle', (pygame.time.get_ticks() - self.location_start_time) / 1000)
                        self.pending_ending_cutscene = True
                elif attack_target in self.enemies:
                    if hasattr(attack_target, 'take_damage'):
                        if attack_target.take_damage(2):
                            self.spawn_death_particles(attack_target)
                            self.enemies.remove(attack_target)
                            self.on_enemy_killed()
                            KILL_SOUND.play()
                    else:
                        self.spawn_death_particles(attack_target)
                        self.enemies.remove(attack_target)
                        self.on_enemy_killed()
                        KILL_SOUND.play()

        if self.summon_phrase_timer > 0:
            self.summon_phrase_timer -= 1
        
        if self.regeneration_active:
            self.regeneration_timer += 1
            if self.regeneration_timer >= 1200:
                self.regeneration_timer = 0
                if self.player.health < self.player.max_health:
                    self.player.heal(1)
        
        for laser in self.player_lasers:
            laser['animation_offset'] = (laser['animation_offset'] + 2) % 20
        
        self.check_player_laser_damage()

    def check_player_laser_damage(self):
        if not self.player_lasers:
            return
        
        enemies_to_remove = []
        for enemy_id in list(self.laser_immune_enemies.keys()):
            self.laser_immune_enemies[enemy_id] -= 1
            if self.laser_immune_enemies[enemy_id] <= 0:
                del self.laser_immune_enemies[enemy_id]
        
        for laser in self.player_lasers:
            laser_rect = laser['rect']
            
            for enemy in self.enemies[:]:
                enemy_id = id(enemy)
                if enemy_id in self.laser_immune_enemies:
                    continue
                    
                enemy_rect = pygame.Rect(enemy.x, enemy.y, enemy.width, enemy.height)
                if laser_rect.colliderect(enemy_rect):
                    self.laser_immune_enemies[enemy_id] = 12
                    if hasattr(enemy, 'take_damage'):
                        if enemy.take_damage(1):
                            self.spawn_death_particles(enemy)
                            if enemy in self.enemies:
                                self.enemies.remove(enemy)
                            self.coins += self.get_enemy_coin_reward()
                            self.on_enemy_killed()
                            KILL_SOUND.play()
                    else:
                        self.spawn_death_particles(enemy)
                        if enemy in self.enemies:
                            self.enemies.remove(enemy)
                        self.coins += self.get_enemy_coin_reward()
                        self.on_enemy_killed()
                        KILL_SOUND.play()

            boss_id = "boss"
            if self.boss and laser_rect.colliderect(pygame.Rect(self.boss.x, self.boss.y, self.boss.width, self.boss.height)):
                if boss_id not in self.laser_immune_enemies:
                    self.laser_immune_enemies[boss_id] = 12
                    self.boss.take_damage(1)
            
            final_boss_id = "final_boss"
            if self.final_boss and laser_rect.colliderect(pygame.Rect(self.final_boss.x, self.final_boss.y, self.final_boss.width, self.final_boss.height)):
                if final_boss_id not in self.laser_immune_enemies:
                    self.laser_immune_enemies[final_boss_id] = 12
                    self.final_boss.take_damage(1)
            
            shadow_boss_id = "shadow_boss"
            if self.shadow_boss and laser_rect.colliderect(pygame.Rect(self.shadow_boss.x, self.shadow_boss.y, self.shadow_boss.width, self.shadow_boss.height)):
                if shadow_boss_id not in self.laser_immune_enemies:
                    self.laser_immune_enemies[shadow_boss_id] = 12
                    if self.shadow_boss.take_damage(1):
                        self.shadow_boss = None
                        self.coins += 10
                        VICTORY_SOUND.play()
                        self.shadow_bullet_unlocked = True
                        self.has_shadow_army = True
                        time_taken = (pygame.time.get_ticks() - self.location_start_time) / 1000
                        self.show_location_rank('castle', time_taken)
                        self.pending_ending_cutscene = True

    def draw_player_lasers(self):
        if not self.player_lasers:
            return
        
        for laser in self.player_lasers:
            rect = laser['rect']
            orientation = laser['orientation']
            e1x, e1y = laser['emitter1']
            e2x, e2y = laser['emitter2']
            emitter_size = 10
            
            pygame.draw.rect(self.screen, (60, 80, 100), 
                            (e1x - emitter_size // 2, e1y - emitter_size // 2, emitter_size, emitter_size))
            pygame.draw.rect(self.screen, (60, 80, 100), 
                            (e2x - emitter_size // 2, e2y - emitter_size // 2, emitter_size, emitter_size))
            
            core_color = (50, 150, 255)
            edge_color = (200, 220, 255)
            
            glow_rect = rect.inflate(8, 8)
            glow_surface = pygame.Surface((glow_rect.width, glow_rect.height), pygame.SRCALPHA)
            pygame.draw.rect(glow_surface, (50, 150, 255, 60), glow_surface.get_rect())
            self.screen.blit(glow_surface, glow_rect.topleft)
            
            pygame.draw.rect(self.screen, core_color, rect)
            
            if orientation == 'horizontal':
                pygame.draw.line(self.screen, edge_color, 
                               (rect.left, rect.top),
                               (rect.right, rect.top), 1)
                pygame.draw.line(self.screen, edge_color, 
                               (rect.left, rect.bottom - 1),
                               (rect.right, rect.bottom - 1), 1)
            else:
                pygame.draw.line(self.screen, edge_color, 
                               (rect.left, rect.top),
                               (rect.left, rect.bottom), 1)
                pygame.draw.line(self.screen, edge_color, 
                               (rect.right - 1, rect.top),
                               (rect.right - 1, rect.bottom), 1)
            
            pygame.draw.circle(self.screen, (100, 180, 255), (e1x, e1y), emitter_size // 2 + 2)
            pygame.draw.circle(self.screen, (100, 180, 255), (e2x, e2y), emitter_size // 2 + 2)

    def draw_ability_slot(self, ability, x, y, key_label):
        """Draw a single ability slot."""
        ability_data = {
            1: ("DASH", (150, 100, 50)),
            2: ("LASER", (100, 150, 255)),
            3: ("SHIELD", (100, 200, 100)),
            4: ("BREAKER", (180, 120, 60)),
            5: ("REGEN", (255, 100, 150)),
            6: ("SUMMON", (255, 215, 100)),
            7: ("SHADOW", (140, 140, 180)),
            8: ("CAPE", (120, 50, 150))
        }
        
        if ability == 0:
            pygame.draw.rect(self.screen, (60, 60, 60), (x, y, 80, 30))
            pygame.draw.rect(self.screen, (100, 100, 100), (x, y, 80, 30), 2)
            text = self.small_font.render("EMPTY", True, (100, 100, 100))
            self.screen.blit(text, (x + 40 - text.get_width() // 2, y + 6))
            return
        
        name, color = ability_data.get(ability, ("???", WHITE))
        
        pygame.draw.rect(self.screen, color, (x, y, 80, 30))
        pygame.draw.rect(self.screen, WHITE, (x, y, 80, 30), 2)
        
        text = self.small_font.render(name, True, WHITE)
        self.screen.blit(text, (x + 40 - text.get_width() // 2, y + 6))
        
        status_text = None
        if ability == 2:
            if self.laser_cooldown > 0:
                cd_seconds = self.laser_cooldown // 60
                status_text = self.small_font.render(f"[{key_label}] CD:{cd_seconds}s", True, RED)
            else:
                status_text = self.small_font.render(f"[{key_label}] Ready", True, GREEN)
        elif ability == 4:
            if self.wall_breaker_cooldown > 0:
                cd_seconds = self.wall_breaker_cooldown // 60
                status_text = self.small_font.render(f"[{key_label}] CD:{cd_seconds}s", True, RED)
            else:
                status_text = self.small_font.render(f"[{key_label}] Ready", True, GREEN)
        elif ability == 5:
            if self.regeneration_active:
                status_text = self.small_font.render(f"[{key_label}] ACTIVE", True, GREEN)
            elif self.regeneration_cooldown > 0:
                cd_seconds = self.regeneration_cooldown // 60
                status_text = self.small_font.render(f"[{key_label}] CD:{cd_seconds}s", True, RED)
            else:
                status_text = self.small_font.render(f"[{key_label}] Ready", True, GREEN)
        elif ability == 6:
            if self.summoned_ally:
                status_text = self.small_font.render(f"[{key_label}] {self.summoned_ally.health}HP", True, GREEN)
            elif self.summon_cooldown > 0:
                cd_seconds = self.summon_cooldown // 60
                status_text = self.small_font.render(f"[{key_label}] CD:{cd_seconds}s", True, RED)
            else:
                status_text = self.small_font.render(f"[{key_label}] Ready", True, GREEN)
        elif ability == 7:
            active_count = len(self.shadow_allies)
            if self.shadow_army_cooldown > 0:
                cd_seconds = self.shadow_army_cooldown // 60
                status_text = self.small_font.render(f"[{key_label}] CD:{cd_seconds}s", True, RED)
            else:
                status_text = self.small_font.render(f"[{key_label}] x{active_count}", True, GREEN)
        elif ability == 8:
            if self.cape_active:
                time_left = self.cape_timer // 60
                status_text = self.small_font.render(f"[{key_label}] {time_left}s", True, (200, 150, 255))
            elif self.cape_cooldown > 0:
                cd_seconds = self.cape_cooldown // 60
                status_text = self.small_font.render(f"[{key_label}] CD:{cd_seconds}s", True, RED)
            else:
                status_text = self.small_font.render(f"[{key_label}] Ready", True, GREEN)
        elif ability == 1 or ability == 3:
            if self.ability_cooldown > 0:
                cd_seconds = self.ability_cooldown // 60
                status_text = self.small_font.render(f"[{key_label}] CD:{cd_seconds}s", True, RED)
            else:
                status_text = self.small_font.render(f"[{key_label}] Ready", True, GREEN)
        
        if status_text:
            self.screen.blit(status_text, (x + 90, y + 6))

    def draw_ability_ui(self):
        if self.current_ability == 0 and self.second_ability == 0:
            return
        
        y = SCREEN_HEIGHT - 50
        
        if self.ability_slots >= 2:
            x1 = SCREEN_WIDTH // 2 - 130
            x2 = SCREEN_WIDTH // 2 + 30
            self.draw_ability_slot(self.current_ability, x1, y, "E")
            self.draw_ability_slot(self.second_ability, x2, y, "Q")
        else:
            x = SCREEN_WIDTH // 2 - 60
            self.draw_ability_slot(self.current_ability, x, y, "E")
        
        if self.dash_active:
            dash_text = self.font.render("DASHING!", True, (255, 200, 100))
            self.screen.blit(dash_text, (SCREEN_WIDTH // 2 - dash_text.get_width() // 2, 120))

        if self.cape_active:
            cape_text = self.font.render("INVINCIBLE!", True, (200, 150, 255))
            self.screen.blit(cape_text, (SCREEN_WIDTH // 2 - cape_text.get_width() // 2, 150))

        if self.shield_active:
            shield_seconds = self.shield_timer // 60
            shield_text = self.font.render(f"SHIELD: {shield_seconds}s", True, (100, 255, 100))
            self.screen.blit(shield_text, (SCREEN_WIDTH // 2 - shield_text.get_width() // 2, 120))
        
        if self.regeneration_active:
            regen_text = self.font.render("REGENERATING!", True, (255, 150, 200))
            self.screen.blit(regen_text, (SCREEN_WIDTH // 2 - regen_text.get_width() // 2, 120))

        if self.summon_phrase_timer > 0:
            phrase = "with a crucian carp i have i summon BIG MORZHAKA!"
            bubble_padding = 12
            text_surface = self.small_font.render(phrase, True, (40, 40, 40))
            text_width = text_surface.get_width()
            text_height = text_surface.get_height()
            
            bubble_width = text_width + bubble_padding * 2
            bubble_height = text_height + bubble_padding * 2
            
            bubble_x = int(self.player.x + self.player.width // 2 - bubble_width // 2)
            bubble_y = int(self.player.y - bubble_height - 25)
            
            if bubble_x < 10:
                bubble_x = 10
            if bubble_x + bubble_width > SCREEN_WIDTH - 10:
                bubble_x = SCREEN_WIDTH - 10 - bubble_width
            if bubble_y < 10:
                bubble_y = 10
            
            pygame.draw.rect(self.screen, (255, 255, 220), (bubble_x, bubble_y, bubble_width, bubble_height), border_radius=10)
            pygame.draw.rect(self.screen, (180, 140, 60), (bubble_x, bubble_y, bubble_width, bubble_height), 3, border_radius=10)
            
            tail_points = [
                (int(self.player.x + self.player.width // 2) - 6, bubble_y + bubble_height),
                (int(self.player.x + self.player.width // 2) + 6, bubble_y + bubble_height),
                (int(self.player.x + self.player.width // 2), bubble_y + bubble_height + 12)
            ]
            pygame.draw.polygon(self.screen, (255, 255, 220), tail_points)
            pygame.draw.line(self.screen, (180, 140, 60), tail_points[0], tail_points[2], 3)
            pygame.draw.line(self.screen, (180, 140, 60), tail_points[1], tail_points[2], 3)
            
            self.screen.blit(text_surface, (bubble_x + bubble_padding, bubble_y + bubble_padding))

    def draw_shield_effect(self):
        if not self.shield_active:
            return
        
        cx = self.player.x + self.player.width // 2
        cy = self.player.y + self.player.height // 2
        
        pulse = abs((self.shield_timer % 30) - 15) / 15
        radius = 20 + int(5 * pulse)
        
        shield_surface = pygame.Surface((radius * 2 + 4, radius * 2 + 4), pygame.SRCALPHA)
        pygame.draw.circle(shield_surface, (100, 200, 255, 80), (radius + 2, radius + 2), radius)
        pygame.draw.circle(shield_surface, (150, 220, 255, 150), (radius + 2, radius + 2), radius, 2)
        self.screen.blit(shield_surface, (cx - radius - 2, cy - radius - 2))

    def get_enemy_coin_reward(self):
        if self.current_location == 3:
            return 3
        elif self.current_location == 2:
            return 2
        else:
            return 1

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

    def return_to_village(self):
        self.current_level = 0
        self.is_village = True
        self.dungeon = Dungeon(self.levels[self.current_level], self.current_level + 1)
        spawn = self.dungeon.spawn_point
        self.player.x = spawn[0] * TILE_SIZE + 4
        self.player.y = spawn[1] * TILE_SIZE + 4
        self.player.reset_velocity()
        if self.summoned_ally:
            self.summoned_ally.x = self.player.x + self.player.width + 10
            self.summoned_ally.y = self.player.y
        self.shadow_allies = []
        self.spawn_enemies()
        self.spawn_npcs()
        self.projectiles = []
        self.boss_projectiles = []
        self.enemy_projectiles = []
        self.death_particles = []
        self.health_kits = []
        self.health_kit_timer = 0
        self.damage_cooldown = 0
        self.shoot_cooldown = 0
        self.enemy_spawn_timer = 0
        self.player_lasers = []
        self.laser_cooldown = 0
        self.laser_immune_enemies = {}
        self.play_music(BACKGROUND_MUSIC)

    def calculate_rank(self, location, time_seconds):
        """Calculate rank based on completion time for a location."""
        rank_thresholds = {
            'dungeon': {'S': 120, 'A': 180, 'B': 240, 'C': 300},
            'ice_cave': {'S': 150, 'A': 210, 'B': 280, 'C': 360},
            'castle': {'S': 240, 'A': 330, 'B': 420, 'C': 540}
        }
        
        thresholds = rank_thresholds.get(location, rank_thresholds['dungeon'])
        
        if time_seconds <= thresholds['S']:
            return 'S'
        elif time_seconds <= thresholds['A']:
            return 'A'
        elif time_seconds <= thresholds['B']:
            return 'B'
        elif time_seconds <= thresholds['C']:
            return 'C'
        else:
            return 'D'

    def show_location_rank(self, location, time_seconds):
        """Display rank screen after completing a location."""
        rank = self.calculate_rank(location, time_seconds)
        
        is_new_best = False
        if self.best_ranks[location]['time'] is None or time_seconds < self.best_ranks[location]['time']:
            self.best_ranks[location]['rank'] = rank
            self.best_ranks[location]['time'] = time_seconds
            is_new_best = True
        
        location_names = {
            'dungeon': 'Dungeon',
            'ice_cave': 'Ice Cave',
            'castle': 'Shadow Byako Castle'
        }
        
        self.rank_screen_data = {
            'location': location_names.get(location, location),
            'rank': rank,
            'time': time_seconds,
            'is_new_best': is_new_best,
            'best_time': self.best_ranks[location]['time'],
            'best_rank': self.best_ranks[location]['rank']
        }
        self.show_rank_screen = True
        self.rank_display_timer = 0

    def draw_rank_screen(self):
        """Draw the rank display screen."""
        if not self.rank_screen_data:
            return
            
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.fill((0, 0, 0))
        overlay.set_alpha(200)
        self.screen.blit(overlay, (0, 0))
        
        data = self.rank_screen_data
        
        rank_colors = {
            'S': (255, 215, 0),
            'A': (0, 255, 100),
            'B': (100, 180, 255),
            'C': (255, 165, 0),
            'D': (180, 180, 180)
        }
        rank_color = rank_colors.get(data['rank'], (255, 255, 255))
        
        title_text = self.font.render(f"{data['location']} Completed!", True, (255, 255, 255))
        self.screen.blit(title_text, (SCREEN_WIDTH // 2 - title_text.get_width() // 2, 120))
        
        rank_font = pygame.font.Font(None, 120)
        rank_text = rank_font.render(data['rank'], True, rank_color)
        self.screen.blit(rank_text, (SCREEN_WIDTH // 2 - rank_text.get_width() // 2, 180))
        
        minutes = int(data['time'] // 60)
        seconds = int(data['time'] % 60)
        time_str = f"Time: {minutes}:{seconds:02d}"
        time_text = self.font.render(time_str, True, (255, 255, 255))
        self.screen.blit(time_text, (SCREEN_WIDTH // 2 - time_text.get_width() // 2, 290))
        
        if data['is_new_best']:
            new_best_text = self.font.render("NEW BEST TIME!", True, (255, 215, 0))
            self.screen.blit(new_best_text, (SCREEN_WIDTH // 2 - new_best_text.get_width() // 2, 330))
        else:
            best_minutes = int(data['best_time'] // 60)
            best_seconds = int(data['best_time'] % 60)
            best_str = f"Best: {best_minutes}:{best_seconds:02d} ({data['best_rank']})"
            best_text = self.small_font.render(best_str, True, (180, 180, 180))
            self.screen.blit(best_text, (SCREEN_WIDTH // 2 - best_text.get_width() // 2, 330))
        
        continue_text = self.small_font.render("Press SPACE to continue", True, (150, 150, 150))
        self.screen.blit(continue_text, (SCREEN_WIDTH // 2 - continue_text.get_width() // 2, 400))

    def get_quest_for_checkpoint(self, level):
        """Get quest data for a specific checkpoint level."""
        quests = {
            4: {
                'id': 'quest_dungeon_1',
                'name': 'Dungeon Slayer',
                'description': 'Defeat 10 enemies',
                'goal': 10,
                'type': 'kills',
                'reward_type': 'coins',
                'reward_amount': 100,
                'reward_text': '100 coins'
            },
            14: {
                'id': 'quest_ice_1',
                'name': 'Frost Hunter',
                'description': 'Defeat 15 enemies',
                'goal': 15,
                'type': 'kills',
                'reward_type': 'ability_slot',
                'reward_amount': 1,
                'reward_text': 'Second Ability Slot!'
            },
            24: {
                'id': 'quest_castle_1',
                'name': 'Shadow Purge',
                'description': 'Defeat 20 enemies',
                'goal': 20,
                'type': 'kills',
                'reward_type': 'ability',
                'reward_ability': 'cape',
                'reward_text': 'Morzhaka Cape ability!'
            }
        }
        return quests.get(level, None)

    def start_quest(self, quest):
        """Start a new quest."""
        self.active_quest = quest
        self.quest_kill_count = 0

    def complete_quest(self):
        """Complete the active quest and give rewards."""
        if not self.active_quest:
            return

        quest = self.active_quest
        self.quests_completed.add(quest['id'])

        if quest['reward_type'] == 'coins':
            self.coins += quest['reward_amount']
        elif quest['reward_type'] == 'ability_slot':
            self.ability_slots = 2
        elif quest['reward_type'] == 'ability':
            if quest.get('reward_ability') == 'shadow_army':
                self.has_shadow_army = True
                if self.current_ability == 0:
                    self.current_ability = 7
            elif quest.get('reward_ability') == 'cape':
                self.has_cape = True
                if self.current_ability == 0:
                    self.current_ability = 8

        self.active_quest = None
        self.quest_kill_count = 0

    def check_quest_progress(self):
        """Check if active quest is completed."""
        if not self.active_quest:
            return False
        if self.active_quest['type'] == 'kills':
            return self.quest_kill_count >= self.active_quest['goal']
        return False

    def draw_quest_dialog(self):
        """Draw the quest giver dialog."""
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.fill((0, 0, 0))
        overlay.set_alpha(180)
        self.screen.blit(overlay, (0, 0))
        
        dialog_width = 500
        dialog_height = 300
        dialog_x = SCREEN_WIDTH // 2 - dialog_width // 2
        dialog_y = SCREEN_HEIGHT // 2 - dialog_height // 2
        
        pygame.draw.rect(self.screen, (40, 30, 50), (dialog_x, dialog_y, dialog_width, dialog_height))
        pygame.draw.rect(self.screen, (100, 80, 120), (dialog_x, dialog_y, dialog_width, dialog_height), 3)
        
        title = self.font.render("Quest Master Cloakius", True, (200, 170, 255))
        self.screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, dialog_y + 20))
        
        quest = self.get_quest_for_checkpoint(self.current_level)
        
        if quest and quest['id'] in self.quests_completed:
            text1 = self.small_font.render("me already gave you quest reward", True, (200, 200, 200))
            text2 = self.small_font.render("go be hero somewhere else", True, (200, 200, 200))
            self.screen.blit(text1, (SCREEN_WIDTH // 2 - text1.get_width() // 2, dialog_y + 80))
            self.screen.blit(text2, (SCREEN_WIDTH // 2 - text2.get_width() // 2, dialog_y + 110))
            
            close_text = self.small_font.render("Press SPACE to close", True, (150, 150, 150))
            self.screen.blit(close_text, (SCREEN_WIDTH // 2 - close_text.get_width() // 2, dialog_y + 250))
        
        elif self.active_quest and self.check_quest_progress():
            text1 = self.font.render("QUEST COMPLETE!", True, (100, 255, 100))
            text2 = self.small_font.render(f"Reward: {self.active_quest['reward_text']}", True, (255, 215, 0))
            self.screen.blit(text1, (SCREEN_WIDTH // 2 - text1.get_width() // 2, dialog_y + 80))
            self.screen.blit(text2, (SCREEN_WIDTH // 2 - text2.get_width() // 2, dialog_y + 120))
            
            text3 = self.small_font.render("me knew you could do it", True, (200, 200, 200))
            self.screen.blit(text3, (SCREEN_WIDTH // 2 - text3.get_width() // 2, dialog_y + 160))
            
            claim_text = self.small_font.render("Press SPACE to claim reward", True, (100, 255, 100))
            self.screen.blit(claim_text, (SCREEN_WIDTH // 2 - claim_text.get_width() // 2, dialog_y + 250))
        
        elif self.active_quest:
            text1 = self.small_font.render(f"Quest: {self.active_quest['name']}", True, (255, 200, 100))
            text2 = self.small_font.render(self.active_quest['description'], True, (200, 200, 200))
            progress = f"Progress: {self.quest_kill_count}/{self.active_quest['goal']}"
            text3 = self.small_font.render(progress, True, (150, 200, 255))
            
            self.screen.blit(text1, (SCREEN_WIDTH // 2 - text1.get_width() // 2, dialog_y + 80))
            self.screen.blit(text2, (SCREEN_WIDTH // 2 - text2.get_width() // 2, dialog_y + 110))
            self.screen.blit(text3, (SCREEN_WIDTH // 2 - text3.get_width() // 2, dialog_y + 150))
            
            text4 = self.small_font.render("keep going hero morzhaka believes in you", True, (200, 200, 200))
            self.screen.blit(text4, (SCREEN_WIDTH // 2 - text4.get_width() // 2, dialog_y + 190))
            
            close_text = self.small_font.render("Press SPACE to close", True, (150, 150, 150))
            self.screen.blit(close_text, (SCREEN_WIDTH // 2 - close_text.get_width() // 2, dialog_y + 250))
        
        elif quest:
            text1 = self.small_font.render("greetings brave morzhaka", True, (200, 200, 200))
            text2 = self.small_font.render("me have quest for you", True, (200, 200, 200))
            self.screen.blit(text1, (SCREEN_WIDTH // 2 - text1.get_width() // 2, dialog_y + 70))
            self.screen.blit(text2, (SCREEN_WIDTH // 2 - text2.get_width() // 2, dialog_y + 95))
            
            quest_text = self.small_font.render(f"Quest: {quest['name']}", True, (255, 200, 100))
            desc_text = self.small_font.render(quest['description'], True, (200, 200, 200))
            reward_text = self.small_font.render(f"Reward: {quest['reward_text']}", True, (255, 215, 0))
            
            self.screen.blit(quest_text, (SCREEN_WIDTH // 2 - quest_text.get_width() // 2, dialog_y + 135))
            self.screen.blit(desc_text, (SCREEN_WIDTH // 2 - desc_text.get_width() // 2, dialog_y + 165))
            self.screen.blit(reward_text, (SCREEN_WIDTH // 2 - reward_text.get_width() // 2, dialog_y + 195))
            
            accept_text = self.small_font.render("Press SPACE to accept quest", True, (100, 255, 100))
            self.screen.blit(accept_text, (SCREEN_WIDTH // 2 - accept_text.get_width() // 2, dialog_y + 250))
        else:
            text1 = self.small_font.render("me have no quest for you here", True, (200, 200, 200))
            text2 = self.small_font.render("but me cape looks cool yes?", True, (200, 200, 200))
            self.screen.blit(text1, (SCREEN_WIDTH // 2 - text1.get_width() // 2, dialog_y + 100))
            self.screen.blit(text2, (SCREEN_WIDTH // 2 - text2.get_width() // 2, dialog_y + 130))
            
            close_text = self.small_font.render("Press SPACE to close", True, (150, 150, 150))
            self.screen.blit(close_text, (SCREEN_WIDTH // 2 - close_text.get_width() // 2, dialog_y + 250))

    def handle_quest_dialog_input(self):
        """Handle input for quest dialog."""
        quest = self.get_quest_for_checkpoint(self.current_level)
        
        if quest and quest['id'] in self.quests_completed:
            self.in_quest_dialog = False
        elif self.active_quest and self.check_quest_progress():
            self.complete_quest()
            self.in_quest_dialog = False
        elif self.active_quest:
            self.in_quest_dialog = False
        elif quest:
            self.start_quest(quest)
            self.in_quest_dialog = False
        else:
            self.in_quest_dialog = False

    def on_enemy_killed(self):
        """Called when an enemy is killed - tracks quest progress."""
        if self.active_quest and self.active_quest['type'] == 'kills':
            self.quest_kill_count += 1

    def go_to_level(self, level_index):
        self.current_level = level_index
        self.is_village = False
        self.dungeon = Dungeon(self.levels[self.current_level], self.current_level + 1)
        spawn = self.dungeon.spawn_point
        self.player.x = spawn[0] * TILE_SIZE + 4
        self.player.y = spawn[1] * TILE_SIZE + 4
        self.player.reset_velocity()
        if self.summoned_ally:
            self.summoned_ally.x = self.player.x + self.player.width + 10
            self.summoned_ally.y = self.player.y
        self.shadow_allies = []
        self.spawn_enemies()
        self.spawn_npcs()
        self.projectiles = []
        self.boss_projectiles = []
        self.enemy_projectiles = []
        self.death_particles = []
        self.health_kits = []
        self.health_kit_timer = 0
        self.damage_cooldown = 0
        self.shoot_cooldown = 0
        self.enemy_spawn_timer = 0
        self.player_lasers = []
        self.laser_cooldown = 0
        self.laser_immune_enemies = {}

        level_data = self.levels[self.current_level]
        location = level_data.get('location', 1)

        if level_data.get('checkpoint', False):
            self.checkpoint_level = self.current_level

        if level_data.get('is_shadow_boss', False):
            self.play_music(FINAL_BOSS_MUSIC)
        elif level_data.get('is_boss_level', False):
            self.play_music(BOSS_MUSIC)
        elif location == 3:
            self.play_music(CASTLE_MUSIC)
        elif location == 2:
            self.play_music(ICE_CAVE_MUSIC)
        else:
            self.play_music(BACKGROUND_MUSIC)

    def next_level(self):
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
        self.player.reset_velocity()
        if self.summoned_ally:
            self.summoned_ally.x = self.player.x + self.player.width + 10
            self.summoned_ally.y = self.player.y
        self.shadow_allies = []
        self.spawn_enemies()
        self.spawn_npcs()
        self.projectiles = []
        self.enemy_projectiles = []
        self.death_particles = []
        self.health_kits = []
        self.health_kit_timer = 0
        self.damage_cooldown = 0
        self.shoot_cooldown = 0
        self.enemy_spawn_timer = 0
        self.player_lasers = []
        self.laser_cooldown = 0
        self.laser_immune_enemies = {}
        
        level_data = self.levels[self.current_level]
        location = level_data.get('location', 1)
        
        if level_data.get('checkpoint', False):
            self.checkpoint_level = self.current_level
        
        if level_data.get('is_shadow_boss', False):
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
        
        if self.current_location == 2:
            self.player.move_on_ice(dx, dy, self.dungeon, self.enemies, self.boss, self.final_boss)
        elif dx != 0 or dy != 0:
            self.player.move(dx, dy, self.dungeon, self.enemies, self.boss, self.final_boss)
        
        if keys[pygame.K_1]:
            self.selected_bullet = 1
        if keys[pygame.K_2] and self.ice_bullet_unlocked:
            self.selected_bullet = 2
        if keys[pygame.K_3] and self.explosive_bullet_unlocked:
            self.selected_bullet = 3
        if keys[pygame.K_4] and self.shadow_bullet_unlocked:
            self.selected_bullet = 4

        if keys[pygame.K_SPACE] and self.shoot_cooldown <= 0:
            level_data = self.levels[self.current_level]
            has_npcs = self.is_village or level_data.get('npcs', [])
            npc_talked = False
            if has_npcs:
                for npc in self.npcs:
                    if npc.is_player_nearby(self.player) and npc.phrase_timer <= 0:
                        if npc.custom_phrases and npc.custom_phrases[0] == "QUEST_GIVER":
                            self.in_quest_dialog = True
                            self.shoot_cooldown = 15
                            npc_talked = True
                        else:
                            npc.interact()
                            self.shoot_cooldown = 15
                            npc_talked = True
                        break
            if not npc_talked and not self.is_village:
                proj_x = self.player.x + self.player.width // 2 - 4
                proj_y = self.player.y + self.player.height // 2 - 4
                if self.selected_bullet == 4 and self.shadow_bullet_unlocked:
                    self.projectiles.append(ShadowOrbProjectile(proj_x, proj_y, self.player.last_direction))
                    self.shoot_cooldown = 25
                elif self.selected_bullet == 3 and self.explosive_bullet_unlocked:
                    self.projectiles.append(ExplosiveProjectile(proj_x, proj_y, self.player.last_direction))
                    self.shoot_cooldown = 50
                elif self.selected_bullet == 2 and self.ice_bullet_unlocked:
                    self.projectiles.append(IceProjectile(proj_x, proj_y, self.player.last_direction))
                    self.shoot_cooldown = 15
                else:
                    self.projectiles.append(self.player.shoot())
                    self.shoot_cooldown = 15
                SHOOT_SOUND.play()

    def update(self):
        if self.in_ending_cutscene:
            return

        if self.show_rank_screen:
            return

        if self.in_quest_dialog:
            return

        if self.game_won or self.game_over:
            if self.current_music:
                self.current_music.stop()
                self.current_music = None
            return
        
        self.dungeon.update()
        
        if self.dash_active:
            self.player.speed = PLAYER_SPEED * 2.5
            self.player.can_pass_through_enemies = True
        else:
            self.player.speed = PLAYER_SPEED
            self.player.can_pass_through_enemies = False
        
        self.player.update()
        
        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= 1
        
        if not self.is_boss_level:
            self.enemy_spawn_timer += 1
            spawn_interval = self.enemy_spawn_interval // 2 if self.hard_mode else self.enemy_spawn_interval
            if self.enemy_spawn_timer >= spawn_interval:
                self.enemy_spawn_timer = 0
                self.spawn_one_enemy()
        
        self.health_kit_timer += 1
        if self.health_kit_timer >= self.health_kit_interval:
            self.health_kit_timer = 0
            self.spawn_health_kit()
        
        self.update_abilities()
        
        for kit in self.health_kits:
            if kit.collides_with_player(self.player):
                if self.player.health < self.player.max_health:
                    self.player.heal(1)
                    HEAL_SOUND.play()
                kit.active = False
        self.health_kits = [k for k in self.health_kits if k.active]
        
        for projectile in self.projectiles:
            if isinstance(projectile, ShadowOrbProjectile):
                projectile.update(self.dungeon, self.enemies)
            else:
                projectile.update(self.dungeon)

        for projectile in self.projectiles:
            if not projectile.active:
                continue
            
            if isinstance(projectile, ShadowOrbProjectile):
                for enemy in self.enemies[:]:
                    if projectile.collides_with_enemy(enemy):
                        if hasattr(enemy, 'take_damage'):
                            if enemy.take_damage(self.get_player_damage(5)):
                                self.spawn_death_particles(enemy)
                                self.enemies.remove(enemy)
                                self.coins += self.get_enemy_coin_reward()
                                self.on_enemy_killed()
                                KILL_SOUND.play()
                            else:
                                DAMAGE_SOUND.play()
                        else:
                            self.spawn_death_particles(enemy)
                            self.enemies.remove(enemy)
                            self.coins += self.get_enemy_coin_reward()
                            self.on_enemy_killed()
                            KILL_SOUND.play()
            elif isinstance(projectile, ExplosiveProjectile):
                for enemy in self.enemies[:]:
                    if projectile.damages_enemy(enemy):
                        if hasattr(enemy, 'take_damage'):
                            if enemy.take_damage(self.get_player_damage(3)):
                                self.spawn_death_particles(enemy)
                                self.enemies.remove(enemy)
                                self.coins += self.get_enemy_coin_reward()
                                self.on_enemy_killed()
                                KILL_SOUND.play()
                            else:
                                DAMAGE_SOUND.play()
                        else:
                            self.spawn_death_particles(enemy)
                            self.enemies.remove(enemy)
                            self.coins += self.get_enemy_coin_reward()
                            self.on_enemy_killed()
                            KILL_SOUND.play()
            else:
                for enemy in self.enemies[:]:
                    if projectile.collides_with_enemy(enemy):
                        if not isinstance(projectile, IceProjectile):
                            projectile.active = False
                        
                        if hasattr(enemy, 'take_damage'):
                            if enemy.take_damage(self.get_player_damage(1)):
                                self.spawn_death_particles(enemy)
                                self.enemies.remove(enemy)
                                self.coins += self.get_enemy_coin_reward()
                                self.on_enemy_killed()
                                KILL_SOUND.play()
                            else:
                                DAMAGE_SOUND.play()
                        else:
                            self.spawn_death_particles(enemy)
                            self.enemies.remove(enemy)
                            self.coins += self.get_enemy_coin_reward()
                            self.on_enemy_killed()
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
                            damage = 3
                            if self.boss.take_damage(damage):
                                self.boss = None
                                self.coins += 10
                                VICTORY_SOUND.play()
                                level_data = self.levels[self.current_level]
                                if level_data.get('is_dungeon_boss', False):
                                    self.dungeon_completed = True
                                    self.ice_cave_unlocked = True
                                    self.ice_bullet_unlocked = True
                                    time_taken = (pygame.time.get_ticks() - self.location_start_time) / 1000
                                    self.show_location_rank('dungeon', time_taken)
                                elif level_data.get('is_ice_boss', False):
                                    self.ice_cave_completed = True
                                    self.castle_unlocked = True
                                    self.explosive_bullet_unlocked = True
                                    time_taken = (pygame.time.get_ticks() - self.location_start_time) / 1000
                                    self.show_location_rank('ice_cave', time_taken)
                                else:
                                    self.next_level()
                            break
                elif projectile.get_rect().colliderect(self.boss.get_rect()):
                    if isinstance(projectile, IceProjectile):
                        if 'boss' in projectile.hit_enemies:
                            continue
                        projectile.hit_enemies.add('boss')
                    else:
                        projectile.active = False
                    if self.boss.take_damage(1):
                        self.boss = None
                        self.coins += 10
                        VICTORY_SOUND.play()
                        level_data = self.levels[self.current_level]
                        if level_data.get('is_dungeon_boss', False):
                            self.dungeon_completed = True
                            self.ice_cave_unlocked = True
                            self.ice_bullet_unlocked = True
                            time_taken = (pygame.time.get_ticks() - self.location_start_time) / 1000
                            self.show_location_rank('dungeon', time_taken)
                        elif level_data.get('is_ice_boss', False):
                            self.ice_cave_completed = True
                            self.castle_unlocked = True
                            self.explosive_bullet_unlocked = True
                            time_taken = (pygame.time.get_ticks() - self.location_start_time) / 1000
                            self.show_location_rank('ice_cave', time_taken)
                        else:
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
                            damage = 3
                            if self.final_boss.take_damage(damage):
                                self.final_boss = None
                                self.coins += 10
                                self.ice_cave_completed = True
                                self.castle_unlocked = True
                                self.explosive_bullet_unlocked = True
                                VICTORY_SOUND.play()
                                time_taken = (pygame.time.get_ticks() - self.location_start_time) / 1000
                                self.show_location_rank('ice_cave', time_taken)
                                return
                            break
                elif projectile.get_rect().colliderect(self.final_boss.get_rect()):
                    if isinstance(projectile, IceProjectile):
                        if 'final_boss' in projectile.hit_enemies:
                            continue
                        projectile.hit_enemies.add('final_boss')
                    else:
                        projectile.active = False
                    if self.final_boss.take_damage(1):
                        self.final_boss = None
                        self.coins += 10
                        self.ice_cave_completed = True
                        self.castle_unlocked = True
                        self.explosive_bullet_unlocked = True
                        VICTORY_SOUND.play()
                        time_taken = (pygame.time.get_ticks() - self.location_start_time) / 1000
                        self.show_location_rank('ice_cave', time_taken)
                        return
                    break

        if self.shadow_boss:
            for projectile in self.projectiles:
                if not projectile.active:
                    continue

                if isinstance(projectile, ExplosiveProjectile):
                    if not projectile.exploding:
                        if projectile.get_rect().colliderect(self.shadow_boss.get_rect()):
                            projectile.explode()
                            damage = 3
                            if self.shadow_boss.take_damage(damage):
                                self.shadow_boss = None
                                self.coins += 10
                                VICTORY_SOUND.play()
                                self.shadow_bullet_unlocked = True
                                self.has_shadow_army = True
                                time_taken = (pygame.time.get_ticks() - self.location_start_time) / 1000
                                self.show_location_rank('castle', time_taken)
                                self.pending_ending_cutscene = True
                            break
                elif projectile.get_rect().colliderect(self.shadow_boss.get_rect()):
                    if isinstance(projectile, IceProjectile):
                        if 'shadow_boss' in projectile.hit_enemies:
                            continue
                        projectile.hit_enemies.add('shadow_boss')
                    else:
                        projectile.active = False
                    if self.shadow_boss.take_damage(1):
                        self.shadow_boss = None
                        self.coins += 10
                        VICTORY_SOUND.play()
                        self.shadow_bullet_unlocked = True
                        self.has_shadow_army = True
                        time_taken = (pygame.time.get_ticks() - self.location_start_time) / 1000
                        self.show_location_rank('castle', time_taken)
                        self.pending_ending_cutscene = True
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
            if self.summoned_ally:
                ally_rect = self.summoned_ally.get_rect()
                boss_rect = self.boss.get_rect()
                if boss_rect.colliderect(ally_rect):
                    if self.summoned_ally.take_damage(1):
                        self.summoned_ally = None
                    else:
                        dx = self.boss.x - self.summoned_ally.x
                        dy = self.boss.y - self.summoned_ally.y
                        dist = (dx ** 2 + dy ** 2) ** 0.5
                        if dist > 0:
                            push_x = (dx / dist) * 4
                            push_y = (dy / dist) * 4
                            if not self.dungeon.is_wall(self.boss.x + push_x, self.boss.y, self.boss.width, self.boss.height):
                                self.boss.x += push_x
                            if not self.dungeon.is_wall(self.boss.x, self.boss.y + push_y, self.boss.width, self.boss.height):
                                self.boss.y += push_y
                            if not self.dungeon.is_wall(self.summoned_ally.x - push_x, self.summoned_ally.y, self.summoned_ally.width, self.summoned_ally.height):
                                self.summoned_ally.x -= push_x
                            if not self.dungeon.is_wall(self.summoned_ally.x, self.summoned_ally.y - push_y, self.summoned_ally.width, self.summoned_ally.height):
                                self.summoned_ally.y -= push_y
            for shadow_ally in self.shadow_allies[:]:
                ally_rect = shadow_ally.get_rect()
                boss_rect = self.boss.get_rect()
                if boss_rect.colliderect(ally_rect):
                    if shadow_ally.take_damage(1):
                        self.shadow_allies.remove(shadow_ally)
        
        if self.final_boss:
            self.final_boss.move_towards_player(self.player, self.dungeon)
            self.final_boss.teleport(self.player, self.dungeon)
            self.final_boss.update_blink()
            if self.final_boss.should_spawn_enemy():
                spawn_pos = self.final_boss.get_spawn_position(self.dungeon)
                if spawn_pos:
                    self.enemies.append(IceEnemy(spawn_pos[0], spawn_pos[1]))
            if self.summoned_ally:
                ally_rect = self.summoned_ally.get_rect()
                boss_rect = self.final_boss.get_rect()
                if boss_rect.colliderect(ally_rect):
                    if self.summoned_ally.take_damage(1):
                        self.summoned_ally = None
                    else:
                        dx = self.final_boss.x - self.summoned_ally.x
                        dy = self.final_boss.y - self.summoned_ally.y
                        dist = (dx ** 2 + dy ** 2) ** 0.5
                        if dist > 0:
                            push_x = (dx / dist) * 4
                            push_y = (dy / dist) * 4
                            if not self.dungeon.is_wall(self.final_boss.x + push_x, self.final_boss.y, self.final_boss.width, self.final_boss.height):
                                self.final_boss.x += push_x
                            if not self.dungeon.is_wall(self.final_boss.x, self.final_boss.y + push_y, self.final_boss.width, self.final_boss.height):
                                self.final_boss.y += push_y
                            if not self.dungeon.is_wall(self.summoned_ally.x - push_x, self.summoned_ally.y, self.summoned_ally.width, self.summoned_ally.height):
                                self.summoned_ally.x -= push_x
                            if not self.dungeon.is_wall(self.summoned_ally.x, self.summoned_ally.y - push_y, self.summoned_ally.width, self.summoned_ally.height):
                                self.summoned_ally.y -= push_y
            for shadow_ally in self.shadow_allies[:]:
                ally_rect = shadow_ally.get_rect()
                boss_rect = self.final_boss.get_rect()
                if boss_rect.colliderect(ally_rect):
                    if shadow_ally.take_damage(1):
                        self.shadow_allies.remove(shadow_ally)

        if self.shadow_boss:
            self.shadow_boss.move_towards_player(self.player, self.dungeon)
            self.shadow_boss.teleport(self.player, self.dungeon)
            self.shadow_boss.update_blink()
            proj = self.shadow_boss.shoot_at_player(self.player)
            if proj:
                self.boss_projectiles.append(proj)
                SHOOT_SOUND.play()
            shadow_enemy = self.shadow_boss.try_spawn_shadow_enemy(self.dungeon)
            if shadow_enemy:
                self.enemies.append(shadow_enemy)
            big_shadow = self.shadow_boss.try_spawn_big_shadow(self.dungeon)
            if big_shadow:
                self.enemies.append(big_shadow)
            if self.summoned_ally:
                ally_rect = self.summoned_ally.get_rect()
                boss_rect = self.shadow_boss.get_rect()
                if boss_rect.colliderect(ally_rect):
                    if self.summoned_ally.take_damage(1):
                        self.summoned_ally = None
                    else:
                        dx = self.shadow_boss.x - self.summoned_ally.x
                        dy = self.shadow_boss.y - self.summoned_ally.y
                        dist = (dx ** 2 + dy ** 2) ** 0.5
                        if dist > 0:
                            push_x = (dx / dist) * 4
                            push_y = (dy / dist) * 4
                            if not self.dungeon.is_wall(self.shadow_boss.x + push_x, self.shadow_boss.y, self.shadow_boss.width, self.shadow_boss.height):
                                self.shadow_boss.x += push_x
                            if not self.dungeon.is_wall(self.shadow_boss.x, self.shadow_boss.y + push_y, self.shadow_boss.width, self.shadow_boss.height):
                                self.shadow_boss.y += push_y
                            if not self.dungeon.is_wall(self.summoned_ally.x - push_x, self.summoned_ally.y, self.summoned_ally.width, self.summoned_ally.height):
                                self.summoned_ally.x -= push_x
                            if not self.dungeon.is_wall(self.summoned_ally.x, self.summoned_ally.y - push_y, self.summoned_ally.width, self.summoned_ally.height):
                                self.summoned_ally.y -= push_y
            for shadow_ally in self.shadow_allies[:]:
                ally_rect = shadow_ally.get_rect()
                boss_rect = self.shadow_boss.get_rect()
                if boss_rect.colliderect(ally_rect):
                    if shadow_ally.take_damage(1):
                        self.shadow_allies.remove(shadow_ally)

        for proj in self.boss_projectiles:
            if hasattr(proj, 'tracking'):
                proj.update(self.dungeon, self.player)
            else:
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
            if self.summoned_ally:
                ally_rect = self.summoned_ally.get_rect()
                enemy_rect = enemy.get_rect()
                if enemy_rect.colliderect(ally_rect):
                    if self.summoned_ally.take_damage(1):
                        self.summoned_ally = None
                    else:
                        dx = enemy.x - self.summoned_ally.x
                        dy = enemy.y - self.summoned_ally.y
                        dist = (dx ** 2 + dy ** 2) ** 0.5
                        if dist > 0:
                            push_x = (dx / dist) * 3
                            push_y = (dy / dist) * 3
                            if not self.dungeon.is_wall(enemy.x + push_x, enemy.y, enemy.width, enemy.height):
                                enemy.x += push_x
                            if not self.dungeon.is_wall(enemy.x, enemy.y + push_y, enemy.width, enemy.height):
                                enemy.y += push_y
            for shadow_ally in self.shadow_allies[:]:
                ally_rect = shadow_ally.get_rect()
                enemy_rect = enemy.get_rect()
                if enemy_rect.colliderect(ally_rect):
                    if shadow_ally.take_damage(1):
                        self.shadow_allies.remove(shadow_ally)
        
        for proj in self.enemy_projectiles:
            proj.update(self.dungeon)
        
        self.enemy_projectiles = [p for p in self.enemy_projectiles if p.active]
        
        if self.summoned_ally:
            self.summoned_ally.update(self.player, self.enemies, self.boss, self.final_boss, self.shadow_boss, self.dungeon)
            
            target = self.summoned_ally.try_attack(self.enemies, self.boss, self.final_boss, self.shadow_boss)
            if target:
                if target in self.enemies:
                    if hasattr(target, 'take_damage'):
                        if target.take_damage(2):
                            self.spawn_death_particles(target)
                            self.enemies.remove(target)
                            self.coins += self.get_enemy_coin_reward()
                            self.on_enemy_killed()
                            KILL_SOUND.play()
                    else:
                        self.spawn_death_particles(target)
                        self.enemies.remove(target)
                        self.coins += self.get_enemy_coin_reward()
                        self.on_enemy_killed()
                        KILL_SOUND.play()
                elif target == self.boss and self.boss:
                    self.boss.take_damage(2)
                elif target == self.final_boss and self.final_boss:
                    self.final_boss.take_damage(2)
                elif target == self.shadow_boss and self.shadow_boss:
                    self.shadow_boss.take_damage(2)
            
        if self.damage_cooldown > 0:
            self.damage_cooldown -= 1
        else:
            for enemy in self.enemies:
                if enemy.is_touching_player(self.player):
                    if self.dash_active or self.cape_active:
                        continue
                    if self.player.take_damage():
                        self.game_over = True
                    DAMAGE_SOUND.play()
                    self.damage_cooldown = 60
                    self.regeneration_active = False
                    break

            if self.boss and self.boss.is_touching_player(self.player) and not self.dash_active and not self.cape_active:
                if self.player.take_damage():
                    self.game_over = True
                DAMAGE_SOUND.play()
                self.damage_cooldown = 60
                self.regeneration_active = False
            
            if self.final_boss and self.final_boss.is_touching_player(self.player) and not self.dash_active and not self.cape_active:
                if self.player.take_damage():
                    self.game_over = True
                DAMAGE_SOUND.play()
                self.damage_cooldown = 60
                self.regeneration_active = False

            if self.shadow_boss and self.shadow_boss.is_touching_player(self.player) and not self.dash_active and not self.cape_active:
                if self.player.take_damage():
                    self.game_over = True
                DAMAGE_SOUND.play()
                self.damage_cooldown = 60
                self.regeneration_active = False

            for proj in self.boss_projectiles:
                if proj.collides_with_player(self.player):
                    if self.dash_active or self.cape_active:
                        continue
                    if self.shield_active:
                        proj.dx = -proj.dx
                        proj.dy = -proj.dy
                        self.projectiles.append(proj)
                        self.boss_projectiles.remove(proj)
                    else:
                        proj.active = False
                        if self.player.take_damage():
                            self.game_over = True
                        DAMAGE_SOUND.play()
                        self.damage_cooldown = 60
                        self.regeneration_active = False
                    break

            for proj in self.enemy_projectiles:
                if proj.collides_with_player(self.player):
                    if self.dash_active or self.cape_active:
                        continue
                    if self.shield_active:
                        proj.dx = -proj.dx
                        proj.dy = -proj.dy
                        self.projectiles.append(proj)
                        self.enemy_projectiles.remove(proj)
                    else:
                        proj.active = False
                        if self.player.take_damage():
                            self.game_over = True
                        DAMAGE_SOUND.play()
                        self.damage_cooldown = 60
                        self.regeneration_active = False
                    break
            
            if self.dungeon.check_laser_collision(self.player) and not self.dash_active and not self.cape_active:
                if self.player.take_damage():
                    self.game_over = True
                DAMAGE_SOUND.play()
                self.damage_cooldown = 60
                self.regeneration_active = False
        
        for npc in self.npcs:
            npc.update()
        
        if self.is_village:
            self.check_village_doors()
        elif not self.is_boss_level and self.dungeon.check_exit(self.player):
            self.next_level()

    def draw(self):
        if self.in_ending_cutscene:
            return
            
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
            
            if self.is_village:
                self.draw_village_well()
                self.draw_village_doors()
                self.draw_shop()
            
            level_data = self.levels[self.current_level]
            if level_data.get('has_shop', False):
                self.draw_checkpoint_shop()
            
            for npc in self.npcs:
                npc.draw(self.screen)
            
            self.player.draw(self.screen)
            
            if self.shield_active:
                self.draw_shield_effect()
            
            if self.player_lasers:
                self.draw_player_lasers()
            
            for enemy in self.enemies:
                enemy.draw(self.screen)
            
            if self.summoned_ally:
                self.summoned_ally.draw(self.screen)

            for shadow_ally in self.shadow_allies:
                shadow_ally.draw(self.screen)

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
            
            if self.is_village:
                location_text = self.font.render("Morzhaka Village", True, (180, 160, 100))
            elif self.is_shadow_boss_level:
                location_text = self.font.render("THE DARK LORD!", True, (200, 30, 30))
            elif self.is_boss_level:
                location_text = self.font.render("BOSS FIGHT!", True, RED)
            else:
                location = self.levels[self.current_level].get('location', 1)
                if location == 3:
                    location_text = self.font.render("Shadow Byako Castle", True, (150, 150, 160))
                elif location == 2:
                    location_text = self.font.render("Ice Caves", True, ICE_FLOOR_COLOR)
                else:
                    location_text = self.font.render("Dungeon", True, WHITE)
            self.screen.blit(location_text, (10, 10))
            
            coin_text = self.font.render(f"Coins: {self.coins}", True, YELLOW)
            self.screen.blit(coin_text, (10, 40))
            
            health_label = self.small_font.render("HP:", True, WHITE)
            self.screen.blit(health_label, (SCREEN_WIDTH - 185, 10))
            self.player.draw_health(self.screen, SCREEN_WIDTH - 155, 8)

            if self.hard_mode:
                hard_text = self.small_font.render("HARD MODE", True, (255, 80, 80))
                self.screen.blit(hard_text, (SCREEN_WIDTH // 2 - hard_text.get_width() // 2, 10))

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
            
            if self.shadow_bullet_unlocked:
                bullet4_color = (180, 100, 255) if self.selected_bullet == 4 else (120, 60, 180)
                bullet4_text = self.small_font.render("[4] Shadow", True, bullet4_color)
                self.screen.blit(bullet4_text, (SCREEN_WIDTH - 185, 95))
            
            self.draw_ability_ui()
            
            if self.active_quest:
                quest_text = f"Quest: {self.quest_kill_count}/{self.active_quest['goal']} kills"
                quest_surface = self.small_font.render(quest_text, True, (255, 200, 100))
                self.screen.blit(quest_surface, (10, SCREEN_HEIGHT - 55))

            if self.in_shop:
                self.draw_shop_menu()

            for npc in self.npcs:
                npc.draw_speech_bubble(self.screen, self.small_font)
                if npc.is_player_nearby(self.player) and not npc.current_phrase:
                    prompt = self.small_font.render(f"[SPACE/ENTER] Talk to {npc.name}", True, (220, 200, 150))
                    prompt_x = int(npc.x + npc.width // 2 - prompt.get_width() // 2)
                    prompt_y = int(npc.y - 25)
                    self.screen.blit(prompt, (prompt_x, prompt_y))
            
            level_data = self.levels[self.current_level]
            if self.is_village:
                hint_text = self.small_font.render("Walk to a door to enter!", True, (180, 160, 100))
            elif level_data.get('checkpoint', False) and level_data.get('has_shop', False):
                hint_text = self.small_font.render("Safe zone! Rest and shop before continuing.", True, (100, 200, 100))
            elif self.is_shadow_boss_level:
                hint_text = self.small_font.render("Defeat the Dark Lord!", True, (200, 30, 30))
            elif self.is_boss_level:
                hint_text = self.small_font.render("Defeat the guardian!", True, RED)
            elif self.current_location == 3:
                hint_text = self.small_font.render("Find the exit!", True, (150, 150, 160))
            else:
                hint_text = self.small_font.render("Find the exit!", True, YELLOW)
            self.screen.blit(hint_text, (10, 70))
            
            controls_text = self.small_font.render("WASD/Arrows: move | SPACE: shoot | 1/2/3: switch bullets", True, WHITE)
            self.screen.blit(controls_text, (10, SCREEN_HEIGHT - 30))

        if self.show_rank_screen:
            self.draw_rank_screen()

        if self.in_quest_dialog:
            self.draw_quest_dialog()

        pygame.display.flip()

    def draw_shop(self):
        cx = 12 * TILE_SIZE + TILE_SIZE // 2
        cy = 10 * TILE_SIZE
        
        pygame.draw.rect(self.screen, (100, 70, 50), (cx - 40, cy - 20, 80, 50))
        pygame.draw.rect(self.screen, (80, 55, 40), (cx - 40, cy - 20, 80, 50), 3)
        pygame.draw.rect(self.screen, (120, 90, 60), (cx - 35, cy - 15, 70, 8))
        
        sign_text = self.small_font.render("SHOP", True, YELLOW)
        self.screen.blit(sign_text, (cx - sign_text.get_width() // 2, cy - 5))
        
        player_tile_x = int(self.player.x // TILE_SIZE)
        player_tile_y = int(self.player.y // TILE_SIZE)
        if 10 <= player_tile_x <= 14 and 9 <= player_tile_y <= 11:
            prompt = self.small_font.render("Press ENTER to shop", True, WHITE)
            self.screen.blit(prompt, (cx - prompt.get_width() // 2, cy + 35))

    def draw_checkpoint_shop(self):
        level_data = self.levels[self.current_level]
        shop_pos = level_data.get('shop_pos', (12, 6))
        cx = shop_pos[0] * TILE_SIZE + TILE_SIZE // 2
        cy = shop_pos[1] * TILE_SIZE
        
        pygame.draw.rect(self.screen, (100, 70, 50), (cx - 40, cy - 20, 80, 50))
        pygame.draw.rect(self.screen, (80, 55, 40), (cx - 40, cy - 20, 80, 50), 3)
        pygame.draw.rect(self.screen, (120, 90, 60), (cx - 35, cy - 15, 70, 8))
        
        sign_text = self.small_font.render("SHOP", True, YELLOW)
        self.screen.blit(sign_text, (cx - sign_text.get_width() // 2, cy - 5))
        
        shop_area = level_data.get('shop_area', {'x': (10, 14), 'y': (5, 8)})
        player_tile_x = int(self.player.x // TILE_SIZE)
        player_tile_y = int(self.player.y // TILE_SIZE)
        if shop_area['x'][0] <= player_tile_x <= shop_area['x'][1] and shop_area['y'][0] <= player_tile_y <= shop_area['y'][1]:
            prompt = self.small_font.render("Press ENTER to shop", True, WHITE)
            self.screen.blit(prompt, (cx - prompt.get_width() // 2, cy + 35))

    def draw_shop_menu(self):
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 200))
        self.screen.blit(overlay, (0, 0))
        
        title = self.title_font.render("SHOP", True, YELLOW)
        self.screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 40))
        
        coins_text = self.font.render(f"Your Coins: {self.coins}", True, YELLOW)
        self.screen.blit(coins_text, (SCREEN_WIDTH // 2 - coins_text.get_width() // 2, 100))
        
        owned_abilities = []
        if self.has_dash:
            owned_abilities.append("DASH")
        if self.has_laser:
            owned_abilities.append("LASER")
        if self.has_shield:
            owned_abilities.append("SHIELD")
        if self.has_wall_breaker:
            owned_abilities.append("WALL BREAKER")
        if self.has_regeneration:
            owned_abilities.append("REGEN")
        if self.has_summon:
            owned_abilities.append("SUMMON")
        if self.has_shadow_army:
            owned_abilities.append("SHADOW ARMY")
        if self.has_cape:
            owned_abilities.append("CAPE")
        
        if owned_abilities:
            owned_text = self.small_font.render(f"Owned: {', '.join(owned_abilities)}", True, (100, 200, 100))
            self.screen.blit(owned_text, (SCREEN_WIDTH // 2 - owned_text.get_width() // 2, 130))
        
        items = [
            {"name": "DASH", "cost": 50, "owned": self.has_dash,
             "desc": "Pass through enemies (E key, 10s cooldown)"},
            {"name": "LASER", "cost": 75, "owned": self.has_laser,
             "desc": "Spawn damaging laser (E key, stays forever)"},
            {"name": "SHIELD", "cost": 100, "owned": self.has_shield,
             "desc": "Deflect bullets 15s (E key, 30s cooldown)"},
            {"name": "WALL BREAKER", "cost": 75, "owned": self.has_wall_breaker,
             "desc": "Break walls in front of you (E key, 30s cooldown)"},
            {"name": "REGENERATION", "cost": 125, "owned": self.has_regeneration,
             "desc": "Heal 1 heart every 20s until hit (E key, 60s cooldown)"},
            {"name": "BIG MORZHAKA", "cost": 200, "owned": self.has_summon,
             "desc": "Summon ally with 20 hearts (E key, 5min cooldown)"},
        ]
        
        y_start = 160
        for i, item in enumerate(items):
            y = y_start + i * 70
            
            if i == self.shop_selection:
                pygame.draw.rect(self.screen, (60, 60, 80), (100, y - 5, SCREEN_WIDTH - 200, 60))
                pygame.draw.rect(self.screen, YELLOW, (100, y - 5, SCREEN_WIDTH - 200, 60), 2)
            
            if item["owned"]:
                name_color = (100, 200, 100)
                status = "[OWNED]"
            elif self.coins >= item["cost"]:
                name_color = WHITE
                status = f"[{item['cost']} coins]"
            else:
                name_color = (150, 150, 150)
                status = f"[{item['cost']} coins - Not enough]"
            
            name_text = self.font.render(item["name"], True, name_color)
            self.screen.blit(name_text, (120, y))
            
            status_text = self.small_font.render(status, True, name_color)
            self.screen.blit(status_text, (SCREEN_WIDTH - 120 - status_text.get_width(), y + 5))
            
            desc_text = self.small_font.render(item["desc"], True, (180, 180, 180))
            self.screen.blit(desc_text, (120, y + 30))
        
        exit_y = y_start + 6 * 70
        exit_color = YELLOW if self.shop_selection == 6 else WHITE
        if self.shop_selection == 6:
            pygame.draw.rect(self.screen, (60, 60, 80), (100, exit_y - 5, SCREEN_WIDTH - 200, 40))
            pygame.draw.rect(self.screen, YELLOW, (100, exit_y - 5, SCREEN_WIDTH - 200, 40), 2)
        exit_text = self.font.render("EXIT SHOP", True, exit_color)
        self.screen.blit(exit_text, (SCREEN_WIDTH // 2 - exit_text.get_width() // 2, exit_y))
        
        controls = self.small_font.render("UP/DOWN: Select | ENTER: Buy | ESC: Exit", True, GRAY)
        self.screen.blit(controls, (SCREEN_WIDTH // 2 - controls.get_width() // 2, SCREEN_HEIGHT - 40))

    def handle_shop_purchase(self):
        if self.shop_selection == 0 and not self.has_dash and self.coins >= 50:
            self.coins -= 50
            self.has_dash = True
            if self.current_ability == 0:
                self.current_ability = 1
        elif self.shop_selection == 1 and not self.has_laser and self.coins >= 75:
            self.coins -= 75
            self.has_laser = True
            if self.current_ability == 0:
                self.current_ability = 2
        elif self.shop_selection == 2 and not self.has_shield and self.coins >= 100:
            self.coins -= 100
            self.has_shield = True
            if self.current_ability == 0:
                self.current_ability = 3
        elif self.shop_selection == 3 and not self.has_wall_breaker and self.coins >= 75:
            self.coins -= 75
            self.has_wall_breaker = True
            if self.current_ability == 0:
                self.current_ability = 4
        elif self.shop_selection == 4 and not self.has_regeneration and self.coins >= 125:
            self.coins -= 125
            self.has_regeneration = True
            if self.current_ability == 0:
                self.current_ability = 5
        elif self.shop_selection == 5 and not self.has_summon and self.coins >= 200:
            self.coins -= 200
            self.has_summon = True
            if self.current_ability == 0:
                self.current_ability = 6
        elif self.shop_selection == 6:
            self.in_shop = False

    def draw_inventory_menu(self):
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 200))
        self.screen.blit(overlay, (0, 0))
        
        title = self.title_font.render("INVENTORY", True, YELLOW)
        self.screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 40))
        
        owned_items = []
        if self.has_dash:
            owned_items.append({"name": "DASH", "id": 1, "color": (150, 100, 50),
                               "desc": "Pass through enemies (E key, 10s cooldown)"})
        if self.has_laser:
            owned_items.append({"name": "LASER", "id": 2, "color": (100, 150, 255),
                               "desc": "Spawn damaging laser (E key, stays forever)"})
        if self.has_shield:
            owned_items.append({"name": "SHIELD", "id": 3, "color": (100, 200, 100),
                               "desc": "Deflect bullets 15s (E key, 30s cooldown)"})
        if self.has_wall_breaker:
            owned_items.append({"name": "WALL BREAKER", "id": 4, "color": (180, 120, 60),
                               "desc": "Break walls in front of you (E key, 30s cooldown)"})
        if self.has_regeneration:
            owned_items.append({"name": "REGENERATION", "id": 5, "color": (255, 100, 150),
                               "desc": "Heal 1 heart every 20s until hit (E key, 60s cooldown)"})
        if self.has_summon:
            owned_items.append({"name": "BIG MORZHAKA", "id": 6, "color": (255, 215, 100),
                               "desc": "Summon ally with 20 hearts (E key, 5min cooldown)"})
        if self.has_shadow_army:
            owned_items.append({"name": "SHADOW ARMY", "id": 7, "color": (140, 140, 180),
                               "desc": "Summon infinite shadow allies (E key, 15s cooldown)"})
        if self.has_cape:
            owned_items.append({"name": "MORZHAKA CAPE", "id": 8, "color": (120, 50, 150),
                               "desc": "Become invincible for 10s (E key, 45s cooldown)"})
        
        if not owned_items:
            no_ability = self.font.render("No abilities owned", True, (150, 150, 150))
            self.screen.blit(no_ability, (SCREEN_WIDTH // 2 - no_ability.get_width() // 2, 180))
            hint = self.small_font.render("Visit the shop in the village to buy abilities!", True, (180, 180, 180))
            self.screen.blit(hint, (SCREEN_WIDTH // 2 - hint.get_width() // 2, 220))
            
            exit_y = 280
            exit_color = YELLOW
            pygame.draw.rect(self.screen, (60, 60, 80), (120, exit_y - 5, SCREEN_WIDTH - 240, 40))
            pygame.draw.rect(self.screen, YELLOW, (120, exit_y - 5, SCREEN_WIDTH - 240, 40), 2)
            exit_text = self.font.render("BACK", True, exit_color)
            self.screen.blit(exit_text, (SCREEN_WIDTH // 2 - exit_text.get_width() // 2, exit_y))
        else:
            if self.ability_slots >= 2:
                current_text = self.font.render("Select ability (E=Slot1, Q=Slot2):", True, WHITE)
            else:
                current_text = self.font.render("Select ability to equip:", True, WHITE)
            self.screen.blit(current_text, (SCREEN_WIDTH // 2 - current_text.get_width() // 2, 100))
            
            max_selection = len(owned_items)
            if self.inventory_selection > max_selection:
                self.inventory_selection = max_selection
            
            y_start = 150
            for i, item in enumerate(owned_items):
                y = y_start + i * 50
                
                if i == self.inventory_selection:
                    pygame.draw.rect(self.screen, (60, 60, 80), (100, y - 5, SCREEN_WIDTH - 200, 45))
                    pygame.draw.rect(self.screen, YELLOW, (100, y - 5, SCREEN_WIDTH - 200, 45), 2)
                
                if self.current_ability == item["id"]:
                    name_color = (100, 255, 100)
                    status = "[SLOT 1 - E]"
                elif self.ability_slots >= 2 and self.second_ability == item["id"]:
                    name_color = (100, 200, 255)
                    status = "[SLOT 2 - Q]"
                else:
                    name_color = item["color"]
                    status = ""
                
                name_text = self.font.render(item["name"], True, name_color)
                self.screen.blit(name_text, (120, y))
                
                if status:
                    status_text = self.small_font.render(status, True, name_color)
                    self.screen.blit(status_text, (SCREEN_WIDTH - 120 - status_text.get_width(), y + 5))
                
                desc_text = self.small_font.render(item["desc"], True, (180, 180, 180))
                self.screen.blit(desc_text, (120, y + 22))
            
            exit_y = y_start + len(owned_items) * 50
            exit_color = YELLOW if self.inventory_selection == len(owned_items) else WHITE
            if self.inventory_selection == len(owned_items):
                pygame.draw.rect(self.screen, (60, 60, 80), (100, exit_y - 5, SCREEN_WIDTH - 200, 40))
                pygame.draw.rect(self.screen, YELLOW, (100, exit_y - 5, SCREEN_WIDTH - 200, 40), 2)
            exit_text = self.font.render("BACK", True, exit_color)
            self.screen.blit(exit_text, (SCREEN_WIDTH // 2 - exit_text.get_width() // 2, exit_y))
        
        if self.ability_slots >= 2:
            controls = self.small_font.render("UP/DOWN: Select | E: Slot 1 | Q: Slot 2 | ESC: Back", True, GRAY)
        else:
            controls = self.small_font.render("UP/DOWN: Select | ENTER: Equip | ESC: Back", True, GRAY)
        self.screen.blit(controls, (SCREEN_WIDTH // 2 - controls.get_width() // 2, SCREEN_HEIGHT - 40))

    def handle_inventory_swap(self, slot=1):
        owned_items = []
        if self.has_dash:
            owned_items.append(1)
        if self.has_laser:
            owned_items.append(2)
        if self.has_shield:
            owned_items.append(3)
        if self.has_wall_breaker:
            owned_items.append(4)
        if self.has_regeneration:
            owned_items.append(5)
        if self.has_summon:
            owned_items.append(6)
        if self.has_shadow_army:
            owned_items.append(7)
        if self.has_cape:
            owned_items.append(8)
        
        if not owned_items:
            self.in_inventory = False
            return
        
        if self.inventory_selection >= len(owned_items):
            self.in_inventory = False
            return
        
        new_ability = owned_items[self.inventory_selection]
        
        if slot == 1:
            if self.second_ability == new_ability:
                self.second_ability = self.current_ability
            if self.current_ability != new_ability:
                self.current_ability = new_ability
                self.player_lasers = []
                self.laser_cooldown = 0
                self.dash_active = False
                self.shield_active = False
                self.ability_cooldown = 0
        elif slot == 2 and self.ability_slots >= 2:
            if self.current_ability == new_ability:
                self.current_ability = self.second_ability
            self.second_ability = new_ability
        
        self.in_inventory = False

    def draw_village_well(self):
        cx = 12 * TILE_SIZE + TILE_SIZE // 2
        cy = 10 * TILE_SIZE + TILE_SIZE // 2
        
        stone_color = (100, 95, 90)
        stone_dark = (70, 65, 60)
        water_color = (60, 100, 140)
        wood_color = (90, 60, 35)
        
        pygame.draw.circle(self.screen, stone_color, (cx, cy), 18)
        pygame.draw.circle(self.screen, stone_dark, (cx, cy), 18, 3)
        pygame.draw.circle(self.screen, water_color, (cx, cy), 12)
        
        pygame.draw.rect(self.screen, wood_color, (cx - 20, cy - 25, 4, 20))
        pygame.draw.rect(self.screen, wood_color, (cx + 16, cy - 25, 4, 20))
        pygame.draw.rect(self.screen, wood_color, (cx - 22, cy - 28, 44, 4))
        
        rope_color = (140, 120, 80)
        pygame.draw.line(self.screen, rope_color, (cx, cy - 26), (cx, cy - 10), 2)

    def draw_door(self, x, y, width, height, door_color, frame_color, locked=False, completed=False):
        pygame.draw.rect(self.screen, frame_color, (x - 3, y - 3, width + 6, height + 6))
        pygame.draw.rect(self.screen, door_color, (x, y, width, height))
        
        darker_color = tuple(max(0, c - 40) for c in door_color)
        lighter_color = tuple(min(255, c + 30) for c in door_color)
        
        pygame.draw.line(self.screen, lighter_color, (x + 2, y + 2), (x + width - 3, y + 2), 2)
        pygame.draw.line(self.screen, lighter_color, (x + 2, y + 2), (x + 2, y + height - 3), 2)
        pygame.draw.line(self.screen, darker_color, (x + width - 3, y + 2), (x + width - 3, y + height - 3), 2)
        pygame.draw.line(self.screen, darker_color, (x + 2, y + height - 3), (x + width - 3, y + height - 3), 2)
        
        if width > height:
            for i in range(3):
                px = x + 8 + i * (width - 16) // 2
                pygame.draw.rect(self.screen, darker_color, (px, y + 6, (width - 20) // 3, height - 12))
        else:
            for i in range(3):
                py = y + 8 + i * (height - 16) // 2
                pygame.draw.rect(self.screen, darker_color, (x + 6, py, width - 12, (height - 20) // 3))
        
        knob_color = (220, 200, 100) if not locked else (80, 80, 80)
        if width > height:
            knob_x = x + width // 2
            knob_y = y + height - 8
        else:
            knob_x = x + width - 8
            knob_y = y + height // 2
        pygame.draw.circle(self.screen, knob_color, (knob_x, knob_y), 5)
        pygame.draw.circle(self.screen, tuple(max(0, c - 40) for c in knob_color), (knob_x, knob_y), 5, 1)
        
        if locked:
            lock_body = (50, 50, 55)
            lock_shackle = (70, 70, 75)
            cx, cy = x + width // 2, y + height // 2
            pygame.draw.rect(self.screen, lock_body, (cx - 8, cy, 16, 12))
            pygame.draw.rect(self.screen, lock_shackle, (cx - 5, cy - 8, 10, 10), 2)
        
        if completed:
            check_color = (80, 220, 80)
            cx, cy = x + width // 2, y + height // 2
            pygame.draw.line(self.screen, check_color, (cx - 10, cy), (cx - 3, cy + 8), 4)
            pygame.draw.line(self.screen, check_color, (cx - 3, cy + 8), (cx + 10, cy - 8), 4)

    def draw_village_doors(self):
        level_data = self.levels[self.current_level]
        doors = level_data.get('doors', {})
        
        if 'castle' in doors:
            door_pos = doors['castle']
            door_x = (door_pos[0] - 2) * TILE_SIZE
            door_y = door_pos[1] * TILE_SIZE - 8
            
            if self.castle_completed:
                door_color = (80, 120, 80)
                frame_color = (50, 80, 50)
            elif self.castle_unlocked:
                door_color = (80, 60, 100)
                frame_color = (50, 40, 70)
            else:
                door_color = (60, 60, 60)
                frame_color = (40, 40, 40)

            self.draw_door(door_x, door_y, TILE_SIZE * 5, TILE_SIZE + 16, door_color, frame_color,
                          locked=not self.castle_unlocked, completed=self.castle_completed)
        
        if 'ice_cave' in doors:
            door_pos = doors['ice_cave']
            door_x = door_pos[0] * TILE_SIZE - 8
            door_y = (door_pos[1] - 1) * TILE_SIZE
            
            if self.ice_cave_completed:
                door_color = (80, 120, 80)
                frame_color = (50, 80, 50)
            elif self.ice_cave_unlocked:
                door_color = (80, 140, 180)
                frame_color = (50, 100, 140)
            else:
                door_color = (60, 60, 60)
                frame_color = (40, 40, 40)
            
            self.draw_door(door_x, door_y, TILE_SIZE + 16, TILE_SIZE * 3, door_color, frame_color,
                          locked=not self.ice_cave_unlocked, completed=self.ice_cave_completed)
        
        if 'dungeon' in doors:
            door_pos = doors['dungeon']
            door_x = door_pos[0] * TILE_SIZE - TILE_SIZE - 8
            door_y = (door_pos[1] - 1) * TILE_SIZE
            
            if self.dungeon_completed:
                door_color = (80, 120, 80)
                frame_color = (50, 80, 50)
            elif self.dungeon_unlocked:
                door_color = (120, 80, 50)
                frame_color = (80, 50, 30)
            else:
                door_color = (60, 60, 60)
                frame_color = (40, 40, 40)
            
            self.draw_door(door_x, door_y, TILE_SIZE + 16, TILE_SIZE * 3, door_color, frame_color, 
                          locked=not self.dungeon_unlocked, completed=self.dungeon_completed)

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
        hardmode_color = YELLOW if self.settings_selection == 2 else WHITE
        back_color = YELLOW if self.settings_selection == 3 else WHITE
        
        volume_pct = int(self.master_volume * 100)
        volume_bar = "=" * (volume_pct // 10) + "-" * (10 - volume_pct // 10)
        volume_text = self.menu_font.render(f"VOLUME: [{volume_bar}] {volume_pct}%", True, volume_color)
        
        fullscreen_status = "ON" if self.is_fullscreen else "OFF"
        fullscreen_text = self.menu_font.render(f"FULLSCREEN: {fullscreen_status}", True, fullscreen_color)
        
        hardmode_status = "ON" if self.hard_mode else "OFF"
        hardmode_text_color = (255, 100, 100) if self.hard_mode else hardmode_color
        hardmode_text = self.menu_font.render(f"HARD MODE: {hardmode_status}", True, hardmode_text_color)
        
        back_text = self.menu_font.render("BACK", True, back_color)
        
        settings_items = [volume_text, fullscreen_text, hardmode_text, back_text]
        settings_y_positions = [150, 210, 270, 330]
        
        arrow_text = self.menu_font.render(">", True, YELLOW)
        self.screen.blit(arrow_text, (SCREEN_WIDTH // 2 - settings_items[self.settings_selection].get_width() // 2 - 40, settings_y_positions[self.settings_selection]))
        
        self.screen.blit(volume_text, (SCREEN_WIDTH // 2 - volume_text.get_width() // 2, 150))
        self.screen.blit(fullscreen_text, (SCREEN_WIDTH // 2 - fullscreen_text.get_width() // 2, 210))
        self.screen.blit(hardmode_text, (SCREEN_WIDTH // 2 - hardmode_text.get_width() // 2, 270))
        self.screen.blit(back_text, (SCREEN_WIDTH // 2 - back_text.get_width() // 2, 330))
        
        if self.hard_mode:
            warning_text = self.small_font.render("Enemies: 2x HP, 2x damage | Bosses: faster | Player: 0.5x damage", True, (255, 150, 150))
            self.screen.blit(warning_text, (SCREEN_WIDTH // 2 - warning_text.get_width() // 2, 390))
        
        controls_text = self.small_font.render("UP/DOWN: select | LEFT/RIGHT: adjust | ENTER/ESC: back", True, GRAY)
        self.screen.blit(controls_text, (SCREEN_WIDTH // 2 - controls_text.get_width() // 2, SCREEN_HEIGHT - 50))

    def draw_pause_menu(self):
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.screen.blit(overlay, (0, 0))

        title_text = self.title_font.render("PAUSED", True, YELLOW)
        title_shadow = self.title_font.render("PAUSED", True, (80, 60, 0))
        self.screen.blit(title_shadow, (SCREEN_WIDTH // 2 - title_text.get_width() // 2 + 3, SCREEN_HEIGHT // 2 - 157))
        self.screen.blit(title_text, (SCREEN_WIDTH // 2 - title_text.get_width() // 2, SCREEN_HEIGHT // 2 - 160))

        resume_color = YELLOW if self.pause_selection == 0 else WHITE
        inventory_color = YELLOW if self.pause_selection == 1 else WHITE
        settings_color = YELLOW if self.pause_selection == 2 else WHITE
        exit_color = YELLOW if self.pause_selection == 3 else WHITE

        resume_text = self.menu_font.render("RESUME", True, resume_color)
        inventory_text = self.menu_font.render("INVENTORY [I]", True, inventory_color)
        settings_text = self.menu_font.render("SETTINGS", True, settings_color)
        exit_text = self.menu_font.render("EXIT", True, exit_color)

        menu_items = [resume_text, inventory_text, settings_text, exit_text]
        menu_y_positions = [SCREEN_HEIGHT // 2 - 60, SCREEN_HEIGHT // 2, SCREEN_HEIGHT // 2 + 60, SCREEN_HEIGHT // 2 + 120]

        arrow_text = self.menu_font.render(">", True, YELLOW)
        self.screen.blit(arrow_text, (SCREEN_WIDTH // 2 - menu_items[self.pause_selection].get_width() // 2 - 40, menu_y_positions[self.pause_selection]))

        self.screen.blit(resume_text, (SCREEN_WIDTH // 2 - resume_text.get_width() // 2, menu_y_positions[0]))
        self.screen.blit(inventory_text, (SCREEN_WIDTH // 2 - inventory_text.get_width() // 2, menu_y_positions[1]))
        self.screen.blit(settings_text, (SCREEN_WIDTH // 2 - settings_text.get_width() // 2, menu_y_positions[2]))
        self.screen.blit(exit_text, (SCREEN_WIDTH // 2 - exit_text.get_width() // 2, menu_y_positions[3]))

        controls_text = self.small_font.render("UP/DOWN: select | ENTER: confirm | I: inventory | ESC: resume", True, GRAY)
        self.screen.blit(controls_text, (SCREEN_WIDTH // 2 - controls_text.get_width() // 2, SCREEN_HEIGHT - 50))

    def draw_paused(self):
        self.screen.fill(BLACK)
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
        
        if self.in_inventory:
            self.draw_inventory_menu()
        elif self.in_settings:
            self.draw_settings()
        else:
            self.draw_pause_menu()
        pygame.display.flip()

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
                            self.settings_selection = (self.settings_selection - 1) % 4
                        elif event.key == pygame.K_DOWN or event.key == pygame.K_s:
                            self.settings_selection = (self.settings_selection + 1) % 4
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
                                self.hard_mode = not self.hard_mode
                            elif self.settings_selection == 3:
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
                    elif self.show_rank_screen:
                        if event.key == pygame.K_SPACE or event.key == pygame.K_RETURN:
                            self.show_rank_screen = False
                            self.rank_screen_data = None
                            if self.pending_ending_cutscene:
                                self.pending_ending_cutscene = False
                                self.start_ending_cutscene()
                            else:
                                self.return_to_village()
                    elif self.in_quest_dialog:
                        if event.key == pygame.K_SPACE or event.key == pygame.K_RETURN:
                            self.handle_quest_dialog_input()
                        elif event.key == pygame.K_ESCAPE:
                            self.in_quest_dialog = False
                    elif self.in_ending_cutscene:
                        if event.key == pygame.K_SPACE or event.key == pygame.K_RETURN:
                            self.advance_ending_cutscene()
                        elif event.key == pygame.K_ESCAPE:
                            self.in_ending_cutscene = False
                            self.castle_completed = True
                            self.return_to_village()
                    elif self.in_shop:
                        if event.key == pygame.K_ESCAPE:
                            self.in_shop = False
                        elif event.key == pygame.K_UP or event.key == pygame.K_w:
                            self.shop_selection = (self.shop_selection - 1) % 7
                        elif event.key == pygame.K_DOWN or event.key == pygame.K_s:
                            self.shop_selection = (self.shop_selection + 1) % 7
                        elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                            self.handle_shop_purchase()
                    elif self.in_inventory:
                        owned_count = sum([self.has_dash, self.has_laser, self.has_shield, self.has_wall_breaker, self.has_regeneration, self.has_summon, self.has_shadow_army, self.has_cape])
                        max_options = owned_count + 1 if owned_count > 0 else 1
                        if event.key == pygame.K_ESCAPE:
                            self.in_inventory = False
                        elif event.key == pygame.K_UP or event.key == pygame.K_w:
                            self.inventory_selection = (self.inventory_selection - 1) % max_options
                        elif event.key == pygame.K_DOWN or event.key == pygame.K_s:
                            self.inventory_selection = (self.inventory_selection + 1) % max_options
                        elif event.key == pygame.K_e:
                            self.handle_inventory_swap(slot=1)
                        elif event.key == pygame.K_q and self.ability_slots >= 2:
                            self.handle_inventory_swap(slot=2)
                        elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                            self.handle_inventory_swap(slot=1)
                    elif self.paused:
                        if event.key == pygame.K_ESCAPE:
                            self.paused = False
                        elif event.key == pygame.K_UP or event.key == pygame.K_w:
                            self.pause_selection = (self.pause_selection - 1) % 4
                        elif event.key == pygame.K_DOWN or event.key == pygame.K_s:
                            self.pause_selection = (self.pause_selection + 1) % 4
                        elif event.key == pygame.K_i:
                            self.in_inventory = True
                            self.inventory_selection = 0
                        elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                            if self.pause_selection == 0:
                                self.paused = False
                            elif self.pause_selection == 1:
                                self.in_inventory = True
                                self.inventory_selection = 0
                            elif self.pause_selection == 2:
                                self.in_settings = True
                                self.settings_selection = 0
                            else:
                                self.running = False
                    else:
                        if event.key == pygame.K_ESCAPE:
                            if not self.game_won and not self.game_over:
                                self.paused = True
                                self.pause_selection = 0
                        elif event.key == pygame.K_p and not self.game_won and not self.game_over and not self.show_rank_screen:
                            level_data = self.levels[self.current_level]
                            if level_data.get('is_dungeon_boss', False):
                                self.dungeon_completed = True
                                self.ice_cave_unlocked = True
                                self.ice_bullet_unlocked = True
                                time_taken = (pygame.time.get_ticks() - self.location_start_time) / 1000
                                self.show_location_rank('dungeon', time_taken)
                            elif level_data.get('is_ice_boss', False):
                                self.ice_cave_completed = True
                                self.castle_unlocked = True
                                self.explosive_bullet_unlocked = True
                                time_taken = (pygame.time.get_ticks() - self.location_start_time) / 1000
                                self.show_location_rank('ice_cave', time_taken)
                            elif level_data.get('is_shadow_boss', False):
                                self.shadow_bullet_unlocked = True
                                self.has_shadow_army = True
                                time_taken = (pygame.time.get_ticks() - self.location_start_time) / 1000
                                self.show_location_rank('castle', time_taken)
                                self.pending_ending_cutscene = True
                            else:
                                self.next_level()
                        elif event.key == pygame.K_e and not self.game_won and not self.game_over:
                            self.activate_ability(slot=1)
                        elif event.key == pygame.K_q and not self.game_won and not self.game_over and self.ability_slots >= 2:
                            self.activate_ability(slot=2)
                        elif event.key == pygame.K_RETURN and not self.game_won and not self.game_over:
                            level_data = self.levels[self.current_level]
                            has_interactions = self.is_village or level_data.get('has_shop', False) or level_data.get('npcs', [])
                            if has_interactions:
                                npc_talked = False
                                for npc in self.npcs:
                                    if npc.is_player_nearby(self.player):
                                        if npc.custom_phrases and npc.custom_phrases[0] == "QUEST_GIVER":
                                            self.in_quest_dialog = True
                                            npc_talked = True
                                        else:
                                            npc.interact()
                                            npc_talked = True
                                        break
                                if not npc_talked:
                                    player_tile_x = int(self.player.x // TILE_SIZE)
                                    player_tile_y = int(self.player.y // TILE_SIZE)
                                    if self.is_village and 10 <= player_tile_x <= 14 and 9 <= player_tile_y <= 11:
                                        self.in_shop = True
                                        self.shop_selection = 0
                                    elif level_data.get('has_shop', False):
                                        shop_area = level_data.get('shop_area', {'x': (10, 14), 'y': (5, 8)})
                                        if shop_area['x'][0] <= player_tile_x <= shop_area['x'][1] and shop_area['y'][0] <= player_tile_y <= shop_area['y'][1]:
                                            self.in_shop = True
                                            self.shop_selection = 0
                        elif event.key == pygame.K_m:
                            self.coins = 99999999999
                        elif event.key == pygame.K_r and (self.game_won or self.game_over):
                            if self.game_won:
                                self.current_level = 0
                                self.checkpoint_level = 0
                                self.ice_bullet_unlocked = False
                                self.explosive_bullet_unlocked = False
                                self.shadow_bullet_unlocked = False
                                self.selected_bullet = 1
                                self.dungeon_unlocked = True
                                self.ice_cave_unlocked = False
                                self.castle_unlocked = False
                                self.dungeon_completed = False
                                self.ice_cave_completed = False
                                self.castle_completed = False
                                self.show_rank_screen = False
                                self.pending_ending_cutscene = False
                                self.best_ranks = {
                                    'dungeon': {'rank': None, 'time': None},
                                    'ice_cave': {'rank': None, 'time': None},
                                    'castle': {'rank': None, 'time': None}
                                }
                                self.is_village = True
                                self.coins = 0
                                self.has_dash = False
                                self.has_laser = False
                                self.has_shield = False
                                self.has_wall_breaker = False
                                self.has_regeneration = False
                                self.has_summon = False
                                self.current_ability = 0
                                self.wall_breaker_cooldown = 0
                                self.regeneration_cooldown = 0
                                self.regeneration_active = False
                                self.regeneration_timer = 0
                                self.summon_cooldown = 0
                                self.summoned_ally = None
                                self.summon_phrase_timer = 0
                                self.ability_cooldown = 0
                                self.dash_active = False
                                self.shield_active = False
                                self.player_lasers = []
                                self.laser_cooldown = 0
                            else:
                                self.current_level = self.checkpoint_level
                            self.dungeon = Dungeon(self.levels[self.current_level], self.current_level + 1)
                            spawn = self.dungeon.spawn_point
                            self.player.x = spawn[0] * TILE_SIZE + 4
                            self.player.y = spawn[1] * TILE_SIZE + 4
                            self.player.health = self.player.max_health
                            self.player.last_direction = (1, 0)
                            self.player.reset_velocity()
                            self.spawn_enemies()
                            self.spawn_npcs()
                            self.projectiles = []
                            self.boss_projectiles = []
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
                            if level_data.get('is_shadow_boss', False):
                                self.play_music(FINAL_BOSS_MUSIC)
                            elif level_data.get('is_boss_level', False):
                                self.play_music(BOSS_MUSIC)
                            elif level_data.get('is_village', False):
                                self.play_music(BACKGROUND_MUSIC)
                            elif location == 3:
                                self.play_music(CASTLE_MUSIC)
                            elif location == 2:
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
            elif self.in_ending_cutscene:
                self.update_ending_cutscene()
                self.draw_ending_cutscene()
                pygame.display.flip()
            elif self.paused:
                self.draw_paused()
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
