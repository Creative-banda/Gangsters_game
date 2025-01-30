import pygame
from settings import PLAYER_SIZE, ENEMY_ANIMATION



class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.animations = {}
        self.load_animations()
        self.current_action = "idle"
        self.frame_index = 0
        self.last_update_time = pygame.time.get_ticks()
        self.image = self.animations[self.current_action][self.frame_index]
        self.rect = self.image.get_rect()
        self.x = x
        self.y = y
        self.rect.midbottom = (self.x, self.y)
        self.direction = -1
        self.vel_y = 0
        
        # Create a rect in front of the enemy as enemy vision
        self.vision_rect = pygame.Rect(self.x, self.y , 100, 10)
        self.vision_rect.center = self.x, self.y
        
        

    def load_animations(self):
        """Load animations from the defined data."""
        for action, data in ENEMY_ANIMATION.items():
            frames = []
            sprite_sheet = pygame.image.load(data["image_path"]).convert_alpha()

            # Define adjustments for cutting padding
            cut_top = 50  # Pixels to remove from the top
            cut_left = 33 # Pixels to remove from the left
            cut_right = 33  # Pixels to remove from the right
            frame_height = 128 - cut_top  # Adjusted height
            frame_width = 128 - (cut_left + cut_right)  # Adjusted width

            # Extract frames based on offsets and dimensions
            for frame_index in range(data["frame_count"]):
                x = (frame_index * 128) + cut_left  # Adjust for left padding
                y = cut_top  # Start Y after cutting the top
                frame = sprite_sheet.subsurface(
                    (x, y, frame_width, frame_height)  # Adjust width and height
                )
                frame = pygame.transform.scale(frame, PLAYER_SIZE)
                frames.append(frame)

            self.animations[action] = frames
            
    def update(self):
        current_time = pygame.time.get_ticks()
        if current_time - self.last_update_time > ENEMY_ANIMATION[self.current_action]["animation_cooldown"]:
            self.last_update_time = current_time
            self.frame_index += 1

            # Reset Jump animation when it ends
            if self.current_action == "Jump" and self.frame_index >= len(self.animations[self.current_action]):
                self.InAir = True
            elif self.current_action == "Reload" and self.frame_index >= len(self.animations[self.current_action]):
                self.isReloading = False
            elif self.current_action == "Shot" and self.frame_index >= len(self.animations[self.current_action]):
                self.isShooting = False
            elif self.current_action == "Hurt" and self.frame_index >= len(self.animations[self.current_action]):
                self.update_animation("idle")

            # Loop animation
            if self.frame_index >= len(self.animations[self.current_action]):
                self.frame_index = 0

        self.image = self.animations[self.current_action][self.frame_index]
        self.image = pygame.transform.flip(self.image, self.direction == -1, False)
        
    def move(self, player, ground_group):
        dy = 0
        # Apply gravity
        self.vel_y += 0.5
        dy += self.vel_y

        # Check collision with ground
        for ground in ground_group:
            if self.rect.colliderect(ground.rect):
                if dy > 0:
                    self.rect.bottom = ground.rect.top
                    self.vel_y = 0
                    dy = 0
                elif dy < 0:
                    self.rect.top = ground.rect.bottom
                    self.vel_y = 0
                    dy = 0

        # Check Player Come in Vision
        
        if self.vision_rect.colliderect(player.rect):
            self.direction = 1 if player.rect.x > self.rect.x else -1
            self.update_animation("Shot")


        # Update enemy's position
        self.y += dy
        self.rect.y = self.y  
        
        # Update vision rect
        
        self.vision_rect.x = self.x - PLAYER_SIZE[0]
        self.vision_rect.y = self.y + PLAYER_SIZE[0] // 2 
    
    def update_animation(self, new_action):
        if new_action != self.current_action:
            self.current_action = new_action
            self.frame_index = 0
            self.last_update_time = pygame.time.get_ticks()
            
    def draw(self, screen, bg_scroll_x, bg_scroll_y):
        self.rect.x = self.x - bg_scroll_x
        self.rect.y = self.y - bg_scroll_y
        self.vision_rect.x = self.vision_rect.x - bg_scroll_x
        self.vision_rect.y = self.vision_rect .y- bg_scroll_y
        screen.blit(self.image, self.rect)
        
        pygame.draw.rect(screen, (255, 0, 0), self.vision_rect)