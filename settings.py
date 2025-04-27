import pygame

pygame.init()
pygame.mixer.init()



VIRTUAL_WIDTH,VIRTUAL_HEIGHT = 800,600

SCREEN_WIDTH, SCREEN_HEIGHT = pygame.display.get_desktop_sizes()[0]


# Scaling Factors
scale_x = SCREEN_WIDTH / VIRTUAL_WIDTH
scale_y = SCREEN_HEIGHT / VIRTUAL_HEIGHT

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

# Constants
BULLET_SIZE = (10 * scale_x, 5 * scale_y)
BULLET_SPEED = 20 * scale_x
PLAYER_SIZE = (70 * scale_x, 80 * scale_x)  # Target size for each frame
SCREEN_THRUST_X = SCREEN_HEIGHT - (200 * scale_x)
SCREEN_THRUST_Y = SCREEN_HEIGHT // (2 * scale_y)
CELL_SIZE = 70 * scale_x   
FPS = 60
ZOOM_VALUE = 1 



# Colors
NEON_BLUE = (0, 255, 255)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
NEON_CYAN = (0, 255, 255)
NEON_PINK = (255, 105, 180)
NEON_YELLOW = (255, 255, 0)



# FONTS
font = pygame.font.Font('assets/font/Pricedown.otf', 25)
big_font = pygame.font.Font("assets/font/Bronx_Bystreets.ttf", 50)

level_font = pygame.font.Font("assets/font/Bronx_Bystreets.ttf", 80)  # Use a tech/street font
start_font = pygame.font.Font("assets/font/Pricedown.otf", 32)
conversation_font = pygame.font.Font("assets/font/Lunar_Escape.otf", 18)

# All Sprite
bullet_group = pygame.sprite.Group()
ground_group = pygame.sprite.Group()
enemy_group = pygame.sprite.Group()
bullet_group = pygame.sprite.Group()
collect_item_group = pygame.sprite.Group()
jumper_group = pygame.sprite.Group()
exit_group = pygame.sprite.Group()
grass_group = pygame.sprite.Group()
ammo_group = pygame.sprite.Group()
plane_group = pygame.sprite.Group()
drop_group = pygame.sprite.Group()
boss_group = pygame.sprite.Group()
acid_group = pygame.sprite.Group()
bomb_group = pygame.sprite.Group()
explosion_group = pygame.sprite.Group()

bg_img_list = []

# images

bullet_image = pygame.image.load("assets/image/bullets/bullet.png").convert_alpha()
for i in range(2,6):
    background_image = pygame.image.load(f"assets/image/background/{i}.png").convert_alpha()
    bg_img_list.append(background_image)
heart_image = pygame.image.load("assets/icons/heart.png").convert_alpha()
bullet_icon = pygame.image.load("assets/icons/bullet.png").convert_alpha()
remaining_bullet_icon = pygame.image.load("assets/icons/remaining_bullet.png").convert_alpha()
remaining_bullet_icon = pygame.transform.scale(remaining_bullet_icon, (25 * scale_x,25 * scale_x))
running_icon = pygame.image.load("assets/icons/running.png").convert_alpha()
running_icon = pygame.transform.scale(running_icon, (25 * scale_x,25 * scale_y))
key_image = pygame.image.load("assets/image/collect_item/key.png").convert_alpha()
key_image = pygame.transform.scale(key_image, (45 * scale_x,35 * scale_y))
drop_image = pygame.image.load("assets/image/background/drop.png").convert_alpha()

# Conversation Images
player_img = pygame.image.load("assets/conversation/player.png").convert_alpha()
player_img = pygame.transform.scale(player_img, (100 * scale_x, 150 * scale_y))

enemy_img = pygame.image.load("assets/conversation/enemy.png").convert_alpha()
enemy_img = pygame.transform.scale(enemy_img, (150 * scale_x, 150 * scale_x))

# Grunge texture overlay

grunge = pygame.image.load("assets/image/background/bg_image.png").convert_alpha()
grunge = pygame.transform.scale(grunge, (SCREEN_WIDTH * ZOOM_VALUE, SCREEN_HEIGHT * ZOOM_VALUE))

bomb_image = pygame.image.load("assets/image/background/bomb.png").convert_alpha()
bomb_image = pygame.transform.scale(bomb_image, (20 * ZOOM_VALUE * scale_x, 30 * ZOOM_VALUE * scale_y))


# sound effects

bullet_sound = pygame.mixer.Sound("assets/sfx/rifle.mp3")
bg_music = pygame.mixer.Sound("assets/sfx/bg_music.mp3")
reload_sound = pygame.mixer.Sound("assets/sfx/reload.mp3")
empty_mag_sound = pygame.mixer.Sound("assets/sfx/empty_gun.mp3")
health_pickup_sound = pygame.mixer.Sound("assets/sfx/health_pickup.mp3")
bullet_pickup_sound = pygame.mixer.Sound("assets/sfx/bullet_pickup.mp3")   
jumper_sound = pygame.mixer.Sound("assets/sfx/jumper.mp3")
select_sound = pygame.mixer.Sound("assets/sfx/select.mp3")
starting_sound = pygame.mixer.Sound("assets/sfx/starting_music.mp3")
death_sound = pygame.mixer.Sound("assets/sfx/death.mp3")
laser_sound = pygame.mixer.Sound("assets/sfx/laser.mp3")
smg_sound = pygame.mixer.Sound("assets/sfx/smg_shot.mp3")
explosion_sound = pygame.mixer.Sound("assets/sfx/explosion_sound.mp3")


# Define animations with frame counts, sprite sheet paths and animation cooldowns
PLAYER_ANIMATION = {
    "idle": {"frame_count": 6, "image_path": "assets/image/player/Idle.png", "animation_cooldown": 70},
    "Run": {"frame_count": 10, "image_path": "assets/image/player/Run.png", "animation_cooldown": 70},
    "Shot": {"frame_count": 4, "image_path": "assets/image/player/Shot.png", "animation_cooldown": 100},
    "Walk": {"frame_count": 10, "image_path": "assets/image/player/Walk.png", "animation_cooldown": 100},
    "Jump": {"frame_count": 10, "image_path": "assets/image/player/Jump.png", "animation_cooldown": 100},
    "Reload": {"frame_count": 17, "image_path": "assets/image/player/Recharge.png", "animation_cooldown": 70},
    "Hurt": {"frame_count": 5, "image_path": "assets/image/player/Hurt.png", "animation_cooldown": 100},
    "Dead": {"frame_count": 5, "image_path": "assets/image/player/Dead.png", "animation_cooldown": 150},
}

ENEMIES = {
    "NORMAL_ENEMY": {
        "idle": {"frame_count": 7, "image_path": "assets/image/enemy/Idle.png", "animation_cooldown": 100},
        "Shot": {"frame_count": 12, "image_path": "assets/image/enemy/Shot.png", "animation_cooldown": 70},
        "Walk": {"frame_count": 10, "image_path": "assets/image/enemy/Walk.png", "animation_cooldown": 100},
        "Hurt": {"frame_count": 4, "image_path": "assets/image/enemy/Hurt.png", "animation_cooldown": 100},
        "Dead": {"frame_count": 5, "image_path": "assets/image/enemy/Dead.png", "animation_cooldown": 100},
    },
    "HEAVY_ENEMY": {
        "idle": {"frame_count": 7, "image_path": "assets/image/enemy2/Idle.png", "animation_cooldown": 100},
        "Shot": {"frame_count": 4, "image_path": "assets/image/enemy2/Shot.png", "animation_cooldown": 100},
        "Walk": {"frame_count": 8, "image_path": "assets/image/enemy2/Walk.png", "animation_cooldown": 100},
        "Hurt": {"frame_count": 4, "image_path": "assets/image/enemy2/Hurt.png", "animation_cooldown": 100},
        "Dead": {"frame_count": 5, "image_path": "assets/image/enemy2/Dead.png", "animation_cooldown": 100},
    },
    "BOSS_ENEMY": {
        "idle": {"frame_count": 4, "image_path": "assets/image/boss/idle.png", "animation_cooldown": 120},
        "Attack1": {"frame_count": 6, "image_path": "assets/image/boss/attack1.png", "animation_cooldown": 80},
        "Attack2": {"frame_count": 8, "image_path": "assets/image/boss/attack2.png", "animation_cooldown": 80},
        "Attack3": {"frame_count": 8, "image_path": "assets/image/boss/attack3.png", "animation_cooldown": 80},
        "Run" : {"frame_count": 6, "image_path": "assets/image/boss/run.png", "animation_cooldown": 100},
        "jump": {"frame_count": 6, "image_path": "assets/image/boss/run_attack.png", "animation_cooldown": 100},
        "Hurt": {"frame_count": 2, "image_path": "assets/image/boss/hurt.png", "animation_cooldown": 90},
        "Dead": {"frame_count": 6, "image_path": "assets/image/boss/death.png", "animation_cooldown": 100},
    }
}


# Player Gun Info

BULLET_INFO = {
"rifle": { "total": 30, "remaining": 20, "mag_size": 20, "bullet_speed": 20, "cooldown" : 100 },
"laser": { "total": 30, "remaining": 20, "mag_size": 20, "bullet_speed": 20, "cooldown" : 200 },
"smg": { "total": 100, "remaining": 30, "mag_size": 30, "bullet_speed": 20, "cooldown" : 5 }
}