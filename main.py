import pygame
import sys, time, cv2
import json
from player import Player, bullet_group
from settings import *
from enemy import Enemy
import numpy as np



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
# Level text with neon flicker
level_font = pygame.font.Font("assets/font/INFECTED.ttf", 80)  # Use a tech/street font
start_font = pygame.font.Font("assets/font/Pricedown.otf", 32)


current_level = 0

isDeathSoundPlay = False

 # Create a surface for the fade out
outro_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
outro_surface.fill((220, 20, 60))

# Create a surface for the fade in

intro_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
intro_surface.fill((0, 200, 255))  # Neon Cyan

fade_alpha = 255

def create_map():
    global background_image, bg_images, bg_scroll_x, bg_scroll_y, current_level, ZOOM_VALUE
    
    # Load the level 1 as json file 
    with open(f"assets/level_{current_level}.json") as file:
        maze_layout = json.load(file)
    
    if current_level == 3:
        ZOOM_VALUE = 0.5
        player.update_size(ZOOM_VALUE)
    
    height = len(maze_layout)
    width = len(maze_layout[0])
    
    bg_scroll_x = 0
    bg_scroll_y = 0

    # Load the background image
    
    background_image = pygame.transform.scale(background_image, (width * CELL_SIZE * ZOOM_VALUE, height * CELL_SIZE * ZOOM_VALUE))
    
    # First create all ground tiles without any offset
    for y, row in enumerate(maze_layout):
        for x, cell in enumerate(row):
            world_x = x * CELL_SIZE * ZOOM_VALUE
            world_y = y * CELL_SIZE * ZOOM_VALUE
            
            if cell > 0 and cell <= 45:  # Ground
                if cell >=5 and cell <= 8 or cell == 35:
                    grass = Grass(world_x, world_y, cell)
                    grass_group.add(grass)
                else:
                    ground = Ground(world_x, world_y, cell)
                    ground_group.add(ground)

            elif cell == 46:  # Enemy
                enemy = Enemy(world_x, world_y - CELL_SIZE // 2, "normal")
                enemy_group.add(enemy)
            elif cell == 47:  # Enemy
                enemy = Enemy(world_x, world_y - CELL_SIZE // 2, "strong")
                enemy_group.add(enemy)
            elif cell == 48:
                collect_item = CollectItem(world_x, world_y, "key", "key")
                collect_item_group.add(collect_item)
            elif cell == 49:
                collect_item = CollectItem(world_x, world_y, "health", "health")
                collect_item_group.add(collect_item)
            elif cell == 50:
                collect_item = Ammo(world_x, world_y,"rifle")
                ammo_group.add(collect_item)
            elif cell == 51:
                collect_item = Ammo(world_x, world_y,"rifle")
                ammo_group.add(collect_item)
            elif cell == 52:  # Player
                player.rect.midbottom = (world_x + CELL_SIZE // 2, world_y)  # Center player horizontally
            elif cell == 54: 
                jumper = Jumper(world_x, world_y)
                jumper_group.add(jumper)
            elif cell == 55:
                exit = Exit(world_x, world_y)
                exit_group.add(exit)
            elif cell == 57:
                collect_item = CollectItem(world_x, world_y,"smg_gun","smg")
                collect_item_group.add(collect_item)
            elif cell == 59:
                collect_item = Ammo(world_x, world_y,"smg")
                ammo_group.add(collect_item)

            

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


def show_Intro():
    running = True
    # Video settings
    video_path = "assets/intro_1.mp4"
    audio_path = "assets/intro.ogg"  
    video = cv2.VideoCapture(video_path)

    fps = video.get(cv2.CAP_PROP_FPS)  # Keep as float to avoid precision errors
    frame_time = 1 / fps  # Time per frame
    try:
        pygame.mixer.music.load(audio_path)  # Ensure it's in OGG format
        pygame.mixer.music.play()
    except pygame.error as e:
        print(f"Error loading audio: {e}")



    # Check if video opened correctly
    if not video.isOpened():
        print("Error: Could not open video.")
        exit()
    while running:
        start_time = time.time()  # Track time for accurate frame display

        ret, frame = video.read()
        if not ret:
            break  # Exit when the video ends

        # Convert OpenCV frame (BGR → RGB)
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        # mirror the frame
        frame = np.fliplr(frame)
        # Convert frame to Pygame surface
        frame_surface = pygame.surfarray.make_surface(np.rot90(frame))

        # Display the frame
        screen.blit(frame_surface, (0, 0))
        pygame.display.update()

        # Check for spacebar to skip video
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                running = False

        # Ensure proper frame rate timing
        elapsed_time = time.time() - start_time
        sleep_time = max(0, frame_time - elapsed_time)  # Ensure we maintain the correct FPS
        time.sleep(sleep_time)
    pygame.mixer.music.stop()
    video.release()
    

class Exit(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.image.load("assets/image/new_map/exit.png")
        self.image = pygame.transform.scale(self.image, (CELL_SIZE // 2 * ZOOM_VALUE, CELL_SIZE * ZOOM_VALUE))
        self.rect = self.image.get_rect()
        self.x = x
        self.y = y
        self.rect.bottomright = (self.x, self.y - CELL_SIZE)
    
    def update(self):
        self.rect.x = self.x - bg_scroll_x
        self.rect.y = self.y - bg_scroll_y
    
    def checkCollision(self, player):
        if self.rect.colliderect(player.rect) and player.has_key:
            player.has_key = False
            
            # Display A Level Complete for few second then move to next level
            for i in range(150):
                screen.fill((57, 255, 20))
                text = big_font.render("LEVEL COMPLETE", True, WHITE)
                text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
                screen.blit(text, text_rect)
                pygame.display.flip()
                clock.tick(60)
            DisplayLevel()
    
    def draw(self):
        screen.blit(self.image, self.rect)


class Ground(pygame.sprite.Sprite):
    def __init__(self, x, y, image):
        super().__init__()
        self.image = pygame.image.load(f"assets/image/new_map/Tile_{image}.png")
        self.image = pygame.transform.scale(self.image, (CELL_SIZE * ZOOM_VALUE, CELL_SIZE * ZOOM_VALUE))
        self.rect = self.image.get_rect()
        self.x = x
        self.y = y
        self.rect.center = (self.x, self.y)
    
    def update(self):
        self.rect.x = self.x - bg_scroll_x
        self.rect.y = self.y - bg_scroll_y
    
    def draw(self):
        screen.blit(self.image, self.rect)
        # pygame.draw.rect(screen, (255, 0, 0), self.rect, 1)


class Grass(pygame.sprite.Sprite):
    def __init__(self, x, y, image):
        super().__init__()
        self.image = pygame.image.load(f"assets/image/new_map/Tile_{image}.png")
        self.image = pygame.transform.scale(self.image, (CELL_SIZE // 2 * ZOOM_VALUE, CELL_SIZE // 2 * ZOOM_VALUE))
        self.rect = self.image.get_rect()
        self.x = x + (CELL_SIZE // 2 ) * ZOOM_VALUE
        self.y = y + (CELL_SIZE // 2 ) * ZOOM_VALUE
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
        self.image = pygame.transform.scale(self.image, (CELL_SIZE // 2 - 10 * ZOOM_VALUE, CELL_SIZE // 2 * ZOOM_VALUE))
        self.rect = self.image.get_rect()
        self.x = x
        self.y = y + CELL_SIZE // 2
        self.rect.center = (self.x, self.y)
        self.type = type
    
    def update(self):
        self.rect.x = self.x - bg_scroll_x
        self.rect.y = self.y - bg_scroll_y
    
    def draw(self):
        if self.type == "smg" or self.type == "laser":
            self.image = pygame.transform.scale(self.image, (CELL_SIZE * ZOOM_VALUE, CELL_SIZE // 2 * ZOOM_VALUE))
        screen.blit(self.image, self.rect)
        # pygame.draw.rect(screen, (255, 0, 0), self.rect, 1)
    
    def collect(self):
        if self.type == "health" and player.health < 100:
            player.health = min(player.health + 20, 100)
            collect_item_group.remove(self)
            health_pickup_sound.play()
            show_achievement("Health +20")
        elif self.type == "key":
            player.has_key = True
            health_pickup_sound.play()
            collect_item_group.remove(self)
            show_achievement("Key Collected !")
        elif self.type == "smg":
            player.isSmg = True
            collect_item_group.remove(self)
            health_pickup_sound.play()
            show_achievement("New Weapon SMG Unlocked")
            

class Ammo(pygame.sprite.Sprite):
    def __init__(self, x, y, gunammo):
        super().__init__()
        self.frame_index = 0
        self.gunammo = gunammo
        self.image = pygame.image.load(f"assets/image/collect_item/ammo/{self.gunammo}_{self.frame_index}.png")
        self.image = pygame.transform.scale(self.image, (30 * ZOOM_VALUE,30 * ZOOM_VALUE))
        self.rect = self.image.get_rect()
        self.x = x
        self.y = y + CELL_SIZE // 2
        self.rect.center = (self.x, self.y)
        self.animation_cooldown = 100
        self.last_update_time = pygame.time.get_ticks()
    
    def update(self):
        self.rect.x = self.x - bg_scroll_x
        self.rect.y = self.y - bg_scroll_y
        if pygame.time.get_ticks() - self.last_update_time > self.animation_cooldown:
            self.last_update_time = pygame.time.get_ticks()
            self.frame_index += 1
        if self.frame_index >= 4:
            self.frame_index = 0
        
        self.image = pygame.image.load(f"assets/image/collect_item/ammo/{self.gunammo}_{self.frame_index}.png")
        self.image = pygame.transform.scale(self.image, (30 * ZOOM_VALUE,30 * ZOOM_VALUE))
    
    
    def collect(self):
        player.bullet_info[self.gunammo]['total'] += 10
        ammo_group.remove(self)
        bullet_pickup_sound.play()
        show_achievement(f"{self.gunammo} Ammo +10")
    
    def draw(self):
        screen.blit(self.image, self.rect)
        # pygame.draw.rect(screen, (255, 0, 0), self.rect, 1)


class Jumper(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.image.load("assets/image/new_map/jumper.png")
        self.image = pygame.transform.scale(self.image, (20 * ZOOM_VALUE,20 * ZOOM_VALUE))
        self.rect = self.image.get_rect()
        self.x = x
        self.y = y + (CELL_SIZE // 2 + 15) * ZOOM_VALUE
        self.rect.center = (self.x, self.y)

    def update(self):
        self.rect.x = self.x - bg_scroll_x
        self.rect.y =self.y - bg_scroll_y
    

    def checkCollision(self, player):
        if self.rect.colliderect(player.rect):
            player.InAir = True
            player.speed = 4
            player.vel_y = -22 * ZOOM_VALUE
            jumper_sound.play()
            player.update_animation("Jump")


    def draw(self, screen):
        screen.blit(self.image, (self.rect.x, self.rect.y))


def DisplayLevel():
    global current_level
    start_alpha = 0
    neon_hue = 0
    current_level += 1



    while True:
        screen.fill((10, 10, 15))  # Dark base color
    
        level_text = level_font.render("CITY GANG", True, (185, 1, 3))
        
        screen.blit(level_text, (SCREEN_WIDTH//2 - 180, SCREEN_HEIGHT//2 - 120))
        
        level_text = start_font.render(f"Level {current_level}", True, (185, 1, 3))
        screen.blit(level_text, (SCREEN_WIDTH//2 - 50, 30))

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
        start_text = start_font.render("PRESS SPACE TO START", True, 
                                     (200, 230, 255) if start_alpha == 255 else (100, 100, 120))
        start_rect = start_text.get_rect(center=button_rect.center)
        screen.blit(start_text, start_rect)
        

        # Grunge texture overlay
        grunge = pygame.image.load("assets/image/background/bg_image.png").convert_alpha()
        grunge = pygame.transform.scale(grunge, (SCREEN_WIDTH * ZOOM_VALUE, SCREEN_HEIGHT * ZOOM_VALUE))
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
            select_sound.play()
            # Flash effect before transition
            for _ in range(3):
                flash_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
                flash_surface.fill((255, 40, 120))
                flash_surface.set_alpha(100)
                screen.blit(flash_surface, (0, 0))
                pygame.display.update()
                pygame.time.delay(50)
            starting_sound.stop()
            bullet_group.empty()
            ground_group.empty()
            enemy_group.empty()
            collect_item_group.empty()
            jumper_group.empty()
            exit_group.empty()
            grass_group.empty()
            ammo_group.empty()
            create_map()
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


def get_color(current_value, max_value):
    # Change color dynamically (Green → Yellow → Red)
    if current_value > max_value * 0.7:
        color = (0, 255, 0)  # Green
    elif current_value > max_value * 0.3:
        color = (255, 255, 0)  # Yellow
    else:
        color = (255, 0, 0)  # Red
    return color


def display_HUD():

    current_ammo = player.bullet_info[player.current_gun]['remaining'] if player.bullet_info[player.current_gun]['remaining'] > 0 else "No Ammo"

    # get the color of the ammo text
    color = get_color(player.bullet_info[player.current_gun]['remaining'], player.bullet_info[player.current_gun]['mag_size'])

    text = font.render(f"{current_ammo}", True, color)
    screen.blit(text, (40, 50))
    screen.blit(bullet_icon, (15, 52))

    if player.bullet_info[player.current_gun]['total'] > 0 :
        remaining_ammo = player.bullet_info[player.current_gun]['total'] 
        col = (0, 255, 255)
    else :
        remaining_ammo = "No Ammo"
        col = (255, 0, 0) 
    text = font.render(f"{remaining_ammo}", True, col)
    screen.blit(text, (40, 90))
    screen.blit(remaining_bullet_icon, (10, 92))
                    
    # player health
    player.health_bar.width = player.health_ratio * player.health
    
    # Text for health
    screen.blit(heart_image, (10, 10))
    
    color = get_color(player.health, 100)

    pygame.draw.rect(screen,color, player.health_bar)
    pygame.draw.rect(screen,  (50, 50, 50), player.health_bar, 2)

    # Display Sprint Bar
    # Calculate sprint bar width based on sprint_value
    current_width = (player.sprint_value / 200) * 100

    color = get_color(player.sprint_value, 200)

    # Draw the sprint bar (Background)
    pygame.draw.rect(screen, (50, 50, 50), (40, 130, 100, 20))  
    
    # Draw sprint bar (filled part)
    pygame.draw.rect(screen, color, (40,130, current_width, 20))
    screen.blit(running_icon, (10, 130))

    
player = Player()

def main():
    global bg_scroll_x, bg_scroll_y, isDeathSoundPlay, fade_alpha, player, current_level

    DisplayLevel()
    # play background music
    bg_music.play(-1)

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
                # switch weapons
                if event.key == pygame.K_1 and player.isRifle:
                    player.current_gun = "rifle"
                    select_sound.play()
                    PLAYER_ANIMATION["Shot"]['animation_cooldown'] = BULLET_INFO[player.current_gun]['cooldown']
                    show_achievement("Rifle Selected")
                if event.key == pygame.K_2 and player.isSmg:
                    player.current_gun = "smg"
                    select_sound.play()
                    PLAYER_ANIMATION["Shot"]['animation_cooldown'] = BULLET_INFO[player.current_gun]['cooldown']
                    show_achievement("SMG Selected")
                if event.key == pygame.K_3 and player.isLaser:
                    player.current_gun = "laser"
                    PLAYER_ANIMATION["Shot"]['animation_cooldown'] = BULLET_INFO[player.current_gun]['cooldown']
                    select_sound.play()
                    show_achievement("Laser Selected")
       
        # Draw the background
        screen.fill((119,120,121))

        # Update and draw the exit
        for exit in exit_group:
            exit.update()
            exit.draw()
            exit.checkCollision(player)
        
        # Draw the background image
        screen.blit(background_image, (0 -bg_scroll_x, 0 - bg_scroll_y))
        
        # Update and draw the player
        x, y = player.move(ground_group)
        bg_scroll_x += x
        bg_scroll_y += y        
        player.update()
        player.draw(screen)
        
        player_x = player.rect.x 
        player_y = player.rect.y 

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
        for bullet in bullet_group:
            bullet.update(x, y)
            bullet.check_collision(ground_group, enemy_group, player, bg_scroll_x, bg_scroll_y)
            bullet.draw(screen)

        # Update and draw the ground
        for ground in ground_group:

            diff_x = abs(ground.x - bg_scroll_x - player_x)
            diff_y = abs(ground.y - bg_scroll_y - player_y)
            ground.update()
            if diff_x < 800 and diff_y < 600:
                ground.draw()
        
        # Update and draw the enemy
        for enemy in enemy_group:
            diff_x = abs(enemy.x - bg_scroll_x - player_x)
            diff_y = abs(enemy.y - bg_scroll_y - player_y)
            # # print(diff_x, diff_y)
            if diff_x < 800 and diff_y < 600:
                enemy.update()
                enemy.move(player, ground_group)
                enemy.draw(screen, bg_scroll_x, bg_scroll_y)
        
        # Update and draw the ammo
        for ammo in ammo_group:
            ammo.update()
            ammo.draw()
            if player.rect.colliderect(ammo.rect):
                ammo.collect()
                
        # if bg_scroll_y > 1800:
        #     player.alive = False
        #     player.health = 0
            
        
        # Display HUD
        display_HUD()
        # Draw the achievement text
        draw_achievement()
        
        
        # Display FPS in the Screen
        fps = str(int(clock.get_fps()))
        fps_text = font.render(f"FPS: {fps}", True, WHITE)
        screen.blit(fps_text, (SCREEN_WIDTH // 2, 10))
        
        if player.has_key:
            screen.blit(key_image, (720, 20))
        
        if not player.alive:
            fade_outro()
            if not isDeathSoundPlay:
                # fade out the background music
                pygame.mixer.Sound.stop(bg_music)
                isDeathSoundPlay = True
                death_sound.play()      
            # Look for the R key to restart the game
            keys = pygame.key.get_pressed()
            if keys[pygame.K_r]:
                fade_alpha = 0
                isDeathSoundPlay = False
                bg_music.play(-1)
                bg_scroll_x = 0
                bg_scroll_y = 0
                death_sound.stop()
                
                # Reset Sprite Groups
                bullet_group.empty()
                ground_group.empty()
                enemy_group.empty()
                collect_item_group.empty()
                collect_item_group.empty()
                jumper_group.empty()
                exit_group.empty()
                grass_group.empty()
                has_smg = player.isSmg
                has_laser = player.isLaser
                
                # Reset the game
                player = Player()
                player.isSmg = has_smg
                player.isLaser = has_laser
                create_map()
        else:
            fade_intro()


        # Update the display
        pygame.display.flip()
        clock.tick(FPS)

if __name__ == "__main__":
    # show_Intro()
    main()