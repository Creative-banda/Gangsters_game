import pygame
from settings import PLAYER_ANIMATION, PLAYER_SIZE, BULLET_SIZE, BULLET_SPEED, SCREEN_THRUST_X, bullet_image, bullet_group



class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()

        self.frame_index = 0
        self.current_action = "Jump"
        self.animations = {}
        self.animation_cooldown = 100
        self.direction = 1  # 1: Right, -1: Left
        self.last_update_time = pygame.time.get_ticks()
        self.InAir = True
        self.vel_y = 0
        self.speed = 2
        self.isReloading = False
        self.last_bullet_time = pygame.time.get_ticks()
        self.isShooting = False

        # Load animations
        self.load_animations()

        # Set initial frame and position
        self.image = self.animations[self.current_action][self.frame_index]
        self.rect = self.image.get_rect()
        self.rect.midbottom = (0, 600)  # Changed from center to midbottom
        self.screen_height = 600  # Add your actual screen height
        self.target_y = self.screen_height - 100   # Position player near bottom

        
    def load_animations(self):
        """Load animations from the defined data."""
        for action, data in PLAYER_ANIMATION.items():
            frames = []
            sprite_sheet = pygame.image.load(data["image_path"]).convert_alpha()

            # Define adjustments for cutting padding
            cut_top = 50  # Pixels to remove from the top
            cut_left = 25 # Pixels to remove from the left
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

    def move(self, ground_group):
        dx = 0
        dy = 0
        screen_dx = 0
        screen_dy = 0
        keys = pygame.key.get_pressed()
        new_action = None

        # Handle Jumping
        if keys[pygame.K_w] and not self.InAir and not self.isReloading and not self.isShooting:
            self.InAir = True
            self.speed = 4
            self.vel_y = -14
            new_action = "Jump"

        # Allow horizontal movement even while in the air
        if (keys[pygame.K_a] or keys[pygame.K_d]) and (not self.isReloading and not self.isShooting):
            if keys[pygame.K_a]:
                dx = -self.speed
                self.direction = -1
            elif keys[pygame.K_d]:
                dx = self.speed
                self.direction = 1

            if not self.InAir and not self.isReloading and not self.isShooting:
                if keys[pygame.K_LSHIFT]:
                    dx *= 2
                    new_action = "Run"
                else:
                    new_action = "Walk"

        # Handle Shooting
        elif keys[pygame.K_SPACE] and not self.isReloading and not self.isShooting:
            new_action = "Shot"
            self.shoot()
        
        # Check dummy hurt animation
        elif keys[pygame.K_h]:
            new_action = "Hurt"

        # Idle animation if no other actions are active
        elif not self.InAir and not (keys[pygame.K_a] or keys[pygame.K_d] or keys[pygame.K_SPACE]) and not self.isReloading:
            if not self.current_action == "Hurt":
                new_action = "idle"

        # Update animation if needed
        if new_action:
            self.update_animation(new_action)

        # Apply gravity
        self.vel_y += 0.5
        dy = self.vel_y

        # Handle horizontal movement and collisions
        new_x = self.rect.x + dx
        player_rect_horizontal = self.rect.copy()
        player_rect_horizontal.x = new_x

        # Check horizontal collisions
        for ground in ground_group:
            if player_rect_horizontal.colliderect(ground.rect):
                if dx > 0:
                    dx = ground.rect.left - self.rect.right
                elif dx < 0:
                    dx = ground.rect.right - self.rect.left
                break

        self.rect.x += dx

        # Handle vertical movement and collisions
        new_y = self.rect.y + dy
        player_rect_vertical = self.rect.copy()
        player_rect_vertical.y = new_y

        # Check vertical collisions
        for ground in ground_group:
            if player_rect_vertical.colliderect(ground.rect):
                if dy > 0:  # Falling down
                    self.vel_y = 0
                    dy = ground.rect.top - self.rect.bottom
                    self.InAir = False
                elif dy < 0:  # Moving up
                    self.vel_y = 0
                    dy = 0
                break

        self.rect.y += dy

        # Horizontal scrolling
        if self.rect.right > SCREEN_THRUST_X:
            screen_dx = dx
            self.rect.x -= dx
        elif self.rect.left < SCREEN_THRUST_X and self.direction == -1:
            screen_dx = dx
            self.rect.x -= dx

        # Vertical scrolling (only when in air)
        if self.rect.bottom > self.target_y and self.vel_y > 0:
            screen_dy = self.rect.bottom - self.target_y
            self.rect.bottom = self.target_y
        elif self.vel_y < 0 and self.rect.bottom < self.target_y:
            screen_dy = dy
            self.rect.y -= dy

        return screen_dx, screen_dy

    def update(self):
        current_time = pygame.time.get_ticks()
        if current_time - self.last_update_time > PLAYER_ANIMATION[self.current_action]["animation_cooldown"]:
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

    def reload(self):
        if self.isReloading:
            return
        self.isReloading = True
        self.update_animation("Reload")

    def shoot(self):
        if pygame.time.get_ticks() - self.last_bullet_time < 250 or self.isReloading:
            return
        self.isShooting = True
        bullet = Bullet(self.rect.centerx + (PLAYER_SIZE[1]// 2 * self.direction), self.rect.centery, self.direction)
        bullet_group.add(bullet)
        self.last_bullet_time = pygame.time.get_ticks()

    def update_animation(self, new_action):
        if new_action != self.current_action:
            self.current_action = new_action
            self.frame_index = 0
            self.last_update_time = pygame.time.get_ticks()
            if new_action == "idle":
                self.isShooting = False

    def draw(self, screen):
        self.image = pygame.transform.scale(self.image, PLAYER_SIZE)
        screen.blit(self.image, self.rect)



class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, direction):
        super().__init__()
        self.image = bullet_image
        self.image = pygame.transform.scale(self.image, BULLET_SIZE)
        self.rect = self.image.get_rect()
        self.rect.midbottom = (x, y+5)
        self.direction = direction

    def update(self, ground_group, enemy_group, player):
        self.check_collision(ground_group, enemy_group, player)
        self.rect.x += BULLET_SPEED * self.direction
        if self.rect.left > 800 or self.rect.right < 0:
            self.kill()
    
    def check_collision(self, ground_group, enemy_group, player):
        if pygame.sprite.spritecollide(self, ground_group, False):
            self.kill()
        
        for enemy in enemy_group:
            if self.rect.colliderect(enemy.rect) and enemy.alive:
                self.kill()
                enemy.update_animation("Hurt")
                enemy.getting_hurt = True
                enemy.take_damage()
        if self.rect.colliderect(player.rect):
            self.kill()
            player.update_animation("Hurt")