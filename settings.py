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


# images

bullet_image = pygame.image.load("assets/image/bullets/bullet.png").convert_alpha()
bullet_image = pygame.transform.scale(bullet_image, BULLET_SIZE)

background_image = pygame.image.load("assets/image/background/2.png").convert_alpha()


# sound effects

bullet_sound = pygame.mixer.Sound("assets/sfx/rifle.mp3")
bg_music = pygame.mixer.Sound("assets/sfx/bg_music.mp3")




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
"Run": {
    "frame_count": 10,  # Number of frames
    "image_path": "assets/image/enemy/Run.png",  # Sprite sheet path
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
"Jump": {
    "frame_count": 10,  # Number of frames
    "image_path": "assets/image/enemy/Jump.png",  # Sprite sheet path
    "animation_cooldown": 100
},

"Reload": {
    "frame_count": 6,  # Number of frames
    "image_path": "assets/image/enemy/Recharge.png",  # Sprite sheet path
    "animation_cooldown": 70
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