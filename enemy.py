import pygame, random
from settings import PLAYER_SIZE, ENEMY_ANIMATION, CELL_SIZE
from player import Bullet, bullet_group



class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.animations = {}
        self.load_animations()
        self.current_action = "Walk"
        self.frame_index = 0
        self.last_update_time = pygame.time.get_ticks()
        self.image = self.animations[self.current_action][self.frame_index]
        self.rect = self.image.get_rect()
        self.x = x
        self.y = y
        self.rect.center = (self.x, self.y)
        self.direction = -1
        self.vel_y = 0
        self.isReloading = False
        self.isShoting = False
        self.idle_counter = 0
        self.move_counter = 0
        self.idling = False
        self.last_bullet_time = pygame.time.get_ticks()
        
        
        # Create a rect in front of the enemy as enemy vision
        self.vision_rect = pygame.Rect(self.x, self.y , 200, 50)
        self.vision_rect.center = self.rect.center
        
    def shoot(self):
        if pygame.time.get_ticks() - self.last_bullet_time < 500 or self.isReloading:
            return
        if self.frame_index == 5:
            self.isShooting = True
            bullet = Bullet(self.rect.centerx, self.rect.centery-10, self.direction)
            bullet_group.add(bullet)
            self.last_bullet_time = pygame.time.get_ticks()
    
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
            if self.current_action == "Shot" and self.frame_index >= len(self.animations[self.current_action]):
                self.update_animation("idle")
            elif self.current_action == "Hurt" and self.frame_index >= len(self.animations[self.current_action]):
                self.update_animation("idle")
                self.isShoting = False

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
        
        if self.direction == 1:
            dx = 1
        else:
            dx = -1


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
        
        if self.alive:
            if self.idling == False and random.randint(1, 200) == 1:
                self.update_animation("idle")
                self.idling = True
                self.idle_counter = 100
                self.dx = 0
            if self.vision_rect.colliderect(player.rect):
                self.direction = 1 if player.rect.x > self.rect.x else -1
                self.update_animation("Shot")
                self.shoot()
                self.isShoting = True
            else:
                self.isShoting = False
                if self.idling == False:
                    self.update_animation("Walk")
                    self.move_counter += 1

                    if self.move_counter > CELL_SIZE:
                        self.direction *= -1
                        self.move_counter *= -1
                else:
                    self.idle_counter -= 1
                    if self.idle_counter <= 0:
                        self.idling = False


        # Update enemy's position
        self.y += dy
        self.rect.y = self.y  
        if not self.isShoting and not self.isReloading and not self.idling:
            self.x += dx
        
        # Update vision rect
        self.vision_rect.midbottom = self.rect.center
    
    def update_animation(self, new_action):
        if new_action != self.current_action:
            self.current_action = new_action
            self.frame_index = 0
            self.last_update_time = pygame.time.get_ticks()
            
    def draw(self, screen, bg_scroll_x, bg_scroll_y):
        self.rect.x = self.x - bg_scroll_x
        self.rect.y = self.y - bg_scroll_y
        self.vision_rect.y = self.vision_rect.y- bg_scroll_y
        screen.blit(self.image, self.rect)
        
        # draw rect arround enemy
        
        pygame.draw.rect(screen,(0,255,0),self.rect,1)
        
        pygame.draw.rect(screen, (255, 0, 0), self.vision_rect,1)