import pygame
import sys
import json
from player import Player, bullet_group
from settings import screen, ground_group, enemy_group, background_image, CELL_SIZE
from enemy import Enemy

# Initialize Pygame
pygame.init()

pygame.display.set_caption("Gangster Game")
clock = pygame.time.Clock()

# GAME VARIABLES
bg_scroll_x = 0
bg_scroll_y = 0



def create_map():
    global CELL_SIZE, background_image, bg_images
    
    exit = None
    # Load the level 1 as json file 
    with open("assets/level_1.json") as file:
        maze_layout = json.load(file)
    
    height = len(maze_layout)
    width = len(maze_layout[0])

    # Load the background image
    
    background_image = pygame.transform.scale(background_image, (width * CELL_SIZE, height * CELL_SIZE))
    
    # First create all ground tiles without any offset
    for y, row in enumerate(maze_layout):
        for x, cell in enumerate(row):
            world_x = x * CELL_SIZE
            world_y = y * CELL_SIZE
            
            if cell > 0 and cell <= 6:  # Ground
                ground = Ground(world_x, world_y, cell)
                ground_group.add(ground)
            elif cell == 7:  # Enemy
                enemy = Enemy(world_x, world_y - CELL_SIZE // 2)
                enemy_group.add(enemy)
            elif cell == 8:  # Player
                player.rect.midbottom = (world_x + CELL_SIZE // 2, world_y)  # Center player horizontally
            elif cell == 9:
                exit = Exit(world_x, world_y)
            
    return exit

class Exit(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.image.load("assets/image/map/exit.png")
        self.image = pygame.transform.scale(self.image, (CELL_SIZE, CELL_SIZE * 2))
        self.rect = self.image.get_rect()
        self.x = x
        self.y = y
        self.rect.bottomright = (self.x, self.y - CELL_SIZE)
    
    def update(self):
        self.rect.x = self.x - bg_scroll_x
        self.rect.y = self.y - bg_scroll_y
    
    def draw(self):
        screen.blit(self.image, self.rect)

class Ground(pygame.sprite.Sprite):
    def __init__(self, x, y, image):
        super().__init__()
        self.image = pygame.image.load(f"assets/image/map/{image}.png")
        self.image = pygame.transform.scale(self.image, (CELL_SIZE, CELL_SIZE))
        self.rect = self.image.get_rect()
        self.x = x
        self.y = y
        self.rect.center = (self.x, self.y)
    
    def update(self):
        self.rect.x = self.x - bg_scroll_x
        self.rect.y = self.y - bg_scroll_y
    
    def draw(self):
        screen.blit(self.image, self.rect)


player = Player()


def main():
    global bg_scroll_x, bg_scroll_y
    exit = create_map()
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
                if event.key == pygame.K_r:
                    player.reload()
                    

        # Draw the background
        screen.fill((119,120,121))
        
        # Draw the background image
        screen.blit(background_image, (0 -bg_scroll_x, 0 - bg_scroll_y))
        
        # Update and draw the player
        x, y = player.move(ground_group)
        bg_scroll_x += x
        bg_scroll_y += y        
        player.update()
        player.draw(screen)

        # Update and draw the bullets
        bullet_group.update(ground_group, enemy_group, player)
        bullet_group.draw(screen)

        # Update and draw the ground
        for ground in ground_group:
            ground.update()
            ground.draw()
        
        # Update and draw the exit
        exit.update()
        exit.draw()
        

        # Update and draw the enemy
        for enemy in enemy_group:
            enemy.update()
            enemy.move(player, ground_group)
            enemy.draw(screen, bg_scroll_x, bg_scroll_y)

        # Update the display
        pygame.display.flip()
        clock.tick(60)

if __name__ == "__main__":
    main()
