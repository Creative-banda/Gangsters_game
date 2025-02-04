import pygame
import sys
import json, random, math
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

# play starting music
starting_sound.play(-1)

font = pygame.font.Font('assets/font/Pricedown.otf', 25)
big_font = pygame.font.Font("assets/font/Pricedown.otf", 50)


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
            
            if cell > 0 and cell <= 45:  # Ground
                if cell >=5 and cell <= 8 or cell == 35:
                    grass = Grass(world_x, world_y, cell)
                    grass_group.add(grass)
                else:
                    ground = Ground(world_x, world_y, cell)
                    ground_group.add(ground)
            elif cell == 46:  # Enemy
                enemy = Enemy(world_x, world_y - CELL_SIZE // 2)
                enemy_group.add(enemy)
            elif cell == 48:
                collect_item = CollectItem(world_x, world_y, "health", "health")
                collect_item_group.add(collect_item)
            elif cell == 49:
                collect_item = CollectItem(world_x, world_y, "key", "key")
                collect_item_group.add(collect_item)
            elif cell == 50:
                collect_item = CollectItem(world_x, world_y, "rifle_ammo", "ammo")
                collect_item_group.add(collect_item)
            elif cell == 51:
                exit = Exit(world_x, world_y)
                exit_group.add(exit)
            elif cell == 52:  # Player
                player.rect.midbottom = (world_x + CELL_SIZE // 2, world_y)  # Center player horizontally
            elif cell == 53:
                jumper = Jumper(world_x, world_y)
                jumper_group.add(jumper)
            

def show_achievement(text, duration=1000):
    """Displays an achievement message at the top of the screen."""
    global achievement_text, achievement_alpha, achievement_timer
    achievement_text = text
    achievement_alpha = 255  # Fully visible
    achievement_timer = pygame.time.get_ticks() + duration

def draw_achievement():
    """Renders the achievement text with fade effect."""
    global achievement_alpha, achievement_text
    if achievement_text:
        if pygame.time.get_ticks() > achievement_timer:
            achievement_alpha -= 5  # Gradual fade-out
            if achievement_alpha <= 0:
                achievement_text = ""

        # Render text
        if achievement_text:
            text_surface = font.render(achievement_text, True, NEON_BLUE)
            text_surface.set_alpha(achievement_alpha)  # Apply fade effect
            screen.blit(text_surface, (SCREEN_WIDTH // 2 - text_surface.get_width() // 2, 50))



class Exit(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.image.load("assets/image/new_map/exit.png")
        self.image = pygame.transform.scale(self.image, (CELL_SIZE, CELL_SIZE))
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
        self.image = pygame.image.load(f"assets/image/new_map/Tile_{image}.png")
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


class Grass(pygame.sprite.Sprite):
    def __init__(self, x, y, image):
        super().__init__()
        self.image = pygame.image.load(f"assets/image/new_map/Tile_{image}.png")
        self.image = pygame.transform.scale(self.image, (CELL_SIZE // 2, CELL_SIZE // 2))
        self.rect = self.image.get_rect()
        self.x = x + CELL_SIZE // 2
        self.y = y + CELL_SIZE // 2 
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
            show_achievement("Health +20")
        elif self.type == "ammo":
            BULLET_INFO[player.current_gun]['total'] += 10
            collect_item_group.remove(self)
            bullet_pickup_sound.play()
            show_achievement("Ammo +10")
        elif self.type == "key":
            player.has_key = True
            health_pickup_sound.play()
            collect_item_group.remove(self)
            show_achievement("Key Collected !")


class Jumper(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.image.load("assets/image/new_map/jumper.png")
        self.image = pygame.transform.scale(self.image, (20,20))
        self.rect = self.image.get_rect()
        self.x = x
        self.y = y + CELL_SIZE // 2 + 15
        self.rect.center = (self.x, self.y)

    def update(self):
        self.rect.x = self.x - bg_scroll_x
        self.rect.y =self.y - bg_scroll_y
    

    def checkCollision(self, player):
        if self.rect.colliderect(player.rect):
            player.inAir = True
            player.vel_y = -22
            jumper_sound.play()


    def draw(self, screen):
        screen.blit(self.image, (self.rect.x, self.rect.y))


def DisplayLevel():
    start_alpha = 0
    flicker_timer = 0
    neon_hue = 0
    smoke_particles = []
    clock = pygame.time.Clock()

    # Generate smoke particles
    for _ in range(30):
        smoke_particles.append({
            'pos': [random.randint(0, SCREEN_WIDTH), SCREEN_HEIGHT//2 + 100],
            'speed': random.uniform(0.3, 0.7),
            'size': random.randint(10, 30),
            'alpha': random.randint(50, 150)
        })

    while True:
        dt = clock.tick(60) / 1000
        screen.fill((10, 10, 15))  # Dark base color
        
        # Draw neon grid background
        grid_color = (30, 30, 40)
        for x in range(0, SCREEN_WIDTH, 40):
            pygame.draw.line(screen, grid_color, (x, 0), (x, SCREEN_HEIGHT), 1)
        for y in range(0, SCREEN_HEIGHT, 40):
            pygame.draw.line(screen, grid_color, (0, y), (SCREEN_WIDTH, y), 1)
            
        # Animated smoke particles
        for p in smoke_particles:
            smoke_surface = pygame.Surface((p['size'], p['size']), pygame.SRCALPHA)
            pygame.draw.circle(smoke_surface, (50, 50, 50, p['alpha']), 
                             (p['size']//2, p['size']//2), p['size']//2)
            screen.blit(smoke_surface, (int(p['pos'][0]), int(p['pos'][1])))
            p['pos'][0] += random.uniform(-0.5, 0.5)
            p['pos'][1] -= p['speed']
            if p['pos'][1] < -50:
                p.update({
                    'pos': [random.randint(0, SCREEN_WIDTH), SCREEN_HEIGHT + 50],
                    'speed': random.uniform(0.3, 0.7),
                    'size': random.randint(10, 30),
                    'alpha': random.randint(50, 150)
                })

        # Neon frame decoration
        pygame.draw.rect(screen, (255, 40, 120), (0, 0, SCREEN_WIDTH, SCREEN_HEIGHT), 4)
        pygame.draw.rect(screen, (40, 255, 200), (4, 4, SCREEN_WIDTH-8, SCREEN_HEIGHT-8), 2)

        # Level text with neon flicker
        flicker_timer += dt
        neon_intensity = 200 + int(55 * abs(math.sin(flicker_timer * 3)))
        level_font = pygame.font.Font("assets/font/INFECTED.ttf", 80)  # Use a tech/street font
        level_text = level_font.render("CITY GANG", True, (255, 40, 120))
        
        # Neon glow effect
        for i in range(5, 0, -1):
            glow_text = level_font.render("CITY GANG", True, 
                                        (255, 40, 120, neon_intensity//i))
            screen.blit(glow_text, (SCREEN_WIDTH//2 - 180 + random.randint(-1,1), 
                                   SCREEN_HEIGHT//2 - 120 + random.randint(-1,1)))

        screen.blit(level_text, (SCREEN_WIDTH//2 - 180, SCREEN_HEIGHT//2 - 120))

        # Animated neon button
        button_width = 400
        button_height = 60
        button_rect = pygame.Rect((SCREEN_WIDTH - button_width)//2, SCREEN_HEIGHT//2 + 40, 
                                button_width, button_height)
        
        # Cycling neon border
        neon_hue = (neon_hue + 0.8) % 360
        border_color = pygame.Color(0)
        border_color.hsva = (neon_hue, 100, 100, 100)
        
        # Button background
        pygame.draw.rect(screen, (20, 20, 30), button_rect, border_radius=10)
        pygame.draw.rect(screen, border_color, button_rect, 3, border_radius=10)
        
        # Button text
        start_font = pygame.font.Font("assets/font/Pricedown.otf", 32)
        start_text = start_font.render("PRESS SPACE TO START", True, 
                                     (200, 230, 255) if start_alpha == 255 else (100, 100, 120))
        start_rect = start_text.get_rect(center=button_rect.center)
        screen.blit(start_text, start_rect)

        # Grunge texture overlay
        grunge = pygame.image.load("assets/image/background/grunge.jpg").convert_alpha()
        grunge.set_alpha(30)
        screen.blit(grunge, (0, 0))

        # Fade in effect
        if start_alpha < 255:
            start_alpha = min(start_alpha + 5, 255)
            fade_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            fade_surface.fill((0, 0, 0))
            fade_surface.set_alpha(255 - start_alpha)
            screen.blit(fade_surface, (0, 0))

        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
                
        keys = pygame.key.get_pressed()
        if keys[pygame.K_SPACE] and start_alpha >= 255:
            # Flash effect before transition
            for _ in range(3):
                flash_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
                flash_surface.fill((255, 40, 120))
                flash_surface.set_alpha(100)
                screen.blit(flash_surface, (0, 0))
                pygame.display.update()
                pygame.time.delay(50)
            starting_sound.stop()
            break

        pygame.display.update()


def fade_outro():
    global fade_alpha, isDeathSoundPlay
    if fade_alpha < 255:  # Increase opacity over time
        fade_alpha += 2
    outro_surface.set_alpha(fade_alpha)
    screen.blit(outro_surface, (0, 0))

    if fade_alpha >= 255:
        #display game over screen
        text = big_font.render("Wasted ", True, WHITE)
        text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        restart_text = font.render("Met your fate ? Press R to rise again !", True, WHITE)
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
    global bg_scroll_x, bg_scroll_y, isDeathSoundPlay, fade_alpha, player
    
    
    DisplayLevel()
    
    # play background music
    bg_music.play(-1)

    create_map()
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
        
        # Update and draw the jumper
        for jumper in jumper_group:
            jumper.update()
            jumper.checkCollision(player)
            jumper.draw(screen)

        for grass in grass_group:
            grass.update()
            grass.draw()

        # Update and draw the bullets
        bullet_group.update(ground_group, enemy_group, player)
        bullet_group.draw(screen)

        # Update and draw the ground
        for ground in ground_group:
            ground.update()
            ground.draw()
        
        # Update and draw the exit
        for exit in exit_group:
            exit.update()
            exit.draw()
        

        # Update and draw the enemy
        for enemy in enemy_group:
            enemy.update()
            enemy.move(player, ground_group)
            enemy.draw(screen, bg_scroll_x, bg_scroll_y)
        
        if bg_scroll_y > 1800:
            player.alive = False
            player.health = 0
            
        
        # Display HUD        
        current_ammo = BULLET_INFO[player.current_gun]['remaining'] if BULLET_INFO[player.current_gun]['remaining'] > 0 else "No Ammo"
        text = font.render(f"{current_ammo}", True, WHITE)
        screen.blit(text, (40, 50))
        screen.blit(bullet_icon, (15, 52))

        remaining_ammo = BULLET_INFO[player.current_gun]['total'] if BULLET_INFO[player.current_gun]['total'] > 0 else "No Ammo"
        text = font.render(f"{remaining_ammo}", True, WHITE)
        screen.blit(text, (40, 90))
        screen.blit(remaining_bullet_icon, (10, 92))
                        
        # player health
        player.health_bar.width = player.health_ratio * player.health
        
        # Text for health
        screen.blit(heart_image, (10, 10))
        
        pygame.draw.rect(screen,GREEN, player.health_bar)
        pygame.draw.rect(screen, RED, player.health_bar, 2)
        
        # Draw the achievement text
        draw_achievement()
        
        if player.has_key:
            screen.blit(key_image, (10, 130))
        
        if not player.alive:
            fade_outro()
            if not isDeathSoundPlay:
                # fade out the background music
                pygame.mixer.Sound.stop(bg_music)
                isDeathSoundPlay = True
                pygame.mixer.Sound("assets/sfx/death.mp3").play()      
            # Look for the R key to restart the game
            keys = pygame.key.get_pressed()
            if keys[pygame.K_r]:
                fade_alpha = 0
                isDeathSoundPlay = False
                bg_music.play(-1)
                bg_scroll_x = 0
                bg_scroll_y = 0
                
                # Reset Sprite Groups
                bullet_group.empty()
                ground_group.empty()
                enemy_group.empty()
                collect_item_group.empty()
                collect_item_group.empty()
                jumper_group.empty()
                exit_group.empty()
                grass_group.empty()
                
                # Reset the game
                player = Player()
                create_map()
        else:
            fade_intro()


        # Update the display
        pygame.display.flip()
        clock.tick(60)

if __name__ == "__main__":
    main()
