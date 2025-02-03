import pygame
import sys
import json
from player import Player, bullet_group
from settings import *
from enemy import Enemy

# Initialize Pygame
pygame.init()

pygame.display.set_caption("Gangster Game")
clock = pygame.time.Clock()

# GAME VARIABLES
bg_scroll_x = 0
bg_scroll_y = 0
isfading = False

font = pygame.font.Font('assets/font/Pricedown.otf', 25)
big_font = pygame.font.Font("assets/font/Pricedown.otf", 50)

# play background music

bg_music.play(-1)

isDeathSoundPlay = False

 # Create a surface for the fade out
outro_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
outro_surface.fill((220, 20, 60))

# Create a surface for the fade in

intro_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
intro_surface.fill((0, 200, 255))  # Neon Cyan

fade_alpha = 255

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
            elif cell == 10:
                collect_item = CollectItem(world_x, world_y, "health", "health")
                collect_item_group.add(collect_item)
            elif cell == 11:
                collect_item = CollectItem(world_x, world_y, "rifle_ammo", "ammo")
                collect_item_group.add(collect_item)
            
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


class CollectItem(pygame.sprite.Sprite):
    def __init__(self, x, y, image, type):
        super().__init__()
        self.image = pygame.image.load(f"assets/image/collect_item/{image}.png")
        self.image = pygame.transform.scale(self.image, (CELL_SIZE // 2 - 10, CELL_SIZE // 2))
        self.rect = self.image.get_rect()
        self.x = x
        self.y = y + CELL_SIZE // 2
        self.rect.center = (self.x, self.y)
        self.type = type
    
    def update(self):
        self.rect.x = self.x - bg_scroll_x
        self.rect.y = self.y - bg_scroll_y
    
    def draw(self):
        screen.blit(self.image, self.rect)
        # pygame.draw.rect(screen, (255, 0, 0), self.rect, 1)
    
    def collect(self):
        if self.type == "health" and player.health < 100:
            player.health = min(player.health + 20, 100)
            collect_item_group.remove(self)
            health_pickup_sound.play()
        elif self.type == "ammo":
            BULLET_INFO[player.current_gun]['total'] += 10
            collect_item_group.remove(self)
            bullet_pickup_sound.play()


# Fade Out Screen Transition

def fade_outro():
    global fade_alpha, isDeathSoundPlay
    if fade_alpha < 255:  # Increase opacity over time
        fade_alpha += 2
    outro_surface.set_alpha(fade_alpha)
    screen.blit(outro_surface, (0, 0))

    if fade_alpha >= 255:
        #display game over screen
        text = big_font.render("Wasted ", True, (255, 255, 255))
        text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        restart_text = font.render("Met your fate ? Press R to rise again !", True, (255, 255, 255))
        restart_rect = restart_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50))
        screen.blit(text, text_rect)
        screen.blit(restart_text, restart_rect)


def fade_intro():
    global fade_alpha
    if fade_alpha > 0:  # Increase opacity over time
        fade_alpha -= 5
    intro_surface.set_alpha(fade_alpha)
    screen.blit(intro_surface, (0, 0))


player = Player()


def main():
    global bg_scroll_x, bg_scroll_y, isDeathSoundPlay, fade_alpha

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
                if event.key == pygame.K_r and player.alive:
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

        # Update and draw the collect items
        for collect_item in collect_item_group:
            collect_item.update()
            collect_item.draw()
            if player.rect.colliderect(collect_item.rect):
                collect_item.collect()


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
        
        # Display HUD        
        current_ammo = BULLET_INFO[player.current_gun]['remaining'] if BULLET_INFO[player.current_gun]['remaining'] > 0 else "No Ammo"
        text = font.render(f"{current_ammo}", True, (255, 255, 255))
        screen.blit(text, (40, 50))
        screen.blit(bullet_icon, (15, 52))

        remaining_ammo = BULLET_INFO[player.current_gun]['total'] if BULLET_INFO[player.current_gun]['total'] > 0 else "No Ammo"
        text = font.render(f"{remaining_ammo}", True, (255, 255, 255))
        screen.blit(text, (40, 90))
        screen.blit(remaining_bullet_icon, (10, 92))
                        
        # player health
        player.health_bar.width = player.health_ratio * player.health
        
        # Text for health
        screen.blit(heart_image, (10, 10))
        
        pygame.draw.rect(screen, (0, 255, 0), player.health_bar)
        pygame.draw.rect(screen, (255, 0, 0), player.health_bar, 2)
        
        if not player.alive:
            fade_outro()
            if not isDeathSoundPlay:
                # fade out the background music
                pygame.mixer.Sound.stop(bg_music)
                isDeathSoundPlay = True
                pygame.mixer.Sound("assets/sfx/death.mp3").play()

        else:
            fade_intro()
        
        if not player.alive:
            # Look for the R key to restart the game
            keys = pygame.key.get_pressed()
            if keys[pygame.K_r]:
                fade_alpha = 0
                isDeathSoundPlay = False
                bg_music.play(-1)
                # Reset the game
                enemy_group.empty()
                collect_item_group.empty()
                ground_group.empty()
                bullet_group.empty()
                player.alive = True
                player.health = 100
                exit = create_map()


        # Update the display
        pygame.display.flip()
        clock.tick(60)

if __name__ == "__main__":
    main()
