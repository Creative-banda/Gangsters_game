import pygame

pygame.init()

SCREEN_WIDTH,SCREEN_HEIGHT = 800,600

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

# All Sprite
bullet_group = pygame.sprite.Group()
ground_group = pygame.sprite.Group()
enemy_group = pygame.sprite.Group()
bullet_group = pygame.sprite.Group()


# images

bullet_image = pygame.image.load("assets/image/bullet.png").convert_alpha()

background_image = pygame.image.load("assets/image/background/2.png").convert_alpha()


# Constants

BULLET_SIZE = (10, 5)
BULLET_SPEED = 20
PLAYER_SIZE = (20, 30)  # Target size for each frame
SCREEN_THRUST_X = SCREEN_HEIGHT - 200
SCREEN_THRUST_Y = SCREEN_HEIGHT // 2
CELL_SIZE = 20


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
    "animation_cooldown": 50
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