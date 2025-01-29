import pygame

pygame.init()

SCREEN_WIDTH,SCREEN_HEIGHT = 800,600

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

# All Sprite
bullet_group = pygame.sprite.Group()
ground_group = pygame.sprite.Group()
enemy_group = pygame.sprite.Group()

# Constants

BULLET_SIZE = (10, 5)
BULLET_SPEED = 20
PLAYER_SIZE = (80, 100)  # Target size for each frame
SCREEN_THRUST_X = SCREEN_HEIGHT - 200
SCREEN_THRUST_Y = SCREEN_HEIGHT // 2



# images

bullet_image = pygame.image.load("assets/bullet.png").convert_alpha()
background_image = pygame.image.load("assets/background.jpg").convert_alpha()

# Define animations with frame counts, sprite sheet paths and animation cooldowns
PLAYER_ANIMATION = {
"idle": {
    "frame_count": 6,  # Number of frames
    "image_path": "assets/player/Idle.png",  # Sprite sheet path,
    "animation_cooldown": 100
},
"Run": {
    "frame_count": 10,  # Number of frames
    "image_path": "assets/player/Run.png",  # Sprite sheet path
    "animation_cooldown": 100
},
"Shot": {
    "frame_count": 4,  # Number of frames
    "image_path": "assets/player/Shot.png",  # Sprite sheet path
    "animation_cooldown": 50
},
"Walk": {
    "frame_count": 10,  # Number of frames
    "image_path": "assets/player/Walk.png",  # Sprite sheet path
    "animation_cooldown": 100
},
"Jump": {
    "frame_count": 10,  # Number of frames
    "image_path": "assets/player/Jump.png",  # Sprite sheet path
    "animation_cooldown": 100
},

"Reload": {
    "frame_count": 17,  # Number of frames
    "image_path": "assets/player/Recharge.png",  # Sprite sheet path
    "animation_cooldown": 70
},
"Hurt": {
    "frame_count": 5,  # Number of frames
    "image_path": "assets/player/Hurt.png",  # Sprite sheet path
    "animation_cooldown": 100
},
}