import pygame, random, copy
from settings import *


jump_sounds = ["jump","jump_2"]

reload_channel = pygame.mixer.Channel(2) 

class Player(pygame.sprite.Sprite):

    def __init__(self):
        super().__init__()
        self.frame_index = 0
        self.zoom_value = ZOOM_VALUE
        self.current_action = "Jump"
        self.animations = {}
        self.direction = 1  # 1: Right, -1: Left
        self.last_update_time = pygame.time.get_ticks()
        self.InAir = True
        self.vel_y = 0
        self.speed = 2 * self.zoom_value
        self.isReloading = False
        self.last_bullet_time = pygame.time.get_ticks()
        self.isShooting = False
        self.health = 100
        self.alive = True
        self.current_gun = "rifle"
        self.isRifle = True
        self.isLaser = False
        self.isSmg = False
        self.sprint_value = 200
        self.last_sprint_update = pygame.time.get_ticks()
    
        self.bullet_info = copy.deepcopy(BULLET_INFO) # Copy the dictionary to avoid modifying the original dictionary

        # Load animations
        self.load_animations()

        # Set initial frame and position
        try:
            self.image = self.animations[self.current_action][self.frame_index]
        except:
            self.image = self.animations[self.current_action][len(self.animations[self.current_action])-1]

        self.rect = self.image.get_rect()
        self.rect.midbottom = (0, 600)  # Changed from center to midbottom
        self.screen_height = 600  
        self.target_y = self.screen_height - 100   # Position player near bottom
        
        # Create a health bar in the top of the player as health bar
        self.max_health = 200
        self.health_bar_length = 100
        self.health_ratio = self.max_health / self.health_bar_length
        # creating a rect for health bar
        self.health_bar = pygame.Rect(40, 10, self.health_bar_length, 20)
        self.has_key = False
    
    def load_animations(self):
        """Load animations from the defined data."""
        for action, data in PLAYER_ANIMATION.items():
            frames = []
            sprite_sheet = pygame.image.load(data["image_path"]).convert_alpha()

            # Define adjustments for cutting padding
            cut_top = 40  # Pixels to remove from the top
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
                frame = pygame.transform.scale(frame, tuple(int(dim * self.zoom_value) for dim in PLAYER_SIZE))
                frames.append(frame)

            self.animations[action] = frames


    def move(self, ground_group):
        if not self.alive:
            self.update_animation("Dead")
        dx = 0
        dy = 0
        screen_dx = 0
        screen_dy = 0


        keys = pygame.key.get_pressed()
        new_action = None
        
        if not reload_channel.get_busy():
            self.isReloading = False
        
    
        if self.InAir:
            self.speed = 4
        else:
            self.speed = 2

        # Handle Jumping
        if keys[pygame.K_w] and not self.InAir and not self.isReloading and not self.isShooting and self.alive:
            self.InAir = True
            self.vel_y = -14 * self.zoom_value
            new_action = "Jump"


            # play a random jump sound
            sound = random.choice(jump_sounds)
            if sound == "jump":
                jump = pygame.mixer.Sound(f"assets/sfx/{sound}.mp3")
                # reduce the volume of the jump sound
                jump.set_volume(0.5)
                jump.play()
            else:
                pygame.mixer.Sound(f"assets/sfx/{sound}.mp3").play()


        # Allow horizontal movement even while in the air
        if (keys[pygame.K_a] or keys[pygame.K_d]) and (not self.isReloading) and self.alive:
            if keys[pygame.K_a]:
                dx = -self.speed
                self.direction = -1
            elif keys[pygame.K_d]:
                dx = self.speed
                self.direction = 1

            if not self.InAir and not self.isReloading and not self.isShooting and self.alive:
                if keys[pygame.K_LSHIFT] and self.sprint_value > 0:
                    self.sprint_value -= 1
                    dx *= 3 
                    new_action = "Run"
                else:
                    new_action = "Walk"
            

        # Handle Shooting
        elif keys[pygame.K_SPACE] and not self.isReloading and not self.isShooting and self.alive:
            if self.bullet_info[self.current_gun]["remaining"] != 0:
                new_action = "Shot"
                self.shoot()
            else:
                new_action = "idle"
                if pygame.time.get_ticks() - self.last_bullet_time > 700:
                    empty_mag_sound.play()
                    self.last_bullet_time = pygame.time.get_ticks()


        # Idle animation if no other actions are active
        elif not self.InAir and not (keys[pygame.K_a] or keys[pygame.K_d] or keys[pygame.K_SPACE]) and not self.isReloading:
            if not self.current_action == "Hurt":
                new_action = "idle"

        if not keys[pygame.K_LSHIFT]:
            if pygame.time.get_ticks() - self.last_sprint_update > 500:
                    self.sprint_value = min(200, self.sprint_value + 5)
                    self.last_sprint_update = pygame.time.get_ticks()

        # Update animation
        if new_action and self.alive:
            self.update_animation(new_action)

        # Apply gravity
        self.vel_y += 0.5 * self.zoom_value
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
                    self.speed = 2
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
            elif self.current_action == "Dead" and self.frame_index >= len(self.animations[self.current_action]):
                self.frame_index = len(self.animations[self.current_action])
            
            if self.alive:
                # Loop animation
                if self.frame_index >= len(self.animations[self.current_action]):
                    self.frame_index = 0
        try:
            self.image = self.animations[self.current_action][self.frame_index]
        except:
            self.image = self.animations[self.current_action][len(self.animations[self.current_action])-1]
        self.image = pygame.transform.flip(self.image, self.direction == -1, False)


    def reload(self):
        if self.isReloading or self.bullet_info[self.current_gun]["remaining"] == self.bullet_info[self.current_gun]["mag_size"] or self.bullet_info[self.current_gun]["total"] == 0:
            return
        self.isReloading = True
        self.update_animation("Reload")
        reload_channel.play(reload_sound)

        
        # decreasing the total bullets by the remaining bullets
        bullet_got_shooted = self.bullet_info[self.current_gun]["mag_size"] - self.bullet_info[self.current_gun]["remaining"]
        if self.bullet_info[self.current_gun]["total"] < bullet_got_shooted:
            self.bullet_info[self.current_gun]["remaining"] = self.bullet_info[self.current_gun]["total"]
            self.bullet_info[self.current_gun]["total"] = 0
        else:
            self.bullet_info[self.current_gun]["total"] -= (self.bullet_info[self.current_gun]["mag_size"] - self.bullet_info[self.current_gun]["remaining"])
            self.bullet_info[self.current_gun]["remaining"] = self.bullet_info[self.current_gun]["mag_size"]


    def shoot(self):
        if pygame.time.get_ticks() - self.last_bullet_time < BULLET_INFO[self.current_gun]['cooldown'] or self.isReloading:
            return

        self.isShooting = True

        if self.current_gun == "rifle":
            bullet = Bullet(self.rect.centerx + (PLAYER_SIZE[1] // 2 * self.direction), self.rect.centery, self.direction, 40, self.zoom_value)
            bullet_group.add(bullet)
            bullet_sound.play()


        elif self.current_gun == "laser":
            for i in range(7):  # Fire 7 bullets in a row
                offset = i * 15 * self.direction  # Space bullets apart
                bullet = Bullet(self.rect.centerx + (PLAYER_SIZE[1] // 2 * self.direction) + offset, 
                                self.rect.centery, 
                                self.direction, 30, self.zoom_value)
                bullet_group.add(bullet)
                laser_sound.play()
        elif self.current_gun == "smg":
            bullet = Bullet(self.rect.centerx + (PLAYER_SIZE[1] // 2 * self.direction), self.rect.centery, self.direction, 10, self.zoom_value)
            bullet_group.add(bullet)
            smg_sound.play()

        self.last_bullet_time = pygame.time.get_ticks()
        self.bullet_info[self.current_gun]["remaining"] -= 1


    def update_animation(self, new_action):
        if new_action != self.current_action:
            self.current_action = new_action
            self.frame_index = 0
            self.last_update_time = pygame.time.get_ticks()
            if new_action == "idle":
                self.isShooting = False


    def draw(self, screen):
        screen.blit(self.image, self.rect)
        

        # display the collision bar
        # pygame.draw.rect(screen, (255, 0, 0), self.rect, 2)


    def update_size(self, ZOOM_VALUE):
        self.zoom_value = ZOOM_VALUE
        self.load_animations()
        self.speed = 2 * self.zoom_value
        self.image = self.animations[self.current_action][self.frame_index]
        self.rect = self.image.get_rect()
       
        
class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, direction, damage, ZOOM_VALUE):
        super().__init__()
        self.image = bullet_image
        self.zoom_value = ZOOM_VALUE
        self.image = pygame.transform.scale(self.image, tuple(int(dim * self.zoom_value) for dim in BULLET_SIZE))
        self.rect = self.image.get_rect()
        self.x = x
        self.y = y
        self.rect.midbottom = (self.x, self.y+5)
        self.direction = direction
        self.damage = damage

    def update(self, bg_scroll_x, bg_scroll_y):
        self.rect.x += BULLET_SPEED * self.direction 
        self.rect.y -= bg_scroll_y
        self.rect.x -= bg_scroll_x
    
    def check_collision(self, ground_group, enemy_group, player, bg_scroll_x, bg_scroll_y):
        if pygame.sprite.spritecollide(self, ground_group, False):
            self.kill()
        
        for enemy in enemy_group:
            diff_x = abs(enemy.x - bg_scroll_x - player.rect.x)
            diff_y = abs(enemy.y - bg_scroll_y - player.rect.y)
            if diff_x < 800 and diff_y < 600:
                if self.rect.colliderect(enemy.rect) and enemy.health > 0:
                    self.kill()
                    enemy.take_damage(self.damage)
                
        if self.rect.colliderect(player.rect):
            self.kill()
            player.health -= self.damage
            if player.health <= 0:
                player.alive = False
            else:
                player.update_animation("Hurt")
        
    def draw(self, screen):
        screen.blit(self.image, self.rect)
    
