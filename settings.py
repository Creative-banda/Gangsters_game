import pygame

pygame.init()

SCREEN_WIDTH,SCREEN_HEIGHT = 800,600

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

# All Sprite
bullet_group = pygame.sprite.Group()
ground_group = pygame.sprite.Group()

# Constants

BULLET_SIZE = (20, 10)
BULLET_SPEED = 20
PLAYER_SIZE = (80, 90)  # Target size for each frame
SCREEN_THRUST = SCREEN_WIDTH // 2



# images

bullet_image = pygame.image.load("assets/bullet.png").convert_alpha()
