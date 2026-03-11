import pygame
from constants import PIXEL_SIZE, BOSS_PIXEL_SIZE, FINAL_BOSS_PIXEL_SIZE, SHADOW_BOSS_PIXEL_SIZE


def create_player_sprites():
    """Create pixel art character sprites with walking animation frames."""
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
    """Create enemy sprite - same design as player but with red skin."""
    sprite_data = [
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
    
    red_skin = (200, 60, 60)
    dark_eyes = (40, 40, 40)
    white_body = (245, 245, 240)
    dark_red_accent = (139, 30, 30)
    dark_boots = (80, 40, 40)
    
    colors = {
        1: red_skin,
        2: dark_eyes,
        3: white_body,
        5: dark_red_accent,
        6: dark_boots
    }
    
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
    
    return sprite


def create_ice_enemy_sprite():
    """Create ice enemy sprite - same design as player but with blue skin."""
    sprite_data = [
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
    
    ice_blue_skin = (100, 180, 255)
    dark_eyes = (40, 40, 40)
    white_body = (245, 245, 240)
    dark_blue_accent = (50, 100, 150)
    ice_boots = (70, 130, 180)
    
    colors = {
        1: ice_blue_skin,
        2: dark_eyes,
        3: white_body,
        5: dark_blue_accent,
        6: ice_boots
    }
    
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
    
    return sprite


def create_castle_enemy_fast_sprite():
    """Create light gray fast castle enemy sprite."""
    sprite_data = [
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
    
    light_gray_skin = (180, 180, 185)
    dark_eyes = (30, 30, 30)
    gray_body = (150, 150, 155)
    dark_gray_accent = (100, 100, 105)
    gray_boots = (120, 120, 125)
    
    colors = {
        1: light_gray_skin,
        2: dark_eyes,
        3: gray_body,
        5: dark_gray_accent,
        6: gray_boots
    }
    
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
    
    return sprite


def create_castle_enemy_shooter_sprite():
    """Create dark gray shooter castle enemy sprite."""
    sprite_data = [
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
    
    dark_gray_skin = (70, 70, 75)
    dark_eyes = (20, 20, 20)
    darker_body = (50, 50, 55)
    black_accent = (30, 30, 35)
    dark_boots = (40, 40, 45)
    
    colors = {
        1: dark_gray_skin,
        2: dark_eyes,
        3: darker_body,
        5: black_accent,
        6: dark_boots
    }
    
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
    
    return sprite


def create_boss_sprite():
    """Create boss sprite - same design as player but 3x bigger with dark red skin."""
    sprite_data = [
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
    
    dark_red_skin = (139, 0, 0)
    dark_eyes = (20, 20, 20)
    dark_body = (60, 60, 60)
    black_accent = (30, 0, 0)
    dark_boots = (50, 20, 20)
    
    colors = {
        1: dark_red_skin,
        2: dark_eyes,
        3: dark_body,
        5: black_accent,
        6: dark_boots
    }
    
    width = len(sprite_data[0]) * BOSS_PIXEL_SIZE
    height = len(sprite_data) * BOSS_PIXEL_SIZE
    
    sprite = pygame.Surface((width, height), pygame.SRCALPHA)
    
    for y, row in enumerate(sprite_data):
        for x, pixel in enumerate(row):
            if pixel in colors:
                pygame.draw.rect(
                    sprite, colors[pixel],
                    (x * BOSS_PIXEL_SIZE, y * BOSS_PIXEL_SIZE, BOSS_PIXEL_SIZE, BOSS_PIXEL_SIZE)
                )
    
    return sprite


def create_ice_boss_sprite():
    """Create purple boss sprite for ice caves."""
    sprite_data = [
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

    purple_skin = (148, 80, 200)
    dark_eyes = (20, 20, 30)
    purple_body = (100, 50, 140)
    dark_purple_accent = (80, 40, 120)
    purple_boots = (120, 60, 160)

    colors = {
        1: purple_skin,
        2: dark_eyes,
        3: purple_body,
        5: dark_purple_accent,
        6: purple_boots
    }
    
    width = len(sprite_data[0]) * BOSS_PIXEL_SIZE
    height = len(sprite_data) * BOSS_PIXEL_SIZE
    sprite = pygame.Surface((width, height), pygame.SRCALPHA)
    
    for y, row in enumerate(sprite_data):
        for x, pixel in enumerate(row):
            if pixel in colors:
                pygame.draw.rect(
                    sprite, colors[pixel],
                    (x * BOSS_PIXEL_SIZE, y * BOSS_PIXEL_SIZE, BOSS_PIXEL_SIZE, BOSS_PIXEL_SIZE)
                )
    
    return sprite


def create_final_boss_sprite():
    """Create final boss sprite - same design as player but 4x bigger with purple skin."""
    sprite_data = [
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
    
    purple_skin = (148, 0, 211)
    dark_eyes = (20, 20, 20)
    dark_body = (40, 20, 60)
    dark_purple_accent = (75, 0, 130)
    purple_boots = (100, 0, 150)
    
    colors = {
        1: purple_skin,
        2: dark_eyes,
        3: dark_body,
        5: dark_purple_accent,
        6: purple_boots
    }
    
    width = len(sprite_data[0]) * FINAL_BOSS_PIXEL_SIZE
    height = len(sprite_data) * FINAL_BOSS_PIXEL_SIZE
    
    sprite = pygame.Surface((width, height), pygame.SRCALPHA)
    
    for y, row in enumerate(sprite_data):
        for x, pixel in enumerate(row):
            if pixel in colors:
                pygame.draw.rect(
                    sprite, colors[pixel],
                    (x * FINAL_BOSS_PIXEL_SIZE, y * FINAL_BOSS_PIXEL_SIZE, FINAL_BOSS_PIXEL_SIZE, FINAL_BOSS_PIXEL_SIZE)
                )
    
    return sprite


def create_shadow_boss_sprite():
    """Create Shadow Byako sprite - black cat with cape."""
    sprite_data = [
        [0, 4, 0, 0, 0, 0, 0, 4, 0],
        [4, 4, 0, 0, 0, 0, 0, 4, 4],
        [4, 1, 0, 1, 1, 1, 0, 1, 4],
        [0, 1, 1, 1, 1, 1, 1, 1, 0],
        [5, 1, 2, 1, 1, 1, 2, 1, 5],
        [5, 1, 1, 1, 3, 1, 1, 1, 5],
        [5, 5, 1, 1, 1, 1, 1, 5, 5],
        [5, 5, 1, 1, 1, 1, 1, 5, 5],
        [5, 5, 5, 1, 1, 1, 5, 5, 5],
        [0, 5, 5, 1, 1, 1, 5, 5, 0],
        [0, 0, 5, 5, 0, 5, 5, 0, 0],
    ]

    black_body = (5, 5, 5)
    black_eyes = (0, 0, 0)
    black_nose = (0, 0, 0)
    black_ears = (0, 0, 0)
    black_cape = (0, 0, 0)

    colors = {
        1: black_body,
        2: black_eyes,
        3: black_nose,
        4: black_ears,
        5: black_cape
    }

    width = len(sprite_data[0]) * SHADOW_BOSS_PIXEL_SIZE
    height = len(sprite_data) * SHADOW_BOSS_PIXEL_SIZE
    sprite = pygame.Surface((width, height), pygame.SRCALPHA)

    for y, row in enumerate(sprite_data):
        for x, pixel in enumerate(row):
            if pixel in colors:
                pygame.draw.rect(
                    sprite, colors[pixel],
                    (x * SHADOW_BOSS_PIXEL_SIZE, y * SHADOW_BOSS_PIXEL_SIZE,
                     SHADOW_BOSS_PIXEL_SIZE, SHADOW_BOSS_PIXEL_SIZE)
                )

    return sprite


def create_summoned_ally_sprite():
    """Create Morzhaka ally sprite - same size as player with golden color and funny eyebrows."""
    sprite_data = [
        [0, 0, 5, 1, 1, 1, 5, 0, 0],
        [0, 7, 1, 5, 1, 5, 1, 7, 0],
        [7, 2, 2, 1, 1, 1, 2, 2, 7],
        [1, 2, 3, 1, 1, 1, 2, 3, 1],
        [5, 1, 1, 1, 2, 1, 1, 1, 5],
        [1, 3, 2, 2, 2, 2, 2, 1, 1],
        [3, 3, 2, 3, 3, 3, 2, 3, 3],
        [3, 3, 3, 2, 3, 2, 3, 3, 3],
        [0, 3, 3, 3, 3, 3, 3, 3, 0],
        [0, 3, 6, 0, 0, 0, 6, 3, 0],
        [3, 5, 3, 0, 0, 0, 3, 5, 3],
    ]

    golden_skin = (255, 215, 120)
    golden_eyes = (180, 140, 60)
    white_body = (255, 255, 245)
    golden_accent = (220, 180, 80)
    golden_boots = (200, 160, 70)
    eyebrow_color = (80, 50, 20)

    colors = {
        1: golden_skin,
        2: golden_eyes,
        3: white_body,
        5: golden_accent,
        6: golden_boots,
        7: eyebrow_color
    }

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

    return sprite


def create_npc_sprite(hat_type='wizard'):
    """Create NPC sprite - same as player but with a hat on top."""
    sprite_data = [
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
    
    tan_skin = (212, 184, 150)
    dark_blue_eyes = (26, 74, 110)
    white_body = (245, 245, 240)
    brown_accent = (139, 105, 20)
    light_blue = (135, 180, 220)
    
    colors = {
        1: tan_skin,
        2: dark_blue_eyes,
        3: white_body,
        5: brown_accent,
        6: light_blue
    }
    
    hat_height = 6
    width = len(sprite_data[0]) * PIXEL_SIZE
    height = len(sprite_data) * PIXEL_SIZE + hat_height * PIXEL_SIZE
    
    sprite = pygame.Surface((width, height), pygame.SRCALPHA)
    
    hat_offset_y = hat_height * PIXEL_SIZE
    
    for y, row in enumerate(sprite_data):
        for x, pixel in enumerate(row):
            if pixel in colors:
                pygame.draw.rect(
                    sprite, colors[pixel],
                    (x * PIXEL_SIZE, y * PIXEL_SIZE + hat_offset_y, PIXEL_SIZE, PIXEL_SIZE)
                )
    
    P = PIXEL_SIZE
    
    if hat_type == 'wizard':
        hat_color = (80, 60, 140)
        hat_light = (120, 100, 180)
        star_color = (255, 220, 100)
        
        points = [
            (4 * P, 0),
            (0, 6 * P),
            (9 * P, 6 * P)
        ]
        pygame.draw.polygon(sprite, hat_color, points)
        pygame.draw.rect(sprite, hat_light, (0, 5 * P, 9 * P, 2 * P))
        pygame.draw.rect(sprite, star_color, (3 * P, 2 * P, 2 * P, 2 * P))
        pygame.draw.rect(sprite, star_color, (4 * P, P, P, P))
        
    elif hat_type == 'farmer':
        hat_color = (180, 150, 80)
        hat_dark = (140, 110, 50)
        straw_color = (220, 200, 100)
        
        pygame.draw.rect(sprite, hat_color, (P, 3 * P, 7 * P, 3 * P))
        pygame.draw.rect(sprite, hat_dark, (0, 5 * P, 9 * P, 2 * P))
        pygame.draw.rect(sprite, straw_color, (7 * P, 4 * P, 3 * P, P))
        
    elif hat_type == 'top_hat':
        hat_color = (30, 30, 35)
        hat_light = (60, 60, 70)
        band_color = (150, 50, 50)
        
        pygame.draw.rect(sprite, hat_color, (P, 0, 7 * P, 6 * P))
        pygame.draw.rect(sprite, hat_light, (0, 5 * P, 9 * P, 2 * P))
        pygame.draw.rect(sprite, band_color, (P, 3 * P, 7 * P, P))
    
    elif hat_type == 'miner':
        hat_color = (180, 140, 60)
        hat_dark = (140, 100, 40)
        lamp_color = (255, 255, 150)
        lamp_glow = (255, 200, 50)
        
        pygame.draw.rect(sprite, hat_color, (P, 2 * P, 7 * P, 4 * P))
        pygame.draw.rect(sprite, hat_dark, (0, 5 * P, 9 * P, 2 * P))
        pygame.draw.rect(sprite, lamp_glow, (3 * P, P, 3 * P, 2 * P))
        pygame.draw.rect(sprite, lamp_color, (4 * P, P, P, P))
    
    elif hat_type == 'pirate':
        hat_color = (40, 40, 45)
        skull_color = (230, 230, 230)
        bone_color = (200, 200, 200)
        
        pygame.draw.rect(sprite, hat_color, (0, 3 * P, 9 * P, 4 * P))
        pygame.draw.polygon(sprite, hat_color, [(P, 3 * P), (4 * P, 0), (8 * P, 3 * P)])
        pygame.draw.rect(sprite, skull_color, (3 * P, 4 * P, 3 * P, 2 * P))
        pygame.draw.rect(sprite, bone_color, (2 * P, 5 * P, P, P))
        pygame.draw.rect(sprite, bone_color, (6 * P, 5 * P, P, P))
    
    elif hat_type == 'knight':
        helmet_color = (140, 140, 150)
        helmet_light = (180, 180, 190)
        visor_color = (40, 40, 50)
        
        pygame.draw.rect(sprite, helmet_color, (P, 0, 7 * P, 7 * P))
        pygame.draw.rect(sprite, helmet_light, (2 * P, P, 5 * P, 2 * P))
        pygame.draw.rect(sprite, visor_color, (2 * P, 4 * P, 5 * P, P))
        pygame.draw.rect(sprite, helmet_light, (4 * P, 0, P, P))
    
    elif hat_type == 'ice_crown':
        ice_color = (150, 200, 255)
        ice_light = (200, 230, 255)
        ice_dark = (100, 150, 200)
        
        pygame.draw.rect(sprite, ice_color, (P, 3 * P, 7 * P, 3 * P))
        pygame.draw.rect(sprite, ice_light, (2 * P, P, P, 3 * P))
        pygame.draw.rect(sprite, ice_light, (4 * P, 0, P, 4 * P))
        pygame.draw.rect(sprite, ice_light, (6 * P, P, P, 3 * P))
        pygame.draw.rect(sprite, ice_dark, (0, 5 * P, 9 * P, P))
    
    return sprite


def create_shadow_enemy_sprite(is_light=True):
    """Create shadow minion sprite - similar to castle enemies but gray."""
    sprite_data = [
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

    if is_light:
        skin = (200, 200, 205)
        eyes = (20, 20, 20)
        body = (170, 170, 175)
        accent = (130, 130, 135)
        boots = (150, 150, 155)
    else:
        skin = (70, 70, 75)
        eyes = (220, 220, 220)
        body = (50, 50, 55)
        accent = (35, 35, 40)
        boots = (45, 45, 50)

    colors = {
        1: skin,
        2: eyes,
        3: body,
        5: accent,
        6: boots
    }

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

    return sprite
