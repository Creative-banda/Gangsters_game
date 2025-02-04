import pygame

pygame.init()
pygame.mixer.init()



SCREEN_WIDTH,SCREEN_HEIGHT = 800,600

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

# Constants
BULLET_SIZE = (10, 5)
BULLET_SPEED = 20
PLAYER_SIZE = (70, 80)  # Target size for each frame
SCREEN_THRUST_X = SCREEN_HEIGHT - 200
SCREEN_THRUST_Y = SCREEN_HEIGHT // 2
CELL_SIZE = 70


# All Sprite
bullet_group = pygame.sprite.Group()
ground_group = pygame.sprite.Group()
enemy_group = pygame.sprite.Group()
bullet_group = pygame.sprite.Group()
collect_item_group = pygame.sprite.Group()
jumper_group = pygame.sprite.Group()
exit_group = pygame.sprite.Group()
grass_group = pygame.sprite.Group()

# images

bullet_image = pygame.image.load("assets/image/bullets/bullet.png").convert_alpha()
bullet_image = pygame.transform.scale(bullet_image, BULLET_SIZE)
background_image = pygame.image.load("assets/image/background/2.png").convert_alpha()
heart_image = pygame.image.load("assets/icons/heart.png").convert_alpha()
bullet_icon = pygame.image.load("assets/icons/bullet.png").convert_alpha()
remaining_bullet_icon = pygame.image.load("assets/icons/remaining_bullet.png").convert_alpha()
remaining_bullet_icon = pygame.transform.scale(remaining_bullet_icon, (25,25))

# sound effects

bullet_sound = pygame.mixer.Sound("assets/sfx/rifle.mp3")
bg_music = pygame.mixer.Sound("assets/sfx/bg_music.mp3")
reload_sound = pygame.mixer.Sound("assets/sfx/reload.mp3")
empty_mag_sound = pygame.mixer.Sound("assets/sfx/empty_gun.mp3")
health_pickup_sound = pygame.mixer.Sound("assets/sfx/health_pickup.mp3")
bullet_pickup_sound = pygame.mixer.Sound("assets/sfx/bullet_pickup.mp3")    




# Define animations with frame counts, sprite sheet paths and animation cooldowns
PLAYER_ANIMATION = {
"idle": {
    "frame_count": 6,  # Number of frames
    "image_path": "assets/image/player/Idle.png",  # Sprite sheet path,
    "animation_cooldown": 100
},
"Run": {
    "frame_count": 10,  # Number of frames
    "image_path": "assets/image/player/Run.png",  # Sprite sheet path
    "animation_cooldown": 100
},
"Shot": {
    "frame_count": 4,  # Number of frames
    "image_path": "assets/image/player/Shot.png",  # Sprite sheet path
    "animation_cooldown": 100
},
"Walk": {
    "frame_count": 10,  # Number of frames
    "image_path": "assets/image/player/Walk.png",  # Sprite sheet path
    "animation_cooldown": 100
},
"Jump": {
    "frame_count": 10,  # Number of frames
    "image_path": "assets/image/player/Jump.png",  # Sprite sheet path
    "animation_cooldown": 100
},

"Reload": {
    "frame_count": 17,  # Number of frames
    "image_path": "assets/image/player/Recharge.png",  # Sprite sheet path
    "animation_cooldown": 70
},
"Hurt": {
    "frame_count": 5,  # Number of frames
    "image_path": "assets/image/player/Hurt.png",  # Sprite sheet path
    "animation_cooldown": 100
},
"Dead": {
    "frame_count": 5,  # Number of frames
    "image_path": "assets/image/player/Dead.png",  # Sprite sheet path
    "animation_cooldown": 150
},
}

ENEMY_ANIMATION = {
"idle": {
    "frame_count": 7,  # Number of frames
    "image_path": "assets/image/enemy/Idle.png",  # Sprite sheet path,
    "animation_cooldown": 100
},
"Shot": {
    "frame_count": 12,  # Number of frames
    "image_path": "assets/image/enemy/Shot.png",  # Sprite sheet path
    "animation_cooldown": 70
},
"Walk": {
    "frame_count": 10,  # Number of frames
    "image_path": "assets/image/enemy/Walk.png",  # Sprite sheet path
    "animation_cooldown": 100
},
"Hurt": {
    "frame_count": 4,  # Number of frames
    "image_path": "assets/image/enemy/Hurt.png",  # Sprite sheet path
    "animation_cooldown": 100
},

"Dead": {
    "frame_count": 5,  # Number of frames
    "image_path": "assets/image/enemy/Dead.png",  # Sprite sheet path
    "animation_cooldown": 100
},
}

# Player Gun Info

BULLET_INFO = {
"rifle": {
    "total": 30,
    "remaining": 3,
    "mag_size": 20,
    "bullet_damage": 10,
    "bullet_speed": 20
},
}