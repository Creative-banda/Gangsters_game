
import pygame
from settings import *


bullet_group = pygame.sprite.Group()

class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()

        self.frame_index = 0
        self.current_action = "idle"
        self.animations = {}
        self.animation_cooldown = 100
        self.direction = 1  # 1: Right, -1: Left
        self.last_update_time = pygame.time.get_ticks()
        self.InAir = True
        self.vel_y = 0
        self.speed = 3
        self.running_speed = 7
        self.isReloading = False
        self.last_bullet_time = pygame.time.get_ticks()
        self.isShooting = False

        # Define animations with frame counts, offsets, and sprite sheet paths
        self.animation_data = {
            "idle": {
                "frame_count": 6,  # Number of frames
                "image_path": "assets/player/Idle.png",  # Sprite sheet path,
                "animataion_cooldown": 100
            },
            "Run": {
                "frame_count": 10,  # Number of frames
                "image_path": "assets/player/Run.png",  # Sprite sheet path
                "animataion_cooldown": 100
            },
            "Shot": {
                "frame_count": 4,  # Number of frames
                "image_path": "assets/player/Shot.png",  # Sprite sheet path
                "animataion_cooldown": 50
            },
            "Walk": {
                "frame_count": 10,  # Number of frames
                "image_path": "assets/player/Walk.png",  # Sprite sheet path
                "animataion_cooldown": 100
            },
            "Jump": {
                "frame_count": 10,  # Number of frames
                "image_path": "assets/player/Jump.png",  # Sprite sheet path
                "animataion_cooldown": 100
            },
            
            "Reload": {
                "frame_count": 17,  # Number of frames
                "image_path": "assets/player/Recharge.png",  # Sprite sheet path
                "animataion_cooldown": 70
            },
        }

        # Load animations
        self.load_animations()

        # Set initial frame and position
        self.image = self.animations[self.current_action][self.frame_index]
        self.rect = self.image.get_rect()
        self.rect.midbottom = (200, 300)  # Changed from center to midbottom

    def load_animations(self):
        """Load animations from the defined data."""
        for action, data in self.animation_data.items():
            frames = []
            sprite_sheet = pygame.image.load(data["image_path"]).convert_alpha()

            # Define adjustments for cutting padding
            cut_top = 50  # Pixels to remove from the top
            cut_left = 35  # Pixels to remove from the left
            cut_right = 35  # Pixels to remove from the right
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

    def move(self, ground_group):
        dx = 0
        dy = 0
        keys = pygame.key.get_pressed()

        # Reset action to determine new animation
        new_action = None

        # Handle Jumping
        if keys[pygame.K_w] and not self.InAir and not self.isReloading:
            self.InAir = True
            self.vel_y = -11  # Jump velocity
            new_action = "Jump"

        # Allow horizontal movement even while in the air
        if keys[pygame.K_a] or keys[pygame.K_d] and not self.isReloading:
            if keys[pygame.K_a]:
                dx = -self.speed  # Move left
                self.direction = -1
            elif keys[pygame.K_d]:
                dx = self.speed  # Move right
                self.direction = 1

            # Set "Walk" or "Run" animations only if on the ground
            if not self.InAir and not self.isReloading:
                if keys[pygame.K_LSHIFT]:
                    dx *= 2  # Running speed
                    new_action = "Run"
                else:
                    new_action = "Walk"

        # Handle Shooting
        if keys[pygame.K_SPACE] and not self.isReloading:
            new_action = "Shot"
            self.shoot()

        # Idle animation if no other actions are active
        if not self.InAir and not (keys[pygame.K_a] or keys[pygame.K_d] or keys[pygame.K_SPACE] ) and not self.isReloading:
            new_action = "idle"

        # Update animation if needed
        if new_action :
            self.update_animation(new_action)

        # Apply gravity
     
        self.vel_y += 0.5  # Simulate gravity
        dy += self.vel_y

        # Calculate new position
        new_x = self.rect.x + dx
        new_y = self.rect.y + dy

        # Create a temporary rect for collision detection
        player_rect = pygame.Rect(new_x + dx, new_y + dy, self.rect.width, self.rect.height)

        # Check for collisions with ground group

        for ground in ground_group:
            if player_rect.colliderect(ground.rect):
                # Calculate the overlap on each side
                overlap_left = player_rect.right - ground.rect.left
                overlap_right = ground.rect.right - player_rect.left
                overlap_top = player_rect.bottom - ground.rect.top
                overlap_bottom = ground.rect.bottom - player_rect.top

                # Find the smallest overlap to determine the side of collision
                min_overlap = min(overlap_left, overlap_right, overlap_top, overlap_bottom)

                if min_overlap == overlap_top:
                    # Collision from the top (landing)
                    self.vel_y = 0
                    self.InAir = False
                    dy = ground.rect.top - self.rect.bottom
                elif min_overlap == overlap_bottom:
                    # Collision from the bottom (hit the ceiling)
                    self.vel_y = 0
                    dy = ground.rect.bottom - self.rect.top
                elif min_overlap == overlap_left:
                    # Collision from the left
                    dx = ground.rect.left - self.rect.right
                elif min_overlap == overlap_right:
                    # Collision from the right
                    dx = ground.rect.right - self.rect.left


       

        # Restrict player within horizontal boundaries
        if self.rect.right > 800:
            self.rect.right = 800
        if self.rect.left < 0:
            self.rect.left = 0
        # Update the player's position
        self.rect.x += dx
        self.rect.y += dy
        # check for if player pass the screen threshhold and move the screen
        if self.rect.right > SCREEN_THRUST:
            self.rect.x -= dx
            # return the added value from this method
            return dx
        elif self.rect.left < SCREEN_THRUST and self.direction == -1 :
            self.rect.x -= dx
            # return the added value from this method
            return dx
        return 0



    def update(self):
        current_time = pygame.time.get_ticks()
        if current_time - self.last_update_time > self.animation_data[self.current_action]["animataion_cooldown"]:
            self.last_update_time = current_time
            self.frame_index += 1

            # Reset Jump animation when it ends
            if self.current_action == "Jump" and self.frame_index >= len(self.animations[self.current_action]):
                self.InAir = True
                self.update_animation("idle")
            elif self.current_action == "Reload" and self.frame_index >= len(self.animations[self.current_action]):
                self.isReloading = False
                self.update_animation("idle")

            # Loop animation
            if self.frame_index >= len(self.animations[self.current_action]):
                self.frame_index = 0

        self.image = self.animations[self.current_action][self.frame_index]
        self.image = pygame.transform.flip(self.image, self.direction == -1, False)

    def reload(self):
        if self.isReloading:
            return
        self.isReloading = True
        self.update_animation("Reload")

    def shoot(self):
        if pygame.time.get_ticks() - self.last_bullet_time < 250 or self.isReloading:
            return
        self.isShooting = True
        bullet = Bullet(self.rect.centerx, self.rect.centery, self.direction)
        bullet_group.add(bullet)
        self.last_bullet_time = pygame.time.get_ticks()

    def update_animation(self, new_action):
        if new_action != self.current_action:
            self.current_action = new_action
            self.frame_index = 0
            self.last_update_time = pygame.time.get_ticks()

    def draw(self, screen):
        self.image = pygame.transform.scale(self.image, PLAYER_SIZE)

        # For testing draw a rectangle with different color than the sprite
        # pygame.draw.rect(screen, (255, 0, 0), self.rect, 2)

        screen.blit(self.image, self.rect)


class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, direction):
        super().__init__()
        self.image = bullet_image
        self.image = pygame.transform.scale(self.image, BULLET_SIZE)
        self.rect = self.image.get_rect()
        self.rect.midbottom = (x, y+5)
        self.direction = direction

    def update(self, ground_group):
        self.check_collision(ground_group)
        self.rect.x += BULLET_SPEED * self.direction
        if self.rect.left > 800 or self.rect.right < 0:
            self.kill()
    
    def check_collision(self, ground_group):
        if pygame.sprite.spritecollide(self, ground_group, False):
            self.kill()