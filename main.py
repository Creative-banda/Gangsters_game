import pygame
import sys, time, cv2
import json, random
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

# PLAY BACKGROUND MUSIC
starting_sound.play(-1)

# FONTS
font = pygame.font.Font('assets/font/Pricedown.otf', 25)
big_font = pygame.font.Font("assets/font/Bronx_Bystreets.ttf", 50)

level_font = pygame.font.Font("assets/font/Bronx_Bystreets.ttf", 80)  # Use a tech/street font
start_font = pygame.font.Font("assets/font/Pricedown.otf", 32)
conversation_font = pygame.font.Font("assets/font/Lunar_Escape.otf", 18)


# TRACKING LOCAL VARIABLES
current_level = 3
isDeathSoundPlay = False

# Create a surface for the fade out
outro_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
outro_surface.fill((220, 20, 60))

# CREATE A SURFACE FOR THE FADE IN 
intro_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
intro_surface.fill((0, 200, 255))  # Neon Cyan
fade_alpha = 255


def create_map():
    global scaled_bg_images, bg_scroll_x, bg_scroll_y, current_level, ZOOM_VALUE, height, width
    
    reset_sprites()
    
    # Load the level 1 as json file 
    with open(f"assets/level_{current_level}.json") as file:
        maze_layout = json.load(file)
    
    if current_level == 4:
        ZOOM_VALUE = 0.5
        player.update_size(ZOOM_VALUE)
        for bullet in bullet_group:
            bullet.update_size(ZOOM_VALUE)
            
        
    height = len(maze_layout)
    width = len(maze_layout[0])
    
    bg_scroll_x = 0
    bg_scroll_y = 0

    # Load the background image
    
    scaled_bg_images = [pygame.transform.scale(bg_img, (width * CELL_SIZE // 4* ZOOM_VALUE, height * CELL_SIZE // 3 * ZOOM_VALUE)) for bg_img in bg_img_list]

    
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
            elif cell == 50:
                collect_item = CollectItem(world_x, world_y, "key")
                collect_item_group.add(collect_item)
            elif cell == 49:
                collect_item = CollectItem(world_x, world_y, "health")
                collect_item_group.add(collect_item)
            elif cell == 51:
                collect_item = Ammo(world_x, world_y,"rifle")
                ammo_group.add(collect_item)
            elif cell == 54: 
                jumper = Jumper(world_x, world_y)
                jumper_group.add(jumper)
            elif cell == 55:
                exit = Exit(world_x, world_y)
                exit_group.add(exit)
            elif cell == 56:
                collect_item = CollectItem(world_x, world_y,"laser")
                collect_item_group.add(collect_item)
            elif cell == 57:
                collect_item = CollectItem(world_x, world_y,"smg")
                collect_item_group.add(collect_item)
            elif cell == 58:
                collect_item = Ammo(world_x, world_y,"laser")
                ammo_group.add(collect_item)
            elif cell == 59:
                collect_item = Ammo(world_x, world_y,"smg")
                ammo_group.add(collect_item)
            
            elif cell == 60:  # Player
                player.rect.midbottom = (world_x + CELL_SIZE // 2, world_y)  # Center player horizontally
            
            elif cell == 99:
                acid = Acid(world_x, world_y)
                print("Acid Created")
                acid_group.add(acid)
            elif cell == 100:
                boss = Enemy(world_x, world_y - CELL_SIZE // 2, "boss")
                boss_group.add(boss)
                

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


class Acid(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.x = x
        self.y = y + 30 * ZOOM_VALUE
        self.frame_index = 0
        self.animation_cooldown = 200
        self.images = []
        self.last_damage_time = pygame.time.get_ticks()
        
        self.last_update_time = pygame.time.get_ticks()
        for i in range(4):
            self.image = pygame.image.load(f"assets/image/new_map/acid-{i}.png")
            self.image = pygame.transform.scale(self.image, (CELL_SIZE * ZOOM_VALUE, (CELL_SIZE + 10) * ZOOM_VALUE))
            self.images.append(self.image)
        self.image = self.images[self.frame_index]
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
    
    def update(self):
        self.rect.x = self.x - bg_scroll_x
        self.rect.y = self.y - bg_scroll_y
        if pygame.time.get_ticks() - self.last_update_time > self.animation_cooldown:
            self.last_update_time = pygame.time.get_ticks()
            self.frame_index += 1
            if self.frame_index >= 3:
                self.frame_index = 0
            self.image = self.images[self.frame_index]
    
    def check_collision(self, player):
        current_time = pygame.time.get_ticks()
        
        if self.rect.colliderect(player.rect):

            if current_time - self.last_damage_time > 2000:
                self.last_damage_time = current_time  # Update before dealing damage
                print("Acid Damage")
                
                player.health -= 20
                if player.health <= 0:
                    player.alive = False
                else:
                    player.InAir = True
                    player.vel_y = -15 * ZOOM_VALUE
                    player.update_animation("Hurt")
                    player.speed = 4

        


    def draw(self):
        screen.blit(self.image, self.rect)


class Exit(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.x = x
        self.y = y
        self.images = []
        self.playerTouch = False
        self.frame_index = 0
        self.last_update_time = pygame.time.get_ticks()
        self.animation_cooldown = 200
        self.animation_complete = False
        for i in range(6):
            self.image = pygame.image.load(f"assets/image/new_map/exit-{i}.png")
            self.image = pygame.transform.scale(self.image, (CELL_SIZE // 2 * ZOOM_VALUE, CELL_SIZE * ZOOM_VALUE))
            self.images.append(self.image)
        
        self.image = self.images[self.frame_index]
        self.rect = self.image.get_rect()
        self.rect.center = (self.x, self.y - CELL_SIZE)
    
    def update(self, bg_scroll_x, bg_scroll_y):

        self.rect.x = self.x - bg_scroll_x
        self.rect.y = self.y - bg_scroll_y
        if self.playerTouch and pygame.time.get_ticks() - self.last_update_time > self.animation_cooldown and self.animation_complete == False:
            self.last_update_time = pygame.time.get_ticks()
            self.frame_index += 1
            if self.frame_index >= 5:
                self.animation_complete = True
                self.frame_index = 5
            self.image = self.images[self.frame_index]
    
    def checkCollision(self, player):

        if self.rect.colliderect(player.rect) and player.has_key:
            player.has_key = False
            player.isActive = False
            player.update_animation("idle")
            self.playerTouch = True
            
        if self.animation_complete:
            # Display A Level Complete for few second then move to next level
            for _ in range(150):
                screen.fill((57, 255, 20))
                text = big_font.render("LEVEL COMPLETE", True, WHITE)
                text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
                screen.blit(text, text_rect)
                pygame.display.flip()
                clock.tick(60)
            player.isActive = True
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
    def __init__(self, x, y, type):
        super().__init__()
        self.type = type
        self.frame_index = 0
        self.max_frame_index = 39
        self.x = x
        self.y = y 
        self.animation_cooldown = 50   
        
        self.last_update_time = pygame.time.get_ticks()
        self.images = []
        
        for i in range(self.max_frame_index):
            self.image = pygame.image.load(f"assets/image/collect_item/{self.type}/{self.type}-{i}.png").convert_alpha()
            if self.type == "smg" or self.type == "laser":
                self.image = pygame.transform.scale(self.image, ((CELL_SIZE + 30) * ZOOM_VALUE, (CELL_SIZE + 30)  * ZOOM_VALUE))        
            else:
                self.image = pygame.transform.scale(self.image, (CELL_SIZE * ZOOM_VALUE, CELL_SIZE * ZOOM_VALUE ))
            self.images.append(self.image)
        
        
        self.image = self.images[self.frame_index]
        self.rect = self.image.get_rect()
        self.rect.center = (self.x, self.y)
    
    def update(self):
        self.rect.x = self.x - bg_scroll_x
        self.rect.y = self.y - bg_scroll_y
        if pygame.time.get_ticks() - self.last_update_time > self.animation_cooldown:
            self.last_update_time = pygame.time.get_ticks()
            self.frame_index += 1
            if self.frame_index >= self.max_frame_index - 1:
                self.frame_index = 0
            
            self.image = self.images[self.frame_index]
    
    def draw(self):
       
        screen.blit(self.image, self.rect)
        # pygame.draw.rect(screen, (255, 0, 0), self.rect, 1)
    
    def collect(self):
        if self.type == "health" and player.health < 100:
            player.health = min(player.health + 20, 100)
            health_pickup_sound.play()
            show_achievement("Health +20")
            
            self.kill()
        elif self.type == "key":
            player.has_key = True
            health_pickup_sound.play()
            show_achievement("Key Collected !")
            self.kill()
        elif self.type == "smg":
            player.isSmg = True
            health_pickup_sound.play()
            show_achievement("New Weapon SMG Unlocked")
            self.kill()
        elif self.type == "laser":
            player.isLaser = True
            health_pickup_sound.play()
            show_achievement("New Weapon Laser Unlocked")
            self.kill()
        
           
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
        if self.gunammo == "rifle":
            self.ammo_contain = 20
        elif self.gunammo == "smg":
            self.ammo_contain = 30
        elif self.gunammo == "laser":
            self.ammo_contain = 10
    
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
        player.bullet_info[self.gunammo]['total'] +=self.ammo_contain
        ammo_group.remove(self)
        bullet_pickup_sound.play()
        show_achievement(f"{self.gunammo} Ammo +{self.ammo_contain}")
    
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


class Plane(pygame.sprite.Sprite):
    def __init__(self, x, y, type):
        super().__init__()
        self.type = type
        self.image = pygame.image.load(f"assets/image/background/{self.type}_plane.png")
        self.image = pygame.transform.scale(self.image, (80 * ZOOM_VALUE, 50 * ZOOM_VALUE))
        self.rect = self.image.get_rect()
        self.x = x
        self.y = y
        self.rect.center = (self.x, self.y)
        self.speed = 2
        self.isDropped = False
    
    def update(self):
        self.x += self.speed  # Move the plane in the world
        self.rect.x = self.x - bg_scroll_x  # Apply scrolling adjustment
        self.rect.y = self.y - bg_scroll_y  # Apply vertical scrolling
        
        if self.rect.centerx >= player.rect.centerx - 50 and not self.isDropped:
            self.isDropped = True
            if self.type == "enemy":
                enemy = Enemy(self.rect.x + bg_scroll_x, self.rect.y + bg_scroll_y - (CELL_SIZE * ZOOM_VALUE), random.choice(["normal", "strong"]), 0.5)
                enemy_group.add(enemy)
            elif self.type == "drop":
                drop = Drop(self.rect.x + bg_scroll_x, self.rect.y + bg_scroll_y)
                drop_group.add(drop)
            elif self.type == "bomb":
                bomb = Bomb(self.rect.x + bg_scroll_x , self.rect.y + bg_scroll_y) 
                bomb_group.add(bomb)

    
    def draw(self):
        screen.blit(self.image, self.rect)
        # pygame.draw.rect(screen, (255, 0, 0), self.rect, 1)


class Drop(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = drop_image
        self.x = x
        self.y = y
        self.image = pygame.transform.scale(self.image, (50 * ZOOM_VALUE, 50 * ZOOM_VALUE))
        self.rect = self.image.get_rect()
        self.rect.center = (self.x, self.y)
        self.vel_y = 0  # Falling speed
        self.landed = False  # To check if it has hit the ground

    def update(self):
        if not self.landed:
            # Adjust rendering position
            self.rect.x = self.x - bg_scroll_x
            self.vel_y += 0.03  # Gravity effect
            self.y += self.vel_y  # Update actual y position

            # Update rectangle position before checking collision
            self.rect.y = self.y - bg_scroll_y

            # Check for collision with the ground
            for ground in ground_group:
                if self.rect.colliderect(ground.rect):
                    self.rect.bottom = ground.rect.top  # Stop at the ground
                    self.y = self.rect.bottom - self.rect.height  # Correct positioning
                    self.landed = True
                    self.convert_to_supply()
                    break  # Stop checking after landing




    def convert_to_supply(self):
        """Transform into a random supply item upon landing."""
        random_item = random.choice([
            ("health", "health"),
            ("rifle_ammo", "rifle"),
            ("smg_ammo", "smg")
        ])


        if "ammo" in random_item[0]:  
            new_item = Ammo(self.rect.x + bg_scroll_x, self.rect.y + bg_scroll_y  - (CELL_SIZE * ZOOM_VALUE), random_item[1])
            ammo_group.add(new_item)
        else:
            new_item = CollectItem(self.rect.x + bg_scroll_x, self.rect.y + bg_scroll_y  - (CELL_SIZE * ZOOM_VALUE) , random_item[1])
            collect_item_group.add(new_item)

        # Remove the drop after transforming
        self.kill()


    def draw(self, screen):
        screen.blit(self.image, self.rect)
        # pygame.draw.rect(screen, (255, 0, 0), self.rect, 1)


class Bomb(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()

        self.x = x
        self.y = y
        
        self.image = bomb_image
        self.rect = self.image.get_rect()
        self.rect.center = (self.x, self.y)
        self.vel_y = 0  # Falling speed

    def update(self, ground_group):
        # Adjust rendering position
        self.rect.x = self.x - bg_scroll_x
        self.vel_y += 0.06  # Gravity effect
        self.y += self.vel_y  # Update actual y position

        # Update rectangle position before checking collision
        self.rect.y = self.y - bg_scroll_y
        for ground in ground_group:
            if self.rect.colliderect(ground.rect):
                self.rect.bottom = ground.rect.top
                self.kill()
                explosion = Explosion(self.rect.x + bg_scroll_x, self.rect.y + bg_scroll_y - (CELL_SIZE * ZOOM_VALUE))
                explosion_group.add(explosion)

    def draw(self):
        screen.blit(self.image, self.rect)
        # pygame.draw.rect(screen, (255, 0, 0), self.rect, 1)


class Explosion(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.x = x
        self.y = y
        self.frame_index = 0
        self.animation_cooldown = 100
        self.last_update_time = pygame.time.get_ticks()
        self.isAudioPlay = False
        self.damage_given = False
        self.images = []
        for i in range(0,15):
            self.image = pygame.image.load(f"assets/image/explosion/explosion-{i}.png")
            self.image = pygame.transform.scale(self.image, (CELL_SIZE * 2 * ZOOM_VALUE, CELL_SIZE * 2 * ZOOM_VALUE))
            self.images.append(self.image)
        self.image = self.images[self.frame_index]
        self.rect = self.image.get_rect()
        self.rect.center = (self.x, self.y)
    
    def update(self):
        self.rect.x = self.x - bg_scroll_x
        self.rect.y = self.y - bg_scroll_y
        if pygame.time.get_ticks() - self.last_update_time > self.animation_cooldown:
            self.last_update_time = pygame.time.get_ticks()
            self.frame_index += 1
            self.image = self.images[self.frame_index]
        if not self.isAudioPlay:
            explosion_sound.play()
            self.isAudioPlay = True
        if not self.damage_given:
            self.check_collision()
            self.damage_given = True
        
        if self.frame_index >= 14:
            self.kill()

    
    def check_collision(self):
        for enemy in enemy_group:
            if self.rect.colliderect(enemy.rect):
                enemy.take_damage(100)
        if self.rect.colliderect(player.rect):
            player.health -= 50
            if player.health <= 0:
                player.alive = False
            else:
                player.update_animation("Hurt")
            player.update_animation("Hurt")
        for boss in boss_group:
            if self.rect.colliderect(boss.rect):
                boss.take_damage(100)


    def draw(self):
        screen.blit(self.image, self.rect)
        # pygame.draw.rect(screen, (255, 0, 0), self.rect, 1)


def DisplayLevel():
    global current_level
    start_alpha = 0
    neon_hue = 0
    current_level += 1
    
    game_name = level_font.render("CITY GANG", True, (185, 1, 3))

    level_text = start_font.render(f"Level {current_level}", True, (185, 1, 3))

    while True:
        screen.fill((10, 10, 15))  # Dark base color
        
        screen.blit(game_name, (SCREEN_WIDTH//2 - 250 , SCREEN_HEIGHT//2 - 120))
        
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
            create_map()
            break

        pygame.display.update()


def death_outro():
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


def game_end():
    outro_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    alpha = 0  # For fade-in effect
    
    pygame.time.delay(600)  # Delay before fade-in
    
    while alpha < 150:
        screen.blit(grunge, (0, 0))  # Draw background image

        # Apply a fade-in effect with a transparent overlay
        outro_surface.fill((0, 0, 0, 255 - alpha))  
        screen.blit(outro_surface, (0, 0))  

        pygame.display.flip()  
        pygame.time.delay(50)  
        alpha += 5  
        
    
    alpha = 0  # Reset alpha for fade-out effect

    while True:
        # Display outro messages
        draw_text("The cybernetic enforcer is down...", 250, 100, conversation_font, color=(255, 50, 50))
        draw_text("But the Syndicate's leader is still out there.", 200, 150, conversation_font, color=(255, 100, 100))
        draw_text("Your fight isn't over... Not yet.", 250, 200, conversation_font, color=(255, 150, 150))

        # "Thanks for Playing" message
        draw_text("THANKS FOR PLAYING!", SCREEN_WIDTH // 2 - 320, SCREEN_HEIGHT // 2 + 50, big_font, color=(255, 50, 50))
        draw_text("Created by Ahtesham", 50, SCREEN_HEIGHT // 2 + 120, big_font, color=(200, 200, 200))

        pygame.display.flip()  # Update the screen

        for event in pygame.event.get():
            if event.type == pygame.QUIT or event.type == pygame.KEYDOWN:
                pygame.quit()
                sys.exit()


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


def draw_text(text, x, y,font, color):
    text_surface = font.render(text, True, color)
    screen.blit(text_surface, (x, y))


player = Player()


def reset_sprites():
    # Reset Sprite Groups
    bullet_group.empty()
    ground_group.empty()
    enemy_group.empty()
    collect_item_group.empty()
    jumper_group.empty()
    exit_group.empty()
    grass_group.empty()
    acid_group.empty()
    boss_group.empty()
    drop_group.empty()
    ammo_group.empty()
    plane_group.empty()


def main():
    global bg_scroll_x, bg_scroll_y, isDeathSoundPlay, fade_alpha, player, current_level
    
    current_conversation = [
        ("Player", "What the hell... who are you?"),
        ("Enemy", "Someone who's been watching you for a long time."),
        ("Player", "Stay back!"),
        ("Enemy", "Interesting. Most people run when they see me. "),
        ("Enemy", "But you... you're different."),
        ("Player", "Yeah, well, I've dealt with my share of thugs."),
        ("Enemy", "Thugs? Oh, you poor soul. You have no idea what you're facing."),
        ("Player", "Maybe not. But I'm still standing."),
        ("Enemy", "For now. I can hear your heartbeat racing."),
        ("Enemy", "Smell the adrenaline in your blood."),
        ("Player", "You're not human, are you?"),
        ("Enemy", "Human? I've evolved beyond such... limitations."),
        ("Enemy", "I am the future walking. And you?"),
        ("Enemy", " You're just another relic to be... retired."),
        ("Player", "I've taken down plenty of 'futures' before."),
        ("Enemy", "Have you? That scar on your neck suggests otherwise."),
        ("Enemy", "You survived our last encounter by pure luck."),
        ("Enemy", "Tonight, luck's not on the menu."),
        ("Player", "Wait... that was you? The attack at the marina?"),
        ("Enemy", "Just the first of many gifts I've left you."),
        ("Enemy", " Consider them... practice rounds.")
    ]

    mid_conversation = [
        ("Enemy", "You're fighting well... for obsolete hardware."),
        ("Player", "And you're bleeding well... for a 'superior being'."),
        ("Enemy", "Merely an inconvenience. Unlike your... condition.")
    ]

    end_conversation = [
        ("Enemy", "This... isn't... possible..."),
        ("Player", "Next time, try evolving a backup plan."),
        ("Enemy", "They'll... send... more..."),
        ("Player", "Tell them I'll come for them"),
    ]

    
    DisplayLevel()
    # play background music
    bg_music.play(-1)
    current_line = 0  # Track which line of conversation is being shown
    
    isConversation_Started = False # Check if conversation has started
    isMidConversation_Started = False
    isLastConversation_Started = False

    Conversation_Ended = False
    
    # Random Choice for Plane Selection
    values = ["drop", "enemy","bomb"]

    # List of probabilities corresponding to each value
    probabilities = [0.1, 0.1, 0.8]

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
                    show_achievement("Rifle Selected")
                    PLAYER_ANIMATION["Shot"]['animation_cooldown'] = BULLET_INFO[player.current_gun]['cooldown']
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
                if event.key == pygame.K_RETURN and isConversation_Started and not Conversation_Ended:
                    current_line += 1
       
        # Draw the background
        screen.fill((119,120,121))
        
        #Check Conversation Started
        if current_level == 4 and not isConversation_Started:
            for enemy in boss_group:
                if abs(player.rect.x - enemy.rect.x) < 200:
                    isConversation_Started = True
                    break
    
        # Draw the background image
        # screen.blit(background_image, (width * CELL_SIZE -bg_scroll_x, height * CELL_SIZE - bg_scroll_y))
        # screen.blit(background_image, (0 - bg_scroll_x , height * CELL_SIZE // 1.45 - bg_scroll_y ))
        
        for i, bg_img in enumerate(scaled_bg_images):
            screen.blit(bg_img, (i * 300 - (bg_scroll_x * 0.4) , height * CELL_SIZE // 1.46 - bg_scroll_y ))
        
        # Update and draw the player
        x, y = player.move(ground_group)
        bg_scroll_x += x
        bg_scroll_y += y        
        player.update()
        player.draw(screen)
        # print(bg_scroll_x, bg_scroll_y)
        
        player_x = player.rect.x 
        player_y = player.rect.y 
        
        
        # Update and draw the exit
        for exit in exit_group:
            exit.update(bg_scroll_x, bg_scroll_y)
            exit.checkCollision(player)
            exit.draw()

        # Update and draw the collect items
        for collect_item in collect_item_group:
            diff_x = abs(collect_item.x - bg_scroll_x - player_x)
            diff_y = abs(collect_item.y - bg_scroll_y - player_y)
            if diff_x < 800 and diff_y < 600:
                collect_item.update()
                collect_item.draw()
                if player.rect.colliderect(collect_item.rect):
                    collect_item.collect()
                    

        for acid in acid_group:
            acid.update()
            acid.draw()            
            acid.check_collision(player)
            
        # Update and draw the jumper
        for jumper in jumper_group:
            diff_x = abs(jumper.x - bg_scroll_x - player_x)
            diff_y = abs(jumper.y - bg_scroll_y - player_y)
            if diff_x < 800 and diff_y < 600:
                jumper.update()
                jumper.checkCollision(player)
                jumper.draw(screen)

        for grass in grass_group:
            diff_x = abs(grass.x - bg_scroll_x - player_x)
            diff_y = abs(grass.y - bg_scroll_y - player_y)
            if diff_x < 800 and diff_y < 600:
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
        

            
        for boss in boss_group:
            diff_x = abs(boss.x - bg_scroll_x - player_x)
            diff_y = abs(boss.y - bg_scroll_y - player_y)
            # # print(diff_x, diff_y)
            if diff_x < 800 and diff_y < 600:
                boss.update()
                boss.move(player, ground_group, bg_scroll_x, bg_scroll_y)
                boss.draw(screen)
            if boss.health <= 0:
                if not isLastConversation_Started:
                    isConversation_Started = True
                    Conversation_Ended = False
                    current_conversation = end_conversation
                    isLastConversation_Started = True
                for enemy in enemy_group:
                    enemy.health = 0
                    enemy.isActive = False
                    enemy.update_animation("Dead")
                    
            elif boss.health <= 5000 :
                if not isMidConversation_Started:
                    
                    boss.isActive = False
                    for enemy in enemy_group:
                        enemy.isActive = False
                    isConversation_Started = True
                    Conversation_Ended = False
                    current_conversation = mid_conversation
                    isMidConversation_Started = True


        # Update and draw the enemy
        for enemy in enemy_group:
            diff_x = abs(enemy.x - bg_scroll_x - player_x)
            diff_y = abs(enemy.y - bg_scroll_y - player_y)
            # # print(diff_x, diff_y)
            if diff_x < 800 and diff_y < 600:
                enemy.update()
                enemy.move(player, ground_group, bg_scroll_x, bg_scroll_y)
                enemy.draw(screen)
        
        # Update and draw the ammo
        for ammo in ammo_group:
            ammo.update()
            ammo.draw()
            if player.rect.colliderect(ammo.rect):
                ammo.collect()
                
        # if bg_scroll_y > 1800:
        #     player.alive = False
        #     player.health = 0
        
        # Spawn Random Plane In Level 4
        
        if current_level == 4 and Conversation_Ended:
            if pygame.time.get_ticks() % 400 == 0:
                chosen_value = random.choices(values, probabilities, k=1)[0]

                plane = Plane(-300, -40, chosen_value)
                plane_group.add(plane)
                
            for plane in plane_group:
                plane.update()
                plane.draw()
            
            for drop in drop_group:
                drop.update()
                drop.draw(screen)
            
            for bomb in bomb_group:
                bomb.update(ground_group)
                bomb.draw()
            
            for explosion in explosion_group:
                explosion.update()
                explosion.draw()

        
        # Display HUD
        display_HUD()
        # Draw the achievement text
        draw_achievement()
        
        if isConversation_Started and not Conversation_Ended:
            print("Conversation Started")
    
            player.isActive = False
            player.update_animation("idle")
            
            # Display Conversation
            if current_line < len(current_conversation):
                speaker, text = current_conversation[current_line]

                # --- UI Enhancements ---

                # Semi-transparent background for the dialogue box
                dialogue_box = pygame.Surface((SCREEN_WIDTH, 150), pygame.SRCALPHA)  # Allows transparency
                dialogue_box.fill((20, 20, 20, 200))  # Dark background with 200 alpha (transparency)
                screen.blit(dialogue_box, (0, SCREEN_HEIGHT - 150))

                # Border for the dialogue box
                pygame.draw.rect(screen, (255, 50, 50), (10, SCREEN_HEIGHT - 145, SCREEN_WIDTH - 20, 140), 3, border_radius=15)  

                # Display Character Image
                if speaker == "Player":
                    screen.blit(player_img, (10, SCREEN_HEIGHT - 130))  # Left side

                    # Display text slightly shifted for better readability
                    draw_text(text, 100, SCREEN_HEIGHT - 110,conversation_font , color=(255, 255, 255))
                
                else:
                    screen.blit(enemy_img, (SCREEN_WIDTH - 140, SCREEN_HEIGHT - 130))  # Right side

                    # Align text for enemy
                    draw_text(text, 30, SCREEN_HEIGHT - 110,conversation_font , color=(200, 200, 200))  

            else:
                Conversation_Ended = True
                for enemy in boss_group:
                    enemy.isActive = True
                current_line = 0
                if current_conversation != end_conversation:
                    player.isActive = True
                else:
                    game_end()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

       
        # Display FPS in the Screen
        fps = str(int(clock.get_fps()))
        fps_text = font.render(f"FPS: {fps}", True, WHITE)
        screen.blit(fps_text, (SCREEN_WIDTH // 2, 10))
        
        if player.has_key:
            screen.blit(key_image, (720, 20))
        
        if not player.alive:
            death_outro()
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
                isConversation_Started = False # Check if conversation has started
                isMidConversation_Started = False
                isLastConversation_Started = False
                
                Conversation_Ended = False
                current_line = 0
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
    show_Intro()
    main()