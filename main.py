import pygame
import sys
import json
from player import Player, bullet_group
from settings import screen, ground_group

# Initialize Pygame
pygame.init()


pygame.display.set_caption("Gangster Game")
clock = pygame.time.Clock()


# GAME VARIABLES
bg_scroll_x = 0
bg_scroll_y = 0

def create_map():
    global height, width, CELL_SIZE
    # Load the level 1 as json file 
    with open("assets/level_1.json") as file:
        maze_layout = json.load(file)
    
    height = len(maze_layout)
    width = len(maze_layout[0])
    CELL_SIZE = 40

    
    for y, row in enumerate(maze_layout):
        for x, cell in enumerate(row):
            
            world_x = x * CELL_SIZE
            world_y = y * CELL_SIZE
            
            if cell == 1:  # Ground
                ground = Ground(world_x, world_y)
                ground_group.add(ground)

            if cell == 2:
                player.rect.midbottom = (world_x, world_y)
                player.rect.y -= 30
            
class Ground(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((CELL_SIZE, CELL_SIZE))
        self.image.fill((0, 0, 0))
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
    
    def update(self):
        self.rect.x -= bg_scroll_x
        self.rect.y -=bg_scroll_y

    
player = Player()
create_map()



def main():
    global bg_scroll_x
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
                    

        # Clear the screen with the background color
        screen.fill((255, 155, 155))
        # Update and draw the player
        bg_scroll_x = player.move(ground_group)
        player.update()
        player.draw(screen)

        # Update and draw the bullets
        bullet_group.update(ground_group)
        bullet_group.draw(screen)

        # Update and draw the ground
        ground_group.draw(screen)
        ground_group.update()





        # Update the display
        pygame.display.flip()
        clock.tick(60)


if __name__ == "__main__":
    main()
